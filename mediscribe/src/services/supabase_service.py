import datetime
from typing import Optional, Dict, Any, List
from src.api.schemas import ClinicalSOAPExtraction, CaseSheetSummary
from src.utils.config import settings
from src.utils.logger import logger

class SupabaseService:
    """
    Manages persistence of consultation sessions, SOAP extractions,
    Case Sheet Summaries, and PDF storage in Supabase (with in-memory fallback).
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
        except Exception as e:
            # Bucket likely already exists
            pass
        self._bucket_checked = True

    async def save_consultation(
        self,
        session_id: str,
        transcript: str,
        soap: ClinicalSOAPExtraction,
        case_sheet_summary: CaseSheetSummary,
        patient_id: Optional[str] = None,
        status: str = "pending_review",
    ) -> Dict[str, Any]:
        """
        Saves a new consultation record with initial AI-generated SOAP and CaseSheetSummary.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        soap_dict = soap.model_dump() if hasattr(soap, "model_dump") else soap
        case_sheet_dict = case_sheet_summary.model_dump() if hasattr(case_sheet_summary, "model_dump") else case_sheet_summary

        data_row = {
            "session_id": session_id,
            "patient_id": patient_id,
            "patient_name": case_sheet_summary.patient_name,
            "doctor_name": case_sheet_summary.doctor,
            "encounter_date": case_sheet_summary.date,
            "transcript": transcript,
            "soap_data": soap_dict,
            "case_sheet_summary": case_sheet_dict,
            "updated_case_sheet_summary": None,
            "status": status,
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        # Local cache / fallback
        self._local_store[session_id] = data_row

        if self.client:
            try:
                # Upsert into supabase consultations table
                res = self.client.table("consultations").upsert(data_row, on_conflict="session_id").execute()
                if res.data:
                    logger.info(f"Successfully stored consultation {session_id} in Supabase.")
                    return res.data[0]
            except Exception as e:
                logger.error(f"Error persisting consultation to Supabase: {e}. Saved in memory.")

        return data_row

    async def get_consultation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves consultation record by session_id.
        """
        if self.client:
            try:
                res = self.client.table("consultations").select("*").eq("session_id", session_id).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
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
        """
        Updates an existing consultation record with the reviewed CaseSheetSummary from frontend.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        updated_dict = (
            updated_case_sheet_summary.model_dump()
            if hasattr(updated_case_sheet_summary, "model_dump")
            else updated_case_sheet_summary
        )

        update_payload: Dict[str, Any] = {
            "updated_case_sheet_summary": updated_dict,
            "status": status,
            "updated_at": now_iso,
        }
        if pdf_url:
            update_payload["pdf_url"] = pdf_url

        # Update local memory
        if session_id in self._local_store:
            self._local_store[session_id].update(update_payload)
            self._local_store[session_id]["patient_name"] = updated_case_sheet_summary.patient_name
            self._local_store[session_id]["doctor_name"] = updated_case_sheet_summary.doctor
        else:
            self._local_store[session_id] = {
                "session_id": session_id,
                "case_sheet_summary": updated_dict,
                **update_payload,
            }

        if self.client:
            try:
                res = self.client.table("consultations").update(update_payload).eq("session_id", session_id).execute()
                if res.data and len(res.data) > 0:
                    logger.info(f"Successfully updated consultation {session_id} in Supabase.")
                    return res.data[0]
            except Exception as e:
                err_str = str(e)
                # If pdf_url column does not exist in schema cache, retry without pdf_url
                if "pdf_url" in err_str:
                    try:
                        fallback_payload = {k: v for k, v in update_payload.items() if k != "pdf_url"}
                        res = self.client.table("consultations").update(fallback_payload).eq("session_id", session_id).execute()
                        if res.data and len(res.data) > 0:
                            logger.info(f"Successfully updated consultation {session_id} in Supabase (without pdf_url column).")
                            return res.data[0]
                    except Exception as retry_err:
                        logger.error(f"Retry update without pdf_url failed: {retry_err}")
                else:
                    logger.error(f"Error updating consultation in Supabase: {e}")

        return self._local_store.get(session_id)

    async def upload_pdf(
        self,
        session_id: str,
        pdf_bytes: bytes,
        filename: Optional[str] = None,
    ) -> str:
        """
        Uploads generated PDF to Supabase Storage bucket ('case-sheets') and updates the database record.
        """
        bucket_name = settings.SUPABASE_STORAGE_BUCKET
        clean_name = filename or f"case_sheet_{session_id}.pdf"
        file_path = f"{session_id}/{clean_name}"
        pdf_url = None

        if self.client:
            self._ensure_bucket(bucket_name)
            try:
                # Upload or upsert to Supabase Storage
                self.client.storage.from_(bucket_name).upload(
                    path=file_path,
                    file=pdf_bytes,
                    file_options={"content-type": "application/pdf", "upsert": "true"},
                )
                # Get public URL
                public_res = self.client.storage.from_(bucket_name).get_public_url(file_path)
                pdf_url = public_res if isinstance(public_res, str) else public_res.get("publicUrl", "")
                logger.info(f"Uploaded PDF to Supabase Storage bucket '{bucket_name}': {pdf_url}")

                # Update database record with pdf_url (if column exists)
                try:
                    self.client.table("consultations").update({"pdf_url": pdf_url}).eq("session_id", session_id).execute()
                except Exception as col_err:
                    logger.warning(f"Could not update pdf_url column in database (schema might need migration): {col_err}")

            except Exception as e:
                logger.error(f"Error uploading PDF to Supabase Storage bucket '{bucket_name}': {e}")

        # Fallback local URL if Supabase storage upload was skipped/unconfigured
        if not pdf_url:
            pdf_url = f"/api/consultation/{session_id}/pdf"

        # Update local memory
        if session_id in self._local_store:
            self._local_store[session_id]["pdf_url"] = pdf_url
            self._local_store[session_id]["_pdf_bytes"] = pdf_bytes
        else:
            self._local_store[session_id] = {
                "session_id": session_id,
                "pdf_url": pdf_url,
                "_pdf_bytes": pdf_bytes,
            }

        return pdf_url

    async def get_pdf_bytes(self, session_id: str) -> Optional[bytes]:
        """
        Retrieves cached/stored PDF bytes if available.
        """
        record = self._local_store.get(session_id)
        if record and "_pdf_bytes" in record:
            return record["_pdf_bytes"]

        if self.client:
            try:
                bucket_name = settings.SUPABASE_STORAGE_BUCKET
                file_path = f"{session_id}/case_sheet_{session_id}.pdf"
                data = self.client.storage.from_(bucket_name).download(file_path)
                if data:
                    return data
            except Exception as e:
                logger.warning(f"Could not download PDF from Supabase storage for {session_id}: {e}")

        return None

    async def list_consultations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lists recent consultations.
        """
        if self.client:
            try:
                res = self.client.table("consultations").select("*").order("created_at", desc=True).limit(limit).execute()
                if res.data:
                    return res.data
            except Exception as e:
                logger.warning(f"Error listing consultations from Supabase: {e}")

        # Return local store items sorted by created_at desc
        return sorted(
            list(self._local_store.values()),
            key=lambda x: x.get("created_at", ""),
            reverse=True,
        )[:limit]

supabase_service = SupabaseService()
