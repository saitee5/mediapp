import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to sys.path
MEDISCRIBE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MEDISCRIBE_DIR))

from main import app
from src.api.schemas import CaseSheetSummary, PrescriptionItem
from src.utils.pdf_generator import generate_case_sheet_pdf

SAMPLE_TRANSCRIPT = """
Consultation Transcript
Provider: Dr. Anita Rao, MD
Patient: Mr. Rajesh Verma, 58 y/o Male
Date: 2026-07-11

DR. RAO: Good morning, Mr. Verma. What brings you in today?
PATIENT: Morning, Doctor. My knees have been killing me for the past two weeks, and I've also been getting headaches.
DR. RAO: Let's check your blood pressure. It is 148 over 92, heart rate 78. On exam, mild swelling of the left knee, mild crepitus in both knees.
DR. RAO: You are currently on Losartan 50mg daily and a potassium supplement. Taking Ibuprofen regularly with Losartan and potassium supplement is straining your kidneys and raising your blood pressure.
DR. RAO: Let's stop the Ibuprofen and potassium supplement. I am prescribing Paracetamol 500mg, 3-4 times daily as needed. We will order a BMP lab test. Return in 2 weeks.
"""

def test_endpoints_workflow():
    """Test the exact unique endpoints:
    1. POST /api/generate-summary
    2. POST /api/update-summary
    3. POST /api/generate-pdf
    4. GET /api/consultation/{session_id}/download-pdf
    """
    client = TestClient(app)

    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "online"
    print("\n[PASS] Health check passed.")

    # 2. Step 1: Generate initial summary from transcript
    gen_res = client.post(
        "/api/generate-summary",
        json={"transcript": SAMPLE_TRANSCRIPT, "session_id": "sess_unique_01"},
    )
    assert gen_res.status_code == 200, f"Generate summary failed: {gen_res.text}"
    gen_data = gen_res.json()
    assert gen_data["session_id"] == "sess_unique_01"
    assert gen_data["status"] == "pending_review"
    assert "case_study_summary" in gen_data
    case_study = gen_data["case_study_summary"]
    print("\n[PASS] POST /api/generate-summary passed.")
    print("Patient:", case_study["patient_name"])

    # 3. Step 2: Update stored case study summary
    edited_summary = dict(case_study)
    edited_summary["notes"] = "Doctor review: Confirmed stop Ibuprofen and potassium supplement."
    edited_summary["treatment_plan"] = "Doctor confirmed: Paracetamol 500mg + BMP in 2 weeks."

    update_res = client.post(
        "/api/update-summary",
        json={
            "session_id": "sess_unique_01",
            "updated_case_study_summary": edited_summary,
        },
    )
    assert update_res.status_code == 200, f"Update summary failed: {update_res.text}"
    update_data = update_res.json()
    assert update_data["status"] == "reviewed"
    assert update_data["updated_case_study_summary"]["notes"] == edited_summary["notes"]
    print("\n[PASS] POST /api/update-summary passed.")

    # 4. Step 3: Generate PDF
    pdf_gen_res = client.post(
        "/api/generate-pdf",
        json={"session_id": "sess_unique_01"},
    )
    assert pdf_gen_res.status_code == 200, f"Generate PDF failed: {pdf_gen_res.text}"
    pdf_gen_data = pdf_gen_res.json()
    assert "pdf_url" in pdf_gen_data and pdf_gen_data["pdf_url"] is not None
    assert "download_url" in pdf_gen_data and pdf_gen_data["download_url"] is not None
    print("\n[PASS] POST /api/generate-pdf passed. Public URL:", pdf_gen_data["pdf_url"])

    # 5. Step 4: Download PDF
    dl_res = client.get("/api/consultation/sess_unique_01/download-pdf")
    assert dl_res.status_code == 200
    assert dl_res.headers.get("content-type") == "application/pdf"
    assert dl_res.content.startswith(b"%PDF-")
    print("\n[PASS] GET /api/consultation/{session_id}/download-pdf passed. Size:", len(dl_res.content))

if __name__ == "__main__":
    test_endpoints_workflow()
