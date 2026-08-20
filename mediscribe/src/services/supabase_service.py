import datetime
from typing import Optional, Dict, Any, List
from src.api.schemas import (
    ClinicalSOAPExtraction,
    CaseSheetSummary,
    PatientVisitSummary,
    DischargeInstructions,
    ReferralLetter,
)
from src.utils.config import settings
from src.utils.logger import logger

class SupabaseService:
    """
    Manages persistence of consultation sessions, SOAP extractions,
    generated clinical documents (Patient Visit Summary, Case Sheet, Discharge Instructions, Referral Letter),
    and PDF storage in Supabase organized per patient (with in-memory fallback).
    """

    def __init__(self):
        self.client = None
        self._local_store: Dict[str, Dict[str, Any]] = {}
        self._bucket_checked = False
        self._init_client()

    def _init_client(self):
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
        if url and key:
            try:
                from supabase import create_client, Client
                self.client: Optional[Client] = create_client(url, key)
                logger.info(f"Supabase client successfully initialized for {url}")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}. Falling back to in-memory store.")
                self.client = None
        else:
            logger.info("Supabase credentials not configured in environment. Using in-memory fallback storage.")

    def is_configured(self) -> bool:
        return self.client is not None

    def _ensure_bucket(self, bucket_name: str):
        """Ensures the storage bucket exists in Supabase Storage."""
        if not self.client or self._bucket_checked:
            return
        try:
            self.client.storage.create_bucket(bucket_name, options={"public": True})
            logger.info(f"Created Supabase Storage bucket '{bucket_name}'.")
        except Exception:
            pass
        self._bucket_checked = True

    async def save_soap_consultation(
        self,
        session_id: str,
        transcript: str,
        soap: ClinicalSOAPExtraction,
        patient_id: Optional[str] = None,
        status: str = "pending_review",
    ) -> Dict[str, Any]:
        """
        Step 1: Saves initial consultation session with extracted SOAP data for doctor review.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        soap_dict = soap.model_dump() if hasattr(soap, "model_dump") else soap

        admin = soap.administrative_data if hasattr(soap, "administrative_data") else None
        participants = admin.participants if admin else None
        encounter = admin.encounter_details if admin else None

        patient_name = participants.patient_name if participants else None
        doctor_name = participants.provider_name if participants else None
        encounter_date = encounter.date if encounter else None

        data_row = {
            "session_id": session_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            "encounter_date": encounter_date,
            "transcript": transcript,
            "soap_data": soap_dict,
            "case_sheet_summary": None,
            "patient_visit_summary": None,
            "discharge_instructions": None,
            "referral_letter": None,
            "pdf_urls": {},
            "status": status,
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        # Update local memory
        self._local_store[session_id] = dict(data_row)

        if self.client:
            try:
                res = self.client.table("consultations").upsert(data_row, on_conflict="session_id").execute()
                if res.data:
                    logger.info(f"Successfully stored initial SOAP for {session_id} in Supabase.")
                    return res.data[0]
            except Exception as e:
                try:
                    fallback_row = {
                        "session_id": session_id,
                        "patient_id": patient_id,
                        "patient_name": patient_name,
                        "doctor_name": doctor_name,
                        "encounter_date": encounter_date,
                        "transcript": transcript,
                        "soap_data": soap_dict,
                        "status": status,
                        "created_at": now_iso,
                        "updated_at": now_iso,
                    }
                    res = self.client.table("consultations").upsert(fallback_row, on_conflict="session_id").execute()
                    if res.data:
                        logger.info(f"Successfully stored initial SOAP for {session_id} in Supabase (fallback schema).")
                        return res.data[0]
                except Exception as retry_err:
                    logger.warning(f"Error persisting initial SOAP to Supabase: {retry_err}. Saved in memory.")

        return data_row

    async def save_generated_documents(
        self,
        session_id: str,
        soap: ClinicalSOAPExtraction,
        patient_visit_summary: PatientVisitSummary,
        case_sheet_summary: Optional[CaseSheetSummary] = None,
        discharge_instructions: Optional[DischargeInstructions] = None,
        referral_letter: Optional[ReferralLetter] = None,
        status: str = "completed",
    ) -> Dict[str, Any]:
        """
        Step 2: Saves the generated multi-document bundle (Patient Summary, Case Sheet, Discharge, Referral)
        and sets status to 'completed'.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        soap_dict = soap.model_dump() if hasattr(soap, "model_dump") else soap
        patient_summary_dict = patient_visit_summary.model_dump() if hasattr(patient_visit_summary, "model_dump") else patient_visit_summary
        case_sheet_dict = case_sheet_summary.model_dump() if (case_sheet_summary and hasattr(case_sheet_summary, "model_dump")) else case_sheet_summary
        discharge_dict = discharge_instructions.model_dump() if (discharge_instructions and hasattr(discharge_instructions, "model_dump")) else discharge_instructions
        referral_dict = referral_letter.model_dump() if (referral_letter and hasattr(referral_letter, "model_dump")) else referral_letter

        update_payload: Dict[str, Any] = {
            "soap_data": soap_dict,
            "patient_visit_summary": patient_summary_dict,
            "case_sheet_summary": case_sheet_dict,
            "discharge_instructions": discharge_dict,
            "referral_letter": referral_dict,
            "status": status,
            "updated_at": now_iso,
        }

        if case_sheet_summary and getattr(case_sheet_summary, "patient_name", None):
            update_payload["patient_name"] = case_sheet_summary.patient_name
            update_payload["doctor_name"] = case_sheet_summary.doctor
        elif patient_visit_summary and getattr(patient_visit_summary, "patient_name", None):
            update_payload["patient_name"] = patient_visit_summary.patient_name

        # Update local memory
        if session_id in self._local_store:
            self._local_store[session_id].update(update_payload)
        else:
            self._local_store[session_id] = {
                "session_id": session_id,
                **update_payload,
                "created_at": now_iso,
            }

        if self.client:
            try:
                res = self.client.table("consultations").update(update_payload).eq("session_id", session_id).execute()
                if res.data and len(res.data) > 0:
                    logger.info(f"Successfully saved generated documents for {session_id} in Supabase.")
                    return res.data[0]
            except Exception as e:
                try:
                    fallback_payload = {
                        "soap_data": soap_dict,
                        "case_sheet_summary": case_sheet_dict,
                        "status": status,
                        "updated_at": now_iso,
                    }
                    res = self.client.table("consultations").update(fallback_payload).eq("session_id", session_id).execute()
                    if res.data and len(res.data) > 0:
                        logger.info(f"Saved generated documents for {session_id} in Supabase (fallback schema).")
                        return res.data[0]
                except Exception as retry_err:
                    logger.warning(f"Supabase update note: {retry_err}. Stored in memory.")

        return self._local_store.get(session_id, update_payload)

    async def upload_patient_pdf(
        self,
        patient_identifier: str,
        session_id: str,
        document_type: str,
        pdf_bytes: bytes,
        filename: Optional[str] = None,
    ) -> str:
        """
        Uploads generated PDF to Supabase Storage organized by patient separately:
        Storage path format: {clean_patient_id}/{session_id}/{doc_name}.pdf
        """
        bucket_name = settings.SUPABASE_STORAGE_BUCKET
        clean_patient = "".join(c for c in patient_identifier.lower() if c.isalnum() or c in ("-", "_")).strip() or "patient_general"
        clean_name = filename or f"{document_type}.pdf"
        file_path = f"{clean_patient}/{session_id}/{clean_name}"
        pdf_url = None

        if self.client:
            self._ensure_bucket(bucket_name)
            try:
                self.client.storage.from_(bucket_name).upload(
                    path=file_path,
                    file=pdf_bytes,
                    file_options={"content-type": "application/pdf", "upsert": "true"},
                )
                public_res = self.client.storage.from_(bucket_name).get_public_url(file_path)
                pdf_url = public_res if isinstance(public_res, str) else public_res.get("publicUrl", "")
                logger.info(f"Uploaded patient PDF to Supabase Storage '{bucket_name}': {file_path}")
            except Exception as e:
                logger.error(f"Error uploading PDF to Supabase Storage: {e}")

        if not pdf_url:
            pdf_url = f"/api/consultation/{session_id}/pdf/{document_type}"

        # Cache in memory
        if session_id not in self._local_store:
            self._local_store[session_id] = {"session_id": session_id}
        if "pdf_urls" not in self._local_store[session_id]:
            self._local_store[session_id]["pdf_urls"] = {}
        if "_pdf_bytes" not in self._local_store[session_id]:
            self._local_store[session_id]["_pdf_bytes"] = {}

        self._local_store[session_id]["pdf_urls"][document_type] = pdf_url
        self._local_store[session_id]["_pdf_bytes"][document_type] = pdf_bytes
        self._local_store[session_id]["pdf_url"] = pdf_url  # Primary fallback

        # Attempt to update Supabase record with pdf_url
        if self.client:
            try:
                self.client.table("consultations").update({"pdf_url": pdf_url}).eq("session_id", session_id).execute()
            except Exception:
                pass

        return pdf_url

    async def get_patient_pdf_bytes(
        self,
        session_id: str,
        document_type: str,
        patient_identifier: Optional[str] = None,
    ) -> Optional[bytes]:
        """Retrieves cached or downloaded PDF bytes for a specific document."""
        record = self._local_store.get(session_id)
        if record and "_pdf_bytes" in record and document_type in record["_pdf_bytes"]:
            return record["_pdf_bytes"][document_type]

        if self.client:
            try:
                bucket_name = settings.SUPABASE_STORAGE_BUCKET
                clean_patient = "".join(c for c in (patient_identifier or "patient_general").lower() if c.isalnum() or c in ("-", "_")).strip()
                file_path = f"{clean_patient}/{session_id}/{document_type}.pdf"
                data = self.client.storage.from_(bucket_name).download(file_path)
                if data:
                    return data
            except Exception as e:
                logger.warning(f"Could not download PDF from Supabase storage for {session_id}/{document_type}: {e}")

        return None

    # Legacy / Backwards-compatibility wrapper
    async def upload_pdf(
        self,
        session_id: str,
        pdf_bytes: bytes,
        filename: Optional[str] = None,
    ) -> str:
        record = await self.get_consultation(session_id)
        patient_id = record.get("patient_id") if record else None
        if not patient_id and record and record.get("patient_name"):
            patient_id = record.get("patient_name").lower().replace(" ", "_")
        return await self.upload_patient_pdf(
            patient_identifier=patient_id or "patient_general",
            session_id=session_id,
            document_type="case_sheet_summary",
            pdf_bytes=pdf_bytes,
            filename=filename,
        )

    async def get_pdf_bytes(self, session_id: str) -> Optional[bytes]:
        return await self.get_patient_pdf_bytes(session_id=session_id, document_type="case_sheet_summary")

    async def get_consultation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves consultation record by session_id."""
        if self.client:
            try:
                res = self.client.table("consultations").select("*").eq("session_id", session_id).execute()
                if res.data and len(res.data) > 0:
                    record = res.data[0]
                    local_rec = self._local_store.get(session_id, {})
                    for k, v in local_rec.items():
                        if k not in record or record[k] is None:
                            record[k] = v
                    return record
            except Exception as e:
                logger.warning(f"Failed to fetch consultation from Supabase: {e}. Checking local store.")

        return self._local_store.get(session_id)

    async def update_case_sheet_summary(
        self,
        session_id: str,
        updated_case_sheet_summary: CaseSheetSummary,
        pdf_url: Optional[str] = None,
        status: str = "reviewed",
    ) -> Optional[Dict[str, Any]]:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        updated_dict = (
            updated_case_sheet_summary.model_dump()
            if hasattr(updated_case_sheet_summary, "model_dump")
            else updated_case_sheet_summary
        )

        update_payload: Dict[str, Any] = {
            "case_sheet_summary": updated_dict,
            "status": status,
            "updated_at": now_iso,
        }
        if pdf_url:
            update_payload["pdf_url"] = pdf_url

        if session_id in self._local_store:
            self._local_store[session_id].update(update_payload)
        else:
            self._local_store[session_id] = {"session_id": session_id, **update_payload}

        if self.client:
            try:
                res = self.client.table("consultations").update(update_payload).eq("session_id", session_id).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Error updating consultation in Supabase: {e}")

        return self._local_store.get(session_id)

    async def list_consultations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists recent consultations."""
        if self.client:
            try:
                res = self.client.table("consultations").select("*").order("created_at", desc=True).limit(limit).execute()
                if res.data:
                    return res.data
            except Exception as e:
                logger.warning(f"Error listing consultations from Supabase: {e}")

        return sorted(
            list(self._local_store.values()),
            key=lambda x: x.get("created_at", ""),
            reverse=True,
        )[:limit]

supabase_service = SupabaseService()
