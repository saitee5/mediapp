import os
import json
import re
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import chromadb
from langchain_core.prompts import ChatPromptTemplate

from src.utils.logger import logger
from src.utils.config import settings
from src.models.llm_client import LLMClientManager
from src.drug_alerts.schemas import (
    DrugAlertItem,
    DrugAlertLLMResponse,
    DrugAlertCheckResponse,
)

CURRENT_DIR = Path(__file__).resolve().parent
JSONL_PATH = CURRENT_DIR / "interactions.jsonl"
CHROMA_PERSIST_DIR = settings.DATA_PATH / "chroma_drug_alerts"

RAG_SYSTEM_PROMPT = """You are a Senior Clinical Pharmacologist and Clinical Decision Support (CDS) Agent.
Your job is to analyze a patient encounter against RETRIEVED CLINICAL KNOWLEDGE BASE GUIDELINES and detect potential:
1. Adverse Drug-Drug Interactions (DDIs)
2. Drug-Disease / Condition Contraindications
3. Dangerous Co-prescriptions and Inappropriate Combinations

CRITICAL INSTRUCTIONS:
- Ground your analysis strictly in the provided RETRIEVED CLINICAL KNOWLEDGE EVIDENCE.
- Check both newly prescribed medications and existing patient active medications/history.
- For each genuine interaction/contraindication identified, output a structured DrugAlertItem:
  * severity: Assign 'CRITICAL' (life-threatening/fatal arrhythmias/serotonin syndrome/rhabdomyolysis/lactic acidosis), 'HIGH' (bleeding/ulceration/acute kidney injury/hyperkalemia), or 'MODERATE' (absorption chelation/spacing).
  * primary_drug: The primary medication involved.
  * interacting_drug: The colliding drug, substance, or contraindicated condition.
  * category: Therapeutic classification.
  * clinical_reason: Precise adverse physiological mechanism.
  * actionable_recommendation: Clear, practical guidance for the doctor (e.g. switch to alternative agent, adjust dose, space out timing by 4 hours, monitor renal function/potassium).
  * evidence_text: The relevant supporting clinical guideline snippet.
- If there are NO dangerous drug interactions or contraindications present in the encounter, return an empty alerts list.
"""

RAG_USER_PROMPT = """RETRIEVED CLINICAL KNOWLEDGE BASE EVIDENCE:
--------------------------------------------------------------------------------
{retrieved_evidence}
--------------------------------------------------------------------------------

PATIENT ENCOUNTER DATA:
--------------------------------------------------------------------------------
- Dialogue Transcript:
{transcript}

- Active & Prescribed Medications:
{medications}

- Patient Allergies & Chronic Medical History:
{patient_history}
--------------------------------------------------------------------------------

Analyze the patient encounter against the retrieved clinical evidence and generate structured drug interaction alerts."""


class DrugAlertRAGService:
    """
    RAG-powered Drug-Drug Interaction and Contraindication Alert Service.
    1. Retrieval: ChromaDB vector search retrieves relevant interaction rules.
    2. Augmentation: Injects retrieved guidelines + patient clinical dialogue into prompt.
    3. Generation: LLM (Gemini 2.5 Flash / Groq) synthesizes grounded, structured clinical alert cards.
    """

    def __init__(self):
        self.collection_name = "drug_interactions"
        self.client = None
        self.collection = None
        self.known_drugs: Set[str] = set()
        self._load_vocabulary_from_jsonl()
        self._init_chroma()

    def _load_vocabulary_from_jsonl(self):
        """Loads vocabulary from interactions.jsonl for preliminary entity hints."""
        if not JSONL_PATH.exists():
            return
        try:
            with open(JSONL_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    raw_strings = [row.get("primary_medicine", "")] + row.get("avoid_with", [])
                    for raw in raw_strings:
                        tokens = re.split(r"[/,();]", raw)
                        for token in tokens:
                            clean = token.strip().lower()
                            clean_core = re.sub(r"^(other|certain|oral|topical|strong|non-selective|containing)\s+", "", clean).strip()
                            if len(clean_core) >= 3:
                                self.known_drugs.add(clean_core)
            logger.info(f"DrugAlert RAG: Loaded {len(self.known_drugs)} unique drug entities for retrieval hints.")
        except Exception as e:
            logger.error(f"Error loading vocabulary from {JSONL_PATH}: {e}")

    def _init_chroma(self):
        """Initializes persistent ChromaDB client and auto-ingests interactions dataset."""
        try:
            CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            count = self.collection.count()
            logger.info(f"DrugAlert RAG: ChromaDB collection '{self.collection_name}' initialized with {count} records.")

            if count < 25 and JSONL_PATH.exists():
                self._ingest_dataset()
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB for DrugAlerts: {e}")
            self.collection = None

    def _ingest_dataset(self):
        """Ingests interactions.jsonl dataset into ChromaDB."""
        if not JSONL_PATH.exists():
            logger.warning(f"Interactions dataset not found at {JSONL_PATH}")
            return

        rows = []
        with open(JSONL_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))

        ids = []
        docs = []
        metas = []

        for row in rows:
            ids.append(row["id"])
            docs.append(row["text"])
            avoid_list = row.get("avoid_with", [])
            meta = {
                "doc_type": "drug_interaction",
                "chunk_id": row["id"],
                "category": row["category"],
                "primary_medicine": row["primary_medicine"].lower(),
                "clinical_reason": row["clinical_reason"],
                "avoid_with": ", ".join(avoid_list).lower(),
                "n_avoid_drugs": len(avoid_list),
            }
            for drug in avoid_list:
                clean_name = re.sub(r"[^a-z0-9]", "_", drug.lower())[:50]
                meta[f"has_{clean_name}"] = True

            metas.append(meta)

        self.collection.upsert(
            ids=ids,
            documents=docs,
            metadatas=metas,
        )
        logger.info(f"Successfully ingested {len(rows)} drug interaction rules into ChromaDB vector store.")

    def get_collection_count(self) -> int:
        if self.collection:
            return self.collection.count()
        return 0

    def extract_drugs_from_text(self, text: str) -> List[str]:
        """Extracts candidate medication mentions from text for vector retrieval queries."""
        if not text:
            return []
        found = set()
        clean_text = text.lower()
        for drug in self.known_drugs:
            pattern = r"\b" + re.escape(drug) + r"\b"
            if re.search(pattern, clean_text):
                found.add(drug)
        return sorted(list(found))

    def retrieve_relevant_guidelines(
        self,
        transcript: Optional[str] = None,
        medications: Optional[List[str]] = None,
        patient_history: Optional[List[str]] = None,
        n_results: int = 6,
    ) -> Tuple[List[str], str]:
        """
        Step 1 (Retrieval): Queries ChromaDB for clinical interaction evidence
        relevant to the patient's dialogue, medications, and medical history.
        """
        if not self.collection:
            self._init_chroma()
            if not self.collection:
                return [], "No vector database available."

        # Collect search query strings
        search_terms = []
        if medications:
            search_terms.extend(medications)
        if patient_history:
            search_terms.extend(patient_history)
        if transcript:
            extracted = self.extract_drugs_from_text(transcript)
            search_terms.extend(extracted)
            # Add short dialogue excerpt
            search_terms.append(transcript[:200])

        if not search_terms:
            search_terms = ["common clinical drug interactions and contraindications"]

        query_text = " ; ".join(search_terms[:10])
        logger.info(f"DrugAlert RAG: Querying ChromaDB with text: '{query_text[:90]}...'")

        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=min(n_results, self.get_collection_count() or 6),
            )
            documents = results.get("documents", [[]])[0]
            ids = results.get("ids", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]

            formatted_snippets = []
            for doc_id, meta, doc in zip(ids, metadatas, documents):
                formatted_snippets.append(
                    f"[{doc_id}] ({meta.get('category', 'General')}): {doc}"
                )

            evidence_text = "\n\n".join(formatted_snippets)
            return documents, evidence_text

        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return [], "Error retrieving evidence."

    async def check_interactions(
        self,
        transcript: Optional[str] = None,
        medications: Optional[List[str]] = None,
        patient_history: Optional[List[str]] = None,
    ) -> DrugAlertCheckResponse:
        """
        Full RAG Pipeline (Retrieval + Augmentation + LLM Generation):
        1. Retrieves relevant interaction guidelines from ChromaDB.
        2. Injects retrieved evidence and patient encounter into prompt.
        3. Calls LLM with structured output to reason over clinical risks and generate alerts.
        """
        raw_docs, retrieved_evidence = self.retrieve_relevant_guidelines(
            transcript=transcript,
            medications=medications,
            patient_history=patient_history,
            n_results=6,
        )

        formatted_transcript = transcript or "None provided"
        formatted_meds = ", ".join(medications) if medications else "None provided"
        formatted_history = ", ".join(patient_history) if patient_history else "None provided"

        # Initialize LLM with structured schema output
        llm = LLMClientManager.get_pipeline_llm(temperature=0.0)
        structured_llm = llm.with_structured_output(DrugAlertLLMResponse)

        prompt = ChatPromptTemplate.from_messages([
            ("system", RAG_SYSTEM_PROMPT),
            ("user", RAG_USER_PROMPT),
        ])

        chain = prompt | structured_llm

        input_data = {
            "retrieved_evidence": retrieved_evidence,
            "transcript": formatted_transcript,
            "medications": formatted_meds,
            "patient_history": formatted_history,
        }

        try:
            logger.info("DrugAlert RAG: Invoking LLM generation over retrieved evidence...")
            # Thread-pinned async execution
            llm_result: DrugAlertLLMResponse = await asyncio.to_thread(chain.invoke, input_data)
            
            alerts = llm_result.alerts if llm_result and llm_result.alerts else []
            detected_meds = llm_result.detected_medications if llm_result and llm_result.detected_medications else []

            # Severity ordering: CRITICAL -> HIGH -> MODERATE -> LOW
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3}
            sorted_alerts = sorted(alerts, key=lambda x: severity_order.get(x.severity, 4))
            has_critical = any(a.severity in ("CRITICAL", "HIGH") for a in sorted_alerts)

            logger.info(f"DrugAlert RAG: LLM generated {len(sorted_alerts)} validated clinical alerts.")

            return DrugAlertCheckResponse(
                status="success",
                detected_medications=detected_meds,
                total_alerts=len(sorted_alerts),
                has_critical_alerts=has_critical,
                alerts=sorted_alerts,
                message=f"RAG scan complete. Identified {len(sorted_alerts)} validated interaction alerts.",
            )

        except Exception as e:
            logger.error(f"Error in DrugAlert RAG LLM generation: {e}")
            # Graceful rule-based fallback if LLM call fails
            return self._rule_based_fallback(transcript, medications, patient_history, raw_docs)

    def _rule_based_fallback(
        self,
        transcript: Optional[str],
        medications: Optional[List[str]],
        patient_history: Optional[List[str]],
        raw_docs: List[str],
    ) -> DrugAlertCheckResponse:
        """Fallback in case of LLM outage."""
        detected = self.extract_drugs_from_text(
            f"{transcript or ''} {' '.join(medications or [])} {' '.join(patient_history or [])}"
        )
        alerts = []
        if ("ibuprofen" in detected or "naproxen" in detected) and ("losartan" in detected or "amlodipine" in detected):
            alerts.append(DrugAlertItem(
                alert_id="alert_fb_01",
                severity="HIGH",
                primary_drug="Ibuprofen",
                interacting_drug="Losartan",
                category="Pain & Cardiovascular",
                clinical_reason="NSAIDs blunt the antihypertensive effect of ARBs and increase acute kidney injury risk.",
                actionable_recommendation="Substitute with Paracetamol for analgesia; monitor renal function and BP.",
                evidence_text=raw_docs[0] if raw_docs else None,
                match_type="rag_rule_fallback",
            ))
        return DrugAlertCheckResponse(
            status="fallback",
            detected_medications=detected,
            total_alerts=len(alerts),
            has_critical_alerts=len(alerts) > 0,
            alerts=alerts,
            message="RAG fallback scan complete.",
        )


drug_alert_service = DrugAlertRAGService()
