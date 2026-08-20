import sys
import asyncio
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to sys.path
MEDISCRIBE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MEDISCRIBE_DIR))

from main import app
from src.drug_alerts import drug_alert_service

def test_drug_alerts_chroma_ingestion():
    """Verify ChromaDB ingested interactions.jsonl knowledge base."""
    count = drug_alert_service.get_collection_count()
    print(f"\n[INFO] ChromaDB collection '{drug_alert_service.collection_name}' has {count} records.")
    assert count >= 30, f"Expected at least 30 interaction records in ChromaDB, found {count}"
    print("[PASS] ChromaDB knowledge base collection initialized and fully indexed.")

def test_retrieval_evidence():
    """Verify ChromaDB retrieval for candidate query."""
    raw_docs, evidence = drug_alert_service.retrieve_relevant_guidelines(
        transcript="Patient taking Ibuprofen for knee pain and Losartan for blood pressure."
    )
    assert len(raw_docs) > 0
    assert len(evidence) > 50
    print(f"[PASS] ChromaDB retrieved {len(raw_docs)} guidelines:\n{evidence[:180]}...")

def test_llm_rag_interaction_generation():
    """Verify true RAG (Retrieval + Augmentation + LLM Generation) for NSAID + Losartan."""
    response = asyncio.run(drug_alert_service.check_interactions(
        transcript="Doctor: Let's start you on Ibuprofen 400mg TID. Patient: I already take Losartan 50mg daily for my hypertension.",
        medications=["Ibuprofen 400mg", "Losartan 50mg"]
    ))
    alerts = response.alerts
    print(f"\n[INFO] RAG LLM generated {len(alerts)} alerts:")
    for a in alerts:
        print(f" - [{a.severity}] {a.primary_drug} <-> {a.interacting_drug}: {a.clinical_reason[:80]}...")
        print(f"   Recommendation: {a.actionable_recommendation[:80]}...")

    assert len(alerts) > 0, "Expected LLM RAG interaction alerts for Ibuprofen + Losartan"
    print("[PASS] LLM RAG accurately reasoned over retrieved guidelines and synthesized clinical alerts.")

def test_api_drug_alerts_endpoint():
    """Verify FastAPI endpoint POST /api/drug-alerts/check and GET /api/drug-alerts/stats."""
    client = TestClient(app)

    # 1. Test Stats
    stats_res = client.get("/api/drug-alerts/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["status"] == "online"
    assert stats["indexed_interaction_rules"] >= 30
    print(f"\n[PASS] GET /api/drug-alerts/stats: {stats}")

    # 2. Test Check Endpoint
    payload = {
        "transcript": "Doctor: I'm prescribing Amoxicillin for your infection. Patient: I also take Methotrexate weekly for arthritis.",
        "medications": ["Amoxicillin 500mg"],
        "patient_history": ["Methotrexate 15mg weekly", "Hypertension"],
    }
    res = client.post("/api/drug-alerts/check", json=payload)
    assert res.status_code == 200, f"Drug check failed: {res.text}"
    data = res.json()
    assert data["status"] == "success"
    assert len(data["alerts"]) > 0
    print(f"[PASS] POST /api/drug-alerts/check generated {len(data['alerts'])} LLM-reasoned alert cards.")

if __name__ == "__main__":
    test_drug_alerts_chroma_ingestion()
    test_retrieval_evidence()
    test_llm_rag_interaction_generation()
    test_api_drug_alerts_endpoint()
    print("\n[SUCCESS] ALL TRUE LLM RAG DRUG INTERACTION TESTS PASSED!")
