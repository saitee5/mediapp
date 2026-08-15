import io
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from src.api.schemas import (
    GenerateSummaryRequest,
    GenerateSummaryResponse,
    UpdateSummaryRequest,
    UpdateSummaryResponse,
    GeneratePDFRequest,
    GeneratePDFResponse,
    ConsultationDetailResponse,
    HealthCheckResponse,
    CaseSheetSummary,
    ClinicalSOAPExtraction,
)
from src.agent import agent
from src.services import supabase_service
from src.utils.pdf_generator import generate_case_sheet_pdf
from src.utils.config import settings
from src.utils.logger import logger

router = APIRouter()

@router.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint providing status of LLM and Supabase."""
    return HealthCheckResponse(
        status="online",
        llm_configured=True,
        model=settings.DEFAULT_LLM_MODEL,
        supabase_configured=supabase_service.is_configured(),
        agent_ready=True,
    )

# ==============================================================================
# Endpoint 1: Generate Case Study Summary from Transcript for Frontend Review
# ==============================================================================
@router.post("/api/generate-summary", response_model=GenerateSummaryResponse)
async def generate_summary(request: GenerateSummaryRequest):
    """
    Step 1:
    - Receives conversation transcript
    - Runs exact 2-agent LangGraph pipeline (SOAPExtractionAgent -> CaseSheetSummaryGen)
    - Saves initial summary in Supabase with status 'pending_review'
    - Returns Case Study Summary to frontend for review
    """
    try:
        session_id = request.session_id or f"consultation_{uuid.uuid4().hex[:12]}"
        logger.info(f"API [Step 1]: Generating case study summary for session {session_id}...")

        # Run exact LangGraph pipeline
        result = await agent.generate_summary(request.transcript)
        soap_data = result.get("soap")
        case_sheet_data = result.get("case_sheet_summary")

        if not soap_data or not case_sheet_data:
            raise RuntimeError("Agent pipeline failed to produce complete SOAP or CaseSheetSummary.")

        # Persist initial record in Supabase
        await supabase_service.save_consultation(
            session_id=session_id,
            transcript=request.transcript,
            soap=soap_data,
            case_sheet_summary=case_sheet_data,
            patient_id=request.patient_id,
            status="pending_review",
        )

        return GenerateSummaryResponse(
            session_id=session_id,
            status="pending_review",
            case_study_summary=case_sheet_data,
            soap=soap_data,
            message="Case study summary generated successfully. Ready for frontend review.",
        )
    except Exception as e:
        logger.error(f"Error in generate-summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# Endpoint 2: Update Stored Case Study Summary (After Frontend Review)
# ==============================================================================
@router.post("/api/update-summary", response_model=UpdateSummaryResponse)
async def update_case_study_summary(request: UpdateSummaryRequest):
    """
    Step 2:
    - Receives updated / validated case_study_summary from frontend
    - Updates database record in Supabase with updated_case_sheet_summary
    - Sets status to 'reviewed'
    - Returns updated summary confirmation
    """
    try:
        session_id = request.session_id
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id must be provided in request body.")

        logger.info(f"API [Step 2]: Updating case study summary for session {session_id}...")
        updated_data = request.updated_case_study_summary

        # Update Supabase database record
        record = await supabase_service.update_case_sheet_summary(
            session_id=session_id,
            updated_case_sheet_summary=updated_data,
            status="reviewed",
        )

        if not record:
            raise HTTPException(status_code=404, detail=f"Consultation session '{session_id}' not found.")

        return UpdateSummaryResponse(
            session_id=session_id,
            status="reviewed",
            updated_case_study_summary=updated_data,
            message="Case study summary successfully updated in database.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating case study summary for {request.session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# Endpoint 3: Generate & Upload PDF (Only takes session_id)
# ==============================================================================
@router.post("/api/generate-pdf", response_model=GeneratePDFResponse)
async def generate_pdf(
    request: GeneratePDFRequest,
    req: Request = None,
):
    """
    Step 3:
    - Takes only session_id
    - Fetches the last stored case study summary from the database
    - Generates formatted hospital PDF
    - Uploads PDF to Supabase Storage bucket ('case-sheets')
    - Updates database record with public pdf_url
    - Returns public Supabase PDF URL and backend download URL
    """
    try:
        session_id = request.session_id
        logger.info(f"API [Step 3]: Generating PDF for session {session_id} from database...")

        # Fetch last stored case study summary from database
        record = await supabase_service.get_consultation(session_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Consultation session '{session_id}' not found in database.")

        raw_summary = record.get("updated_case_sheet_summary") or record.get("case_sheet_summary")
        if not raw_summary:
            raise HTTPException(status_code=400, detail=f"No Case Study Summary found in database for session '{session_id}'.")

        target_summary = CaseSheetSummary.model_validate(raw_summary)

        # Generate PDF bytes
        pdf_bytes = generate_case_sheet_pdf(target_summary)

        # Upload to Supabase Storage
        safe_patient = "".join(c for c in target_summary.patient_name if c.isalnum() or c in (" ", "_", "-")).strip() or "patient"
        filename = f"case_sheet_{safe_patient.replace(' ', '_')}_{session_id[:8]}.pdf"
        
        pdf_url = await supabase_service.upload_pdf(
            session_id=session_id,
            pdf_bytes=pdf_bytes,
            filename=filename,
        )

        base_url = str(req.base_url).rstrip("/") if req else ""
        download_url = f"{base_url}/api/consultation/{session_id}/download-pdf"

        # Check status
        record = await supabase_service.get_consultation(session_id)
        current_status = record.get("status", "reviewed") if record else "reviewed"

        return GeneratePDFResponse(
            session_id=session_id,
            status=current_status,
            pdf_url=pdf_url,
            download_url=download_url,
            message="PDF generated and uploaded to Supabase Storage successfully.",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF for {request.session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# Endpoint 4: Direct Download & View PDF Endpoints
# ==============================================================================
@router.get("/api/consultation/{session_id}/download-pdf")
async def download_consultation_pdf(session_id: str):
    """
    Download endpoint: Returns the PDF as an attachment download from backend.
    """
    try:
        record = await supabase_service.get_consultation(session_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Consultation session '{session_id}' not found.")

        raw_summary = record.get("updated_case_sheet_summary") or record.get("case_sheet_summary")
        if not raw_summary:
            raise HTTPException(status_code=400, detail="No Case Study Summary available to generate PDF.")

        case_sheet = CaseSheetSummary.model_validate(raw_summary)
        pdf_bytes = generate_case_sheet_pdf(case_sheet)

        safe_patient = "".join(c for c in case_sheet.patient_name if c.isalnum() or c in (" ", "_", "-")).strip() or "patient"
        safe_filename = f"case_sheet_{safe_patient.replace(' ', '_')}_{session_id[:8]}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={safe_filename}",
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/consultation/{session_id}/pdf")
async def view_consultation_pdf(session_id: str):
    """
    View endpoint: Streams the PDF inline for browser viewing.
    """
    try:
        record = await supabase_service.get_consultation(session_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Consultation session '{session_id}' not found.")

        raw_summary = record.get("updated_case_sheet_summary") or record.get("case_sheet_summary")
        if not raw_summary:
            raise HTTPException(status_code=400, detail="No Case Study Summary available to generate PDF.")

        case_sheet = CaseSheetSummary.model_validate(raw_summary)
        pdf_bytes = generate_case_sheet_pdf(case_sheet)

        safe_patient = "".join(c for c in case_sheet.patient_name if c.isalnum() or c in (" ", "_", "-")).strip() or "patient"
        safe_filename = f"case_sheet_{safe_patient.replace(' ', '_')}_{session_id[:8]}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={safe_filename}",
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error streaming PDF for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/consultation/{session_id}", response_model=ConsultationDetailResponse)
async def get_consultation(session_id: str, req: Request = None):
    """
    Retrieves full consultation record, SOAP data, case study summaries, and PDF links from Supabase.
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
        case_sheet_obj = (
            CaseSheetSummary.model_validate(record["case_sheet_summary"])
            if record.get("case_sheet_summary")
            else None
        )
        updated_obj = (
            CaseSheetSummary.model_validate(record["updated_case_sheet_summary"])
            if record.get("updated_case_sheet_summary")
            else None
        )

        base_url = str(req.base_url).rstrip("/") if req else ""
        download_url = f"{base_url}/api/consultation/{session_id}/download-pdf"

        return ConsultationDetailResponse(
            session_id=record["session_id"],
            status=record.get("status", "pending_review"),
            patient_id=record.get("patient_id"),
            patient_name=record.get("patient_name"),
            doctor_name=record.get("doctor_name"),
            encounter_date=record.get("encounter_date"),
            transcript=record.get("transcript"),
            soap=soap_obj,
            case_sheet_summary=case_sheet_obj,
            updated_case_sheet_summary=updated_obj,
            pdf_url=record.get("pdf_url"),
            download_url=download_url,
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
