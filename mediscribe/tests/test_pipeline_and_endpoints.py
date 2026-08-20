import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to sys.path
MEDISCRIBE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MEDISCRIBE_DIR))

from main import app
from src.api.schemas import (
    ClinicalSOAPExtraction,
    PatientVisitSummary,
    CaseSheetSummary,
    DischargeInstructions,
    ReferralLetter,
)

SAMPLE_TRANSCRIPT = """
Consultation Transcript
Provider: Dr. Anita Rao, MD
Patient: Mr. Rajesh Verma, 58 y/o Male
Date: 2026-07-11

DR. RAO: Good morning, Mr. Verma. What brings you in today?
PATIENT: Morning, Doctor. My knees have been hurting for the past two weeks, and I've also been getting mild headaches and dizziness.
DR. RAO: Let's check your vitals. BP is 148/92 mmHg, pulse 78 bpm, regular. On physical examination, mild swelling in the left knee, bilateral crepitus. Lungs are clear.
DR. RAO: You mentioned you are taking Losartan 50mg daily and an over-the-counter potassium supplement, plus Ibuprofen 400mg daily. Taking Ibuprofen with Losartan is elevating your blood pressure and stressing your kidneys.
DR. RAO: Here is the plan: Discontinue Ibuprofen and potassium supplement immediately. I am prescribing Paracetamol 500mg, 1 tablet up to 3 times daily as needed for knee pain. We will order a Basic Metabolic Panel (BMP) blood test. Increase daily water intake to 2 liters.
DR. RAO: In addition, given the chronic bilateral knee crepitus and localized left knee swelling, I am placing an urgent referral to Dr. Miller at the Department of Orthopedics for comprehensive evaluation, weight-bearing bilateral knee X-rays, and physical therapy consultation. Return for a follow-up visit in 2 weeks.
"""

client = TestClient(app)

def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["agent_ready"] is True
    print("\n[PASS] Health check passed.")

def test_step1_extract_soap():
    """Tests Step 1: Extract structured SOAP from transcript."""
    res = client.post(
        "/api/extract-soap",
        json={"transcript": SAMPLE_TRANSCRIPT, "session_id": "sess_pdf_test_01", "patient_id": "p_rajesh_58"},
    )
    assert res.status_code == 200, f"Extract SOAP failed: {res.text}"
    data = res.json()
    assert data["session_id"] == "sess_pdf_test_01"
    assert data["status"] == "pending_review"
    assert "soap" in data
    soap = data["soap"]
    print("\n[PASS] Step 1: POST /api/extract-soap succeeded.")
    return soap

def test_step2_generate_documents(soap):
    """Tests Step 2: Generate documents with autonomous triage."""
    res = client.post(
        "/api/generate-documents",
        json={
            "session_id": "sess_pdf_test_01",
            "verified_soap": soap,
            "generate_case_sheet": True,
        },
    )
    assert res.status_code == 200, f"Generate documents failed: {res.text}"
    data = res.json()
    assert data["status"] == "completed"
    assert data["patient_visit_summary"] is not None
    assert data["case_sheet_summary"] is not None
    assert data["discharge_instructions"] is not None
    assert data["referral_letter"] is not None
    print("\n[PASS] Step 2: POST /api/generate-documents succeeded (All 4 docs ready).")

def test_step3_generate_and_store_pdfs():
    """Tests Step 3: Generate and store PDFs partitioned by patient separately in Supabase."""
    res = client.post(
        "/api/generate-pdf",
        json={
            "session_id": "sess_pdf_test_01",
            "document_type": "all",
        },
    )
    assert res.status_code == 200, f"Generate PDF failed: {res.text}"
    data = res.json()
    assert data["session_id"] == "sess_pdf_test_01"
    assert data["status"] == "completed"
    assert len(data["generated_pdfs"]) >= 3
    assert "case_sheet_summary" in data["pdf_urls"]
    assert "patient_visit_summary" in data["pdf_urls"]
    assert "discharge_instructions" in data["pdf_urls"]
    assert "referral_letter" in data["pdf_urls"]

    print("\n[PASS] Step 3: POST /api/generate-pdf generated all patient PDFs:")
    for item in data["generated_pdfs"]:
        print(f" - [{item['document_type']}]: {item['pdf_url']}")

def test_pdf_streaming_endpoints():
    """Tests direct streaming and download endpoints for the generated PDFs."""
    # 1. Stream Patient Summary PDF
    res = client.get("/api/consultation/sess_pdf_test_01/pdf/patient_visit_summary")
    assert res.status_code == 200
    assert res.headers.get("content-type") == "application/pdf"
    assert res.content.startswith(b"%PDF-")
    print("\n[PASS] Stream Patient Summary PDF size:", len(res.content), "bytes")

    # 2. Stream Case Sheet PDF
    res = client.get("/api/consultation/sess_pdf_test_01/pdf/case_sheet_summary")
    assert res.status_code == 200
    assert res.content.startswith(b"%PDF-")
    print("[PASS] Stream Case Sheet PDF size:", len(res.content), "bytes")

    # 3. Stream Discharge Instructions PDF
    res = client.get("/api/consultation/sess_pdf_test_01/pdf/discharge_instructions")
    assert res.status_code == 200
    assert res.content.startswith(b"%PDF-")
    print("[PASS] Stream Discharge Instructions PDF size:", len(res.content), "bytes")

    # 4. Stream Referral Letter PDF
    res = client.get("/api/consultation/sess_pdf_test_01/pdf/referral_letter")
    assert res.status_code == 200
    assert res.content.startswith(b"%PDF-")
    print("[PASS] Stream Referral Letter PDF size:", len(res.content), "bytes")

    # 5. Attachment Download
    dl_res = client.get("/api/consultation/sess_pdf_test_01/download-pdf/patient_visit_summary")
    assert dl_res.status_code == 200
    assert "attachment;" in dl_res.headers.get("content-disposition", "")
    print("[PASS] Attachment download passed.")

def test_consultation_retrieval_with_pdfs():
    """Tests GET /api/consultation/{session_id} includes all documents and PDF URLs."""
    res = client.get("/api/consultation/sess_pdf_test_01")
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] == "sess_pdf_test_01"
    assert data["status"] == "completed"
    assert data["patient_visit_summary"] is not None
    assert data["pdf_urls"] is not None
    print("\n[PASS] GET /api/consultation/{session_id} verified with PDF records.")

if __name__ == "__main__":
    test_health_check()
    soap = test_step1_extract_soap()
    test_step2_generate_documents(soap)
    test_step3_generate_and_store_pdfs()
    test_pdf_streaming_endpoints()
    test_consultation_retrieval_with_pdfs()
    print("\n[SUCCESS] ALL MULTI-DOCUMENT PDF GENERATION AND STORAGE TESTS PASSED!")
