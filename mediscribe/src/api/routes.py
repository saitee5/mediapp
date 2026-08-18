import io
import uuid
import datetime
import asyncio
import json
from typing import Optional, Dict
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File,
)
from fastapi.responses import StreamingResponse
import websockets

from src.api.schemas import (
    ExtractSOAPRequest,
    ExtractSOAPResponse,
    GenerateDocumentsRequest,
    GenerateDocumentsResponse,
    GeneratePDFRequest,
    GeneratePDFResponse,
    GeneratedPDFItem,
    ConsultationDetailResponse,
    HealthCheckResponse,
    ClinicalSOAPExtraction,
    PatientVisitSummary,
    CaseSheetSummary,
    DischargeInstructions,
    ReferralLetter,
)
from src.agent import agent
from src.services import supabase_service
from src.services.transcription_service import transcription_service
from src.services.deepgram_service import deepgram_service
from src.drug_alerts import (
    drug_alert_service,
    DrugAlertCheckRequest,
    DrugAlertCheckResponse,
)
from src.utils.pdf_generator import (
    generate_case_sheet_pdf,
    generate_patient_summary_pdf,
    generate_discharge_instructions_pdf,
    generate_referral_letter_pdf,
)
from src.utils.config import settings
from src.utils.logger import logger

router = APIRouter()

@router.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint providing status of LLM, Deepgram / Groq STT, and Supabase."""
    return HealthCheckResponse(
        status="online",
        llm_configured=True,
        model=settings.DEFAULT_LLM_MODEL,
        supabase_configured=supabase_service.is_configured(),
        agent_ready=True,
    )


# ==============================================================================
# Real-Time Speech-to-Text (STT) Powered by Deepgram Nova-2 Medical (with Groq Fallback)
# ==============================================================================

@router.websocket("/api/ws/transcribe")
async def websocket_realtime_transcribe(websocket: WebSocket):
    """
    Real-time continuous full-duplex WebSocket endpoint for clinical speech-to-text.
    - If DEEPGRAM_API_KEY is configured: Streams directly via Deepgram Nova-2 Medical (zero cutoffs, live word-by-word interim results).
    - Fallback: Uses Groq Whisper STT pipeline.
    """
    await websocket.accept()
    logger.info("Client connected to real-time STT WebSocket (/api/ws/transcribe).")

    # Mode 1: Deepgram Live Stream Proxy (True Full-Duplex Continuous Audio Streaming)
    if deepgram_service.is_configured():
        deepgram_ws_url = deepgram_service.get_live_ws_url()
        headers = {"Authorization": f"Token {deepgram_service.api_key}"}

        try:
            async with websockets.connect(deepgram_ws_url, additional_headers=headers) as dg_ws:
                logger.info("Connected upstream to Deepgram Nova-2 Medical streaming engine.")

                # Task A: Forward incoming client audio to Deepgram
                async def client_to_deepgram():
                    try:
                        while True:
                            message = await websocket.receive()
                            if message.get("type") == "websocket.disconnect":
                                break
                            if "bytes" in message and message["bytes"]:
                                await dg_ws.send(message["bytes"])
                            elif "text" in message and message["text"]:
                                text_msg = message["text"]
                                if text_msg in ("ping", "KeepAlive") or "KeepAlive" in text_msg:
                                    await dg_ws.send(json.dumps({"type": "KeepAlive"}))
                                    await websocket.send_json({"type": "pong"})
                                elif text_msg == "close":
                                    break
                    except WebSocketDisconnect:
                        pass
                    except Exception as e:
                        if "disconnect" not in str(e).lower():
                            logger.warning(f"Client to Deepgram stream note: {e}")

                # Task B: Periodic KeepAlive Heartbeat (prevent Deepgram Net0001 timeout on silence)
                async def deepgram_heartbeat():
                    try:
                        while True:
                            await asyncio.sleep(5)
                            await dg_ws.send(json.dumps({"type": "KeepAlive"}))
                    except Exception:
                        pass

                # Task C: Receive transcripts from Deepgram and forward to client
                async def deepgram_to_client():
                    try:
                        async for dg_msg in dg_ws:
                            data = json.loads(dg_msg)
                            channel = data.get("channel", {})
                            alternatives = channel.get("alternatives", [])
                            if alternatives:
                                transcript = alternatives[0].get("transcript", "").strip()
                                is_final = data.get("is_final", False)
                                speech_final = data.get("speech_final", False)
                                now_str = datetime.datetime.now().strftime("%H:%M:%S")

                                if transcript:
                                    await websocket.send_json({
                                        "type": "transcript",
                                        "text": transcript,
                                        "is_final": is_final,
                                        "speech_final": speech_final,
                                        "engine": "deepgram-nova-2-medical",
                                        "timestamp": now_str,
                                    })
                    except Exception as e:
                        if "disconnect" not in str(e).lower():
                            logger.warning(f"Deepgram to client stream note: {e}")

                await asyncio.gather(
                    client_to_deepgram(),
                    deepgram_heartbeat(),
                    deepgram_to_client(),
                    return_exceptions=True
                )

        except Exception as dg_err:
            logger.warning(f"Deepgram streaming unavailable ({dg_err}). Using Groq Whisper pipeline...")

    # Mode 2: Groq Whisper Audio Chunk Pipeline
    transcript_history = []
    try:
        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                break

            if "bytes" in message and message["bytes"]:
                audio_bytes = message["bytes"]
                try:
                    recent_context = " ".join(transcript_history[-3:])[-200:] if transcript_history else "Medical consultation between doctor and patient."
                    text, latency_ms = await transcription_service.transcribe_audio_bytes(
                        audio_bytes=audio_bytes,
                        filename="chunk.webm",
                        mime_type="audio/webm",
                        prompt=recent_context,
                    )
                    now_str = datetime.datetime.now().strftime("%H:%M:%S")

                    if text:
                        transcript_history.append(text)
                        await websocket.send_json({
                            "type": "transcript",
                            "text": text,
                            "is_final": True,
                            "speech_final": True,
                            "latency_ms": latency_ms,
                            "engine": "groq-whisper",
                            "timestamp": now_str,
                        })
                    else:
                        await websocket.send_json({
                            "type": "ping",
                            "latency_ms": latency_ms,
                            "timestamp": now_str,
                        })
                except Exception as err:
                    logger.warning(f"Audio chunk transcription error: {err}")
                    await websocket.send_json({"type": "error", "message": str(err)})

            elif "text" in message and message["text"]:
                if message["text"] == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message["text"] == "clear":
                    transcript_history.clear()
                elif message["text"] == "close":
                    break

    except WebSocketDisconnect:
        logger.info("Client disconnected from STT WebSocket (/api/ws/transcribe).")
    except Exception as e:
        if "disconnect" not in str(e).lower():
            logger.error(f"Unexpected WebSocket session exception: {e}")


@router.post("/api/transcribe-audio")
async def transcribe_audio_file(
    file: UploadFile = File(...),
    language: str = Query("en", description="Audio language"),
):
    """
    HTTP endpoint to transcribe an uploaded audio file using Deepgram Nova-2 (or Groq Whisper).
    """
    try:
        content = await file.read()
        mime_type = file.content_type or "audio/webm"

        text, latency_ms = await deepgram_service.transcribe_audio_bytes(
            audio_bytes=content,
            mime_type=mime_type,
            language=language,
        )

        return {
            "status": "success",
            "text": text,
            "latency_ms": latency_ms,
            "filename": file.filename or "audio.webm",
        }
    except Exception as e:
        logger.error(f"Error in transcribe-audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# Step 1 Endpoint: Extract SOAP Note from Transcript for Doctor Review
# ==============================================================================
@router.post("/api/extract-soap", response_model=ExtractSOAPResponse)
@router.post("/api/generate-summary", response_model=ExtractSOAPResponse)
async def extract_soap_for_review(request: ExtractSOAPRequest):
    """
    Step 1:
    - Receives conversation transcript
    - Runs Agent 1 (SOAP extraction)
    - Saves initial consultation in Supabase with status 'pending_review'
    - Returns structured SOAP note to frontend for physician review and editing
    """
    try:
        session_id = request.session_id or f"consultation_{uuid.uuid4().hex[:12]}"
        logger.info(f"API [Step 1]: Extracting structured SOAP for session {session_id}...")

        # Run extraction pipeline
        soap_data = await agent.extract_soap(request.transcript)

        # Save initial record in Supabase / memory store
        await supabase_service.save_soap_consultation(
            session_id=session_id,
            transcript=request.transcript,
            soap=soap_data,
            patient_id=request.patient_id,
            status="pending_review",
        )

        return ExtractSOAPResponse(
            session_id=session_id,
            status="pending_review",
            soap=soap_data,
            message="Clinical SOAP extracted successfully. Ready for physician review.",
        )
    except Exception as e:
        logger.error(f"Error in extract-soap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# Step 2 Endpoint: Generate Multi-Document Bundle from Verified SOAP
# ==============================================================================
@router.post("/api/generate-documents", response_model=GenerateDocumentsResponse)
async def generate_documents_from_verified_soap(request: GenerateDocumentsRequest):
    """
    Step 2:
    - Receives physician-verified / edited SOAP note + optional generate_case_sheet flag from frontend
    - Document routing logic:
        * Patient Visit Summary: FIXED (Always generated)
        * Case Sheet Summary: FRONTEND DECIDED (generate_case_sheet flag)
        * Discharge Instructions: AUTONOMOUSLY DECIDED BY AI from the clinical SOAP
        * Referral Letter: AUTONOMOUSLY DECIDED BY AI from the clinical SOAP
    - Executes downstream LangGraph with autonomous triage routing
    - Saves all generated documents in Supabase with status 'completed'
    - Returns the multi-document bundle to frontend
    """
    try:
        session_id = request.session_id
        logger.info(
            f"API [Step 2]: Generating documents for session {session_id} "
            f"(generate_case_sheet={request.generate_case_sheet}, AI evaluating Discharge & Referral needs)..."
        )

        # Run downstream multi-document pipeline
        pipeline_output = await agent.generate_documents(
            soap=request.verified_soap,
            generate_case_sheet=request.generate_case_sheet,
        )

        patient_summary = pipeline_output.get("patient_visit_summary")
        case_sheet = pipeline_output.get("case_sheet_summary")
        discharge = pipeline_output.get("discharge_instructions")
        referral = pipeline_output.get("referral_letter")

        if not patient_summary:
            raise RuntimeError("Downstream pipeline failed to generate required Patient Visit Summary.")

        # Persist final documents in database
        await supabase_service.save_generated_documents(
            session_id=session_id,
            soap=request.verified_soap,
            patient_visit_summary=patient_summary,
            case_sheet_summary=case_sheet,
            discharge_instructions=discharge,
            referral_letter=referral,
            status="completed",
        )

        return GenerateDocumentsResponse(
            session_id=session_id,
            status="completed",
            patient_visit_summary=patient_summary,
            case_sheet_summary=case_sheet,
            discharge_instructions=discharge,
            referral_letter=referral,
            message="Clinical documents generated successfully from verified SOAP.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating documents for {request.session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# Step 3 Endpoint: Generate & Store Final PDFs Organized by Patient Separately
# ==============================================================================
@router.post("/api/generate-pdf", response_model=GeneratePDFResponse)
async def generate_consultation_pdfs(request: GeneratePDFRequest, req: Request = None):
    """
    Step 3:
    - Fetches the stored consultation records and generated documents for the session
    - Formats and generates official hospital PDFs for each document
    - Stores each PDF in Supabase Storage partitioned by patient separately:
        Path format: {patient_identifier}/{session_id}/{doc_type}.pdf
    - Returns all public Supabase URLs and direct download endpoints
    """
    try:
        session_id = request.session_id
        doc_type_filter = (request.document_type or "all").lower()
        logger.info(f"API [Step 3]: Generating PDFs for session {session_id} (filter='{doc_type_filter}')...")

        record = await supabase_service.get_consultation(session_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Consultation session '{session_id}' not found.")

        # Extract patient identifier
        patient_name = record.get("patient_name") or "patient"
        patient_id = record.get("patient_id")
        if not patient_id:
            safe_name = "".join(c for c in patient_name.lower() if c.isalnum() or c in ("-", "_")).strip()
            patient_id = f"patient_{safe_name}" if safe_name else "patient_general"

        base_url = str(req.base_url).rstrip("/") if req else ""
        generated_items = []
        pdf_urls: Dict[str, str] = {}
        download_urls: Dict[str, str] = {}

        # 1. Case Sheet Summary PDF
        if doc_type_filter in ("all", "case_sheet", "case_sheet_summary") and record.get("case_sheet_summary"):
            case_sheet = CaseSheetSummary.model_validate(record["case_sheet_summary"])
            pdf_bytes = generate_case_sheet_pdf(case_sheet)
            filename = f"case_sheet_{session_id[:8]}.pdf"
            public_url = await supabase_service.upload_patient_pdf(
                patient_identifier=patient_id,
                session_id=session_id,
                document_type="case_sheet_summary",
                pdf_bytes=pdf_bytes,
                filename=filename,
            )
            dl_url = f"{base_url}/api/consultation/{session_id}/download-pdf/case_sheet_summary"
            pdf_urls["case_sheet_summary"] = public_url
            download_urls["case_sheet_summary"] = dl_url
            generated_items.append(GeneratedPDFItem(
                document_type="case_sheet_summary",
                title="Clinical Case Sheet Summary",
                filename=filename,
                pdf_url=public_url,
                download_url=dl_url,
            ))

        # 2. Patient Visit Summary PDF
        if doc_type_filter in ("all", "patient_summary", "patient_visit_summary") and record.get("patient_visit_summary"):
            patient_summary = PatientVisitSummary.model_validate(record["patient_visit_summary"])
            pdf_bytes = generate_patient_summary_pdf(patient_summary)
            filename = f"patient_visit_summary_{session_id[:8]}.pdf"
            public_url = await supabase_service.upload_patient_pdf(
                patient_identifier=patient_id,
                session_id=session_id,
                document_type="patient_visit_summary",
                pdf_bytes=pdf_bytes,
                filename=filename,
            )
            dl_url = f"{base_url}/api/consultation/{session_id}/download-pdf/patient_visit_summary"
            pdf_urls["patient_visit_summary"] = public_url
            download_urls["patient_visit_summary"] = dl_url
            generated_items.append(GeneratedPDFItem(
                document_type="patient_visit_summary",
                title="Patient Visit Summary (After-Visit Care Report)",
                filename=filename,
                pdf_url=public_url,
                download_url=dl_url,
            ))

        # 3. Discharge Instructions PDF
        if doc_type_filter in ("all", "discharge", "discharge_instructions") and record.get("discharge_instructions"):
            discharge = DischargeInstructions.model_validate(record["discharge_instructions"])
            pdf_bytes = generate_discharge_instructions_pdf(discharge)
            filename = f"discharge_instructions_{session_id[:8]}.pdf"
            public_url = await supabase_service.upload_patient_pdf(
                patient_identifier=patient_id,
                session_id=session_id,
                document_type="discharge_instructions",
                pdf_bytes=pdf_bytes,
                filename=filename,
            )
            dl_url = f"{base_url}/api/consultation/{session_id}/download-pdf/discharge_instructions"
            pdf_urls["discharge_instructions"] = public_url
            download_urls["discharge_instructions"] = dl_url
            generated_items.append(GeneratedPDFItem(
                document_type="discharge_instructions",
                title="Patient Discharge Instructions & Care Plan",
                filename=filename,
                pdf_url=public_url,
                download_url=dl_url,
            ))

        # 4. Specialist Referral Letter PDF
        if doc_type_filter in ("all", "referral", "referral_letter") and record.get("referral_letter"):
            referral = ReferralLetter.model_validate(record["referral_letter"])
            pdf_bytes = generate_referral_letter_pdf(referral)
            filename = f"referral_letter_{session_id[:8]}.pdf"
            public_url = await supabase_service.upload_patient_pdf(
                patient_identifier=patient_id,
                session_id=session_id,
                document_type="referral_letter",
                pdf_bytes=pdf_bytes,
                filename=filename,
            )
            dl_url = f"{base_url}/api/consultation/{session_id}/download-pdf/referral_letter"
            pdf_urls["referral_letter"] = public_url
            download_urls["referral_letter"] = dl_url
            generated_items.append(GeneratedPDFItem(
                document_type="referral_letter",
                title="Specialist Consultation & Referral Letter",
                filename=filename,
                pdf_url=public_url,
                download_url=dl_url,
            ))

        if not generated_items:
            raise HTTPException(status_code=400, detail="No generated clinical documents found for this session to produce PDFs.")

        # Primary default URLs
        primary_pdf = generated_items[0].pdf_url
        primary_dl = generated_items[0].download_url

        return GeneratePDFResponse(
            session_id=session_id,
            patient_id=patient_id,
            status="completed",
            pdf_url=primary_pdf,
            download_url=primary_dl,
            pdf_urls=pdf_urls,
            download_urls=download_urls,
            generated_pdfs=generated_items,
            message="PDFs generated and stored per patient in Supabase Storage successfully.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDFs for {request.session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# Direct PDF Stream & Attachment Download Endpoints
# ==============================================================================
@router.get("/api/consultation/{session_id}/pdf/{document_type}")
@router.get("/api/consultation/{session_id}/pdf")
async def view_consultation_pdf(session_id: str, document_type: str = "case_sheet_summary"):
    """
    Streams the requested PDF inline for browser viewing.
    """
    try:
        record = await supabase_service.get_consultation(session_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Consultation session '{session_id}' not found.")

        patient_name = record.get("patient_name") or "patient"
        safe_patient = "".join(c for c in patient_name.lower() if c.isalnum() or c in ("-", "_")).strip()
        patient_id = record.get("patient_id") or f"patient_{safe_patient}"

        # Fetch or generate PDF bytes
        pdf_bytes = await supabase_service.get_patient_pdf_bytes(session_id, document_type, patient_identifier=patient_id)
        if not pdf_bytes:
            if document_type in ("case_sheet_summary", "case_sheet") and record.get("case_sheet_summary"):
                pdf_bytes = generate_case_sheet_pdf(CaseSheetSummary.model_validate(record["case_sheet_summary"]))
            elif document_type in ("patient_visit_summary", "patient_summary") and record.get("patient_visit_summary"):
                pdf_bytes = generate_patient_summary_pdf(PatientVisitSummary.model_validate(record["patient_visit_summary"]))
            elif document_type in ("discharge_instructions", "discharge") and record.get("discharge_instructions"):
                pdf_bytes = generate_discharge_instructions_pdf(DischargeInstructions.model_validate(record["discharge_instructions"]))
            elif document_type in ("referral_letter", "referral") and record.get("referral_letter"):
                pdf_bytes = generate_referral_letter_pdf(ReferralLetter.model_validate(record["referral_letter"]))
            else:
                for doc_key, gen_fn, model_cls in [
                    ("case_sheet_summary", generate_case_sheet_pdf, CaseSheetSummary),
                    ("patient_visit_summary", generate_patient_summary_pdf, PatientVisitSummary),
                    ("discharge_instructions", generate_discharge_instructions_pdf, DischargeInstructions),
                    ("referral_letter", generate_referral_letter_pdf, ReferralLetter),
                ]:
                    if record.get(doc_key):
                        pdf_bytes = gen_fn(model_cls.model_validate(record[doc_key]))
                        document_type = doc_key
                        break

        if not pdf_bytes:
            raise HTTPException(status_code=404, detail=f"No PDF data available for document type '{document_type}'.")

        filename = f"{document_type}_{session_id[:8]}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error streaming PDF for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/consultation/{session_id}/download-pdf/{document_type}")
@router.get("/api/consultation/{session_id}/download-pdf")
async def download_consultation_pdf(session_id: str, document_type: str = "case_sheet_summary"):
    """
    Downloads the requested PDF as an attachment.
    """
    try:
        record = await supabase_service.get_consultation(session_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Consultation session '{session_id}' not found.")

        patient_name = record.get("patient_name") or "patient"
        safe_patient = "".join(c for c in patient_name.lower() if c.isalnum() or c in ("-", "_")).strip()
        patient_id = record.get("patient_id") or f"patient_{safe_patient}"

        pdf_bytes = await supabase_service.get_patient_pdf_bytes(session_id, document_type, patient_identifier=patient_id)
        if not pdf_bytes:
            if document_type in ("case_sheet_summary", "case_sheet") and record.get("case_sheet_summary"):
                pdf_bytes = generate_case_sheet_pdf(CaseSheetSummary.model_validate(record["case_sheet_summary"]))
            elif document_type in ("patient_visit_summary", "patient_summary") and record.get("patient_visit_summary"):
                pdf_bytes = generate_patient_summary_pdf(PatientVisitSummary.model_validate(record["patient_visit_summary"]))
            elif document_type in ("discharge_instructions", "discharge") and record.get("discharge_instructions"):
                pdf_bytes = generate_discharge_instructions_pdf(DischargeInstructions.model_validate(record["discharge_instructions"]))
            elif document_type in ("referral_letter", "referral") and record.get("referral_letter"):
                pdf_bytes = generate_referral_letter_pdf(ReferralLetter.model_validate(record["referral_letter"]))
            else:
                for doc_key, gen_fn, model_cls in [
                    ("case_sheet_summary", generate_case_sheet_pdf, CaseSheetSummary),
                    ("patient_visit_summary", generate_patient_summary_pdf, PatientVisitSummary),
                    ("discharge_instructions", generate_discharge_instructions_pdf, DischargeInstructions),
                    ("referral_letter", generate_referral_letter_pdf, ReferralLetter),
                ]:
                    if record.get(doc_key):
                        pdf_bytes = gen_fn(model_cls.model_validate(record[doc_key]))
                        document_type = doc_key
                        break

        if not pdf_bytes:
            raise HTTPException(status_code=404, detail=f"No PDF data available for download.")

        filename = f"{document_type}_{session_id[:8]}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# Endpoint 4: Consultation Details & History
# ==============================================================================
@router.get("/api/consultation/{session_id}", response_model=ConsultationDetailResponse)
async def get_consultation(session_id: str):
    """
    Retrieves full consultation record, SOAP data, all generated documents, and PDF links from Supabase.
    """
    try:
        record = await supabase_service.get_consultation(session_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Consultation session '{session_id}' not found.")

        soap_obj = (
            ClinicalSOAPExtraction.model_validate(record["soap_data"])
            if record.get("soap_data")
            else None
        )
        patient_summary_obj = (
            PatientVisitSummary.model_validate(record["patient_visit_summary"])
            if record.get("patient_visit_summary")
            else None
        )
        case_sheet_obj = (
            CaseSheetSummary.model_validate(record["case_sheet_summary"])
            if record.get("case_sheet_summary")
            else None
        )
        discharge_obj = (
            DischargeInstructions.model_validate(record["discharge_instructions"])
            if record.get("discharge_instructions")
            else None
        )
        referral_obj = (
            ReferralLetter.model_validate(record["referral_letter"])
            if record.get("referral_letter")
            else None
        )

        return ConsultationDetailResponse(
            session_id=record["session_id"],
            status=record.get("status", "pending_review"),
            patient_id=record.get("patient_id"),
            patient_name=record.get("patient_name"),
            doctor_name=record.get("doctor_name"),
            encounter_date=record.get("encounter_date"),
            transcript=record.get("transcript"),
            soap=soap_obj,
            patient_visit_summary=patient_summary_obj,
            case_sheet_summary=case_sheet_obj,
            discharge_instructions=discharge_obj,
            referral_letter=referral_obj,
            pdf_url=record.get("pdf_url"),
            pdf_urls=record.get("pdf_urls"),
            created_at=record.get("created_at"),
            updated_at=record.get("updated_at"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching consultation {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/consultations")
async def list_consultations(limit: int = Query(50, ge=1, le=100)):
    """
    Lists recent consultations stored in Supabase.
    """
    try:
        records = await supabase_service.list_consultations(limit=limit)
        return {"total": len(records), "consultations": records}
    except Exception as e:
        logger.error(f"Error listing consultations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# RAG Drug-Drug Interaction & Contraindication Alert Endpoints
# ==============================================================================
@router.post("/api/drug-alerts/check", response_model=DrugAlertCheckResponse)
async def check_drug_interactions(request: DrugAlertCheckRequest):
    """
    RAG-powered Drug-Drug Interaction and Contraindication Alert System.
    - Extracts medication entities from raw conversation dialogue, explicit medication lists, or patient history
    - Performs hybrid retrieval (exact metadata filters + cosine semantic search) over ChromaDB vector store
    - Returns structured alert cards with severity (CRITICAL, HIGH, MODERATE), clinical reasons, and actionable provider guidance.
    """
    try:
        transcript = request.transcript
        medications = request.medications or []
        history = request.patient_history or []

        # If session_id provided, supplement with stored consultation transcript & medications
        if request.session_id:
            record = await supabase_service.get_consultation(request.session_id)
            if record:
                if not transcript and record.get("transcript"):
                    transcript = record["transcript"]
                soap_data = record.get("soap_data")
                if soap_data and isinstance(soap_data, dict):
                    plan = soap_data.get("plan", {})
                    rx_list = plan.get("medications", [])
                    for rx in rx_list:
                        if isinstance(rx, dict) and rx.get("name"):
                            medications.append(rx["name"])

        # Detect all candidate medications
        all_detected = set()
        if medications:
            for med in medications:
                all_detected.update(drug_alert_service.extract_drugs_from_text(med))
        if transcript:
            all_detected.update(drug_alert_service.extract_drugs_from_text(transcript))
        if history:
            for hist in history:
                all_detected.update(drug_alert_service.extract_drugs_from_text(hist))

        detected_list = sorted(list(all_detected))

        # Run True LLM RAG Interaction Checker (Retrieval + Augmentation + Generation)
        response = await drug_alert_service.check_interactions(
            transcript=transcript,
            medications=medications,
            patient_history=history,
        )
        return response
    except Exception as e:
        logger.error(f"Error checking drug interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/drug-alerts/stats")
async def get_drug_alert_stats():
    """
    Returns statistics on indexed drug-drug interaction rules in ChromaDB.
    """
    try:
        count = drug_alert_service.get_collection_count()
        return {
            "status": "online",
            "indexed_interaction_rules": count,
            "vector_store": "ChromaDB",
            "knowledge_base": "interactions.jsonl",
        }
    except Exception as e:
        logger.error(f"Error getting drug alert stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

