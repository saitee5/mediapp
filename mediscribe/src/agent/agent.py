import asyncio
from typing import Optional, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from src.api.schemas import (
    ClinicalSOAPExtraction,
    PatientVisitSummary,
    CaseSheetSummary,
    DischargeInstructions,
    ReferralLetter,
    ClinicalDocumentRoutingDecision,
    AgentState,
    DownstreamAgentState,
)
from src.models.llm_client import get_pipeline_llm
from src.utils.logger import logger


# ==============================================================================
# Step 1: Agent Nodes for Structured SOAP Extraction from Raw Transcript
# ==============================================================================

def SOAPExtractionAgent(state: AgentState) -> Dict[str, Any]:
    llm = get_pipeline_llm()
    structured_llm = llm.with_structured_output(ClinicalSOAPExtraction)
    extraction_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert medical AI assistant. Your task is to analyze clinical conversation transcripts "
            "and extract a highly structured JSON schema based on the SOAP framework (Subjective, Objective, "
            "Assessment, and Plan). Be precise, exhaustive, and preserve all clinical specifics."
        ),
        ("human", "Please analyze the following conversation transcript and extract the structured clinical concepts:\n\n{transcript}")
    ])

    chain = extraction_prompt | structured_llm
    logger.info("Agent 1: Extracting structured SOAP data from transcript...")
    transcript = state.transcription if hasattr(state, "transcription") else state.get("transcription", "")
    extracted_data: ClinicalSOAPExtraction = chain.invoke({"transcript": transcript})
    logger.info("Agent 1: Extraction complete.")
    return {"soap": extracted_data}

async def aSOAPExtractionAgent(state: AgentState) -> Dict[str, Any]:
    llm = get_pipeline_llm()
    structured_llm = llm.with_structured_output(ClinicalSOAPExtraction)
    extraction_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert medical AI assistant. Your task is to analyze clinical conversation transcripts "
            "and extract a highly structured JSON schema based on the SOAP framework (Subjective, Objective, "
            "Assessment, and Plan). Be precise, exhaustive, and preserve all clinical specifics."
        ),
        ("human", "Please analyze the following conversation transcript and extract the structured clinical concepts:\n\n{transcript}")
    ])

    chain = extraction_prompt | structured_llm
    logger.info("Agent 1 (Async): Extracting structured SOAP data from transcript...")
    transcript = state.transcription if hasattr(state, "transcription") else state.get("transcription", "")
    extracted_data: ClinicalSOAPExtraction = await asyncio.to_thread(chain.invoke, {"transcript": transcript})
    logger.info("Agent 1 (Async): Extraction complete.")
    return {"soap": extracted_data}


# ==============================================================================
# Step 2: Downstream Multi-Document Generation Nodes (from Verified SOAP)
# ==============================================================================

# --- Node 0: Autonomous Document Needs Classifier (AI-Decided Routing) ---
async def aDocumentNeedsClassifier(state: DownstreamAgentState) -> Dict[str, Any]:
    """AI Classifier that inspects the verified SOAP to decide if Discharge Instructions or Referral Letter are needed."""
    llm = get_pipeline_llm()
    structured_llm = llm.with_structured_output(ClinicalDocumentRoutingDecision)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert clinical triage AI. Your task is to evaluate the provided verified SOAP note and determine document requirements:\n"
            "1. 'needs_discharge_instructions': True if the patient was given new medications/prescriptions, dosage changes, surgical/wound care, or home care guidelines. False if routine check with no new medication changes.\n"
            "2. 'needs_referral_letter': True if the physician ordered or recommended a referral to another specialty, specialist, or external procedure (e.g., Orthopedics, Cardiology, Physical Therapy, Surgery, etc.). False if no specialist referral was made."
        ),
        ("human", "Here is the Verified Clinical SOAP Note (JSON):\n{soap_json}")
    ])

    chain = prompt | structured_llm
    logger.info("Agent (Downstream): Evaluating clinical document needs from SOAP...")
    soap = state.soap if hasattr(state, "soap") else state.get("soap")
    soap_json = soap.model_dump_json() if hasattr(soap, "model_dump_json") else str(soap)

    decision: ClinicalDocumentRoutingDecision = await asyncio.to_thread(chain.invoke, {"soap_json": soap_json})
    logger.info(
        f"Agent (Downstream): Needs evaluation complete -> Discharge={decision.needs_discharge_instructions}, "
        f"Referral={decision.needs_referral_letter}"
    )
    return {
        "needs_discharge_instructions": decision.needs_discharge_instructions,
        "needs_referral_letter": decision.needs_referral_letter,
    }


# --- Node A: Patient Visit Summary (Fixed / Mandatory) ---
async def aPatientVisitSummaryGen(state: DownstreamAgentState) -> Dict[str, Any]:
    """Generates patient-friendly After-Visit Summary in plain 6th-8th grade English."""
    llm = get_pipeline_llm()
    structured_llm = llm.with_structured_output(PatientVisitSummary)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert clinical communication AI. Your task is to generate a Patient Visit Summary "
            "(After-Visit Summary) based on the provided verified SOAP note.\n"
            "Guidelines:\n"
            "1. Write in warm, empathetic, 6th-to-8th grade plain English without confusing medical jargon.\n"
            "2. Translate clinical terms into clear everyday language (e.g., 'high blood pressure' instead of 'hypertension').\n"
            "3. Clearly explain what was examined, what the diagnosis means, how medications work, and step-by-step home action items.\n"
            "4. Include warning symptoms for when the patient should reach out to the clinic.\n"
            "5. Rely strictly on the provided verified SOAP data."
        ),
        ("human", "Here is the Verified Clinical SOAP Note (JSON):\n{soap_json}")
    ])

    chain = prompt | structured_llm
    logger.info("Agent (Downstream): Generating Patient Visit Summary (Fixed)...")
    soap = state.soap if hasattr(state, "soap") else state.get("soap")
    soap_json = soap.model_dump_json() if hasattr(soap, "model_dump_json") else str(soap)

    result: PatientVisitSummary = await asyncio.to_thread(chain.invoke, {"soap_json": soap_json})
    logger.info("Agent (Downstream): Patient Visit Summary generated.")
    return {"patient_visit_summary": result}


# --- Node B: Case Sheet Summary (Conditional - Frontend Decided) ---
async def aCaseSheetSummaryGen(state: DownstreamAgentState) -> Dict[str, Any]:
    """Generates professional hospital EMR Case Sheet Summary."""
    llm = get_pipeline_llm()
    structured_llm = llm.with_structured_output(CaseSheetSummary)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert clinical documentation AI. Your task is to synthesize a professional, "
            "highly structured Clinical Case Sheet Report in the 'CaseSheetSummary' format for hospital EMR "
            "and physician handoff.\n"
            "Rely strictly on the provided verified SOAP data. Fill in all fields with clinical accuracy."
        ),
        ("human", "Here is the Verified Clinical SOAP Note (JSON):\n{soap_json}")
    ])

    chain = prompt | structured_llm
    logger.info("Agent (Downstream): Synthesizing Clinical Case Sheet Summary (Frontend Requested)...")
    soap = state.soap if hasattr(state, "soap") else state.get("soap")
    soap_json = soap.model_dump_json() if hasattr(soap, "model_dump_json") else str(soap)

    result: CaseSheetSummary = await asyncio.to_thread(chain.invoke, {"soap_json": soap_json})
    logger.info("Agent (Downstream): Case Sheet Summary generated.")
    return {"case_sheet_summary": result}


# --- Node C: Discharge Instructions (Conditional - AI Decided) ---
async def aDischargeInstructionsGen(state: DownstreamAgentState) -> Dict[str, Any]:
    """Generates structured Discharge Instructions and Medication Schedule packet."""
    llm = get_pipeline_llm()
    structured_llm = llm.with_structured_output(DischargeInstructions)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert clinical care transition AI. Your task is to generate actionable, comprehensive "
            "Discharge Instructions based on the provided verified SOAP note.\n"
            "Guidelines:\n"
            "1. Build a precise medication schedule table with medicine name, purpose in simple terms, exact schedule, and precautions.\n"
            "2. Detail clear activity, diet, and wound/incision care instructions.\n"
            "3. Explicitly list emergency RED-FLAG warning signs when the patient/caregiver must seek immediate emergency care (call 911 / visit ER).\n"
            "4. Specify follow-up appointments and timelines.\n"
            "5. Rely strictly on the provided verified SOAP data."
        ),
        ("human", "Here is the Verified Clinical SOAP Note (JSON):\n{soap_json}")
    ])

    chain = prompt | structured_llm
    logger.info("Agent (Downstream): Generating Discharge Instructions (AI Decided)...")
    soap = state.soap if hasattr(state, "soap") else state.get("soap")
    soap_json = soap.model_dump_json() if hasattr(soap, "model_dump_json") else str(soap)

    result: DischargeInstructions = await asyncio.to_thread(chain.invoke, {"soap_json": soap_json})
    logger.info("Agent (Downstream): Discharge Instructions generated.")
    return {"discharge_instructions": result}


# --- Node D: Specialist Referral Letter (Conditional - AI Decided) ---
async def aReferralLetterGen(state: DownstreamAgentState) -> Dict[str, Any]:
    """Generates professional Physician-to-Specialist Referral Letter."""
    llm = get_pipeline_llm()
    structured_llm = llm.with_structured_output(ReferralLetter)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert medical communication AI. Your task is to generate a formal, professional "
            "Physician-to-Specialist Referral Letter based on the provided verified SOAP note.\n"
            "Guidelines:\n"
            "1. Identify the target specialty/department from the SOAP assessment/plan (e.g. Orthopedics, Cardiology, Physical Therapy, Nephrology).\n"
            "2. Clearly state the primary reason for referral and clinical question for the specialist.\n"
            "3. Include relevant clinical history, exam observations, diagnostic labs, active medications, and allergies.\n"
            "4. Write in formal clinical correspondence format between medical colleagues.\n"
            "5. Rely strictly on the provided verified SOAP data."
        ),
        ("human", "Here is the Verified Clinical SOAP Note (JSON):\n{soap_json}")
    ])

    chain = prompt | structured_llm
    logger.info("Agent (Downstream): Generating Specialist Referral Letter (AI Decided)...")
    soap = state.soap if hasattr(state, "soap") else state.get("soap")
    soap_json = soap.model_dump_json() if hasattr(soap, "model_dump_json") else str(soap)

    result: ReferralLetter = await asyncio.to_thread(chain.invoke, {"soap_json": soap_json})
    logger.info("Agent (Downstream): Referral Letter generated.")
    return {"referral_letter": result}


# ==============================================================================
# Conditional Routing Functions for Downstream LangGraph
# ==============================================================================

def route_after_patient_summary(state: DownstreamAgentState) -> str:
    gen_case_sheet = state.generate_case_sheet if hasattr(state, "generate_case_sheet") else state.get("generate_case_sheet", True)
    needs_discharge = state.needs_discharge_instructions if hasattr(state, "needs_discharge_instructions") else state.get("needs_discharge_instructions", False)
    needs_referral = state.needs_referral_letter if hasattr(state, "needs_referral_letter") else state.get("needs_referral_letter", False)

    if gen_case_sheet:
        return "case_sheet_gen"
    if needs_discharge:
        return "discharge_instructions_gen"
    if needs_referral:
        return "referral_letter_gen"
    return END

def route_after_case_sheet(state: DownstreamAgentState) -> str:
    needs_discharge = state.needs_discharge_instructions if hasattr(state, "needs_discharge_instructions") else state.get("needs_discharge_instructions", False)
    needs_referral = state.needs_referral_letter if hasattr(state, "needs_referral_letter") else state.get("needs_referral_letter", False)

    if needs_discharge:
        return "discharge_instructions_gen"
    if needs_referral:
        return "referral_letter_gen"
    return END

def route_after_discharge(state: DownstreamAgentState) -> str:
    needs_referral = state.needs_referral_letter if hasattr(state, "needs_referral_letter") else state.get("needs_referral_letter", False)

    if needs_referral:
        return "referral_letter_gen"
    return END


# ==============================================================================
# StateGraphs Assembly
# ==============================================================================

# --- Pipeline 1: Extraction Graph ---
extraction_graph = StateGraph(AgentState)
extraction_graph.add_node("soap_extractor", aSOAPExtractionAgent)
extraction_graph.add_edge(START, "soap_extractor")
extraction_graph.add_edge("soap_extractor", END)
compiled_extraction_pipeline = extraction_graph.compile()

# --- Pipeline 2: Downstream Multi-Document Generation Graph with AI Autonomous Decisions ---
downstream_graph = StateGraph(DownstreamAgentState)
downstream_graph.add_node("document_needs_classifier", aDocumentNeedsClassifier)
downstream_graph.add_node("patient_summary_gen", aPatientVisitSummaryGen)
downstream_graph.add_node("case_sheet_gen", aCaseSheetSummaryGen)
downstream_graph.add_node("discharge_instructions_gen", aDischargeInstructionsGen)
downstream_graph.add_node("referral_letter_gen", aReferralLetterGen)

# Entry point: Classifier evaluates SOAP -> Patient Summary is ALWAYS generated
downstream_graph.add_edge(START, "document_needs_classifier")
downstream_graph.add_edge("document_needs_classifier", "patient_summary_gen")

# Conditional Edge 1: From Patient Summary -> Case Sheet OR Discharge OR Referral OR END
downstream_graph.add_conditional_edges(
    "patient_summary_gen",
    route_after_patient_summary,
    {
        "case_sheet_gen": "case_sheet_gen",
        "discharge_instructions_gen": "discharge_instructions_gen",
        "referral_letter_gen": "referral_letter_gen",
        END: END,
    },
)

# Conditional Edge 2: From Case Sheet -> Discharge OR Referral OR END
downstream_graph.add_conditional_edges(
    "case_sheet_gen",
    route_after_case_sheet,
    {
        "discharge_instructions_gen": "discharge_instructions_gen",
        "referral_letter_gen": "referral_letter_gen",
        END: END,
    },
)

# Conditional Edge 3: From Discharge -> Referral OR END
downstream_graph.add_conditional_edges(
    "discharge_instructions_gen",
    route_after_discharge,
    {
        "referral_letter_gen": "referral_letter_gen",
        END: END,
    },
)

# Terminal Edge: Referral Letter -> END
downstream_graph.add_edge("referral_letter_gen", END)

compiled_downstream_pipeline = downstream_graph.compile()


# ==============================================================================
# High-Level Service Class
# ==============================================================================

class MediScribeAgent:
    """AI Agent interface for MediScribe extraction and downstream document generation."""

    def __init__(self):
        self.extraction_pipeline = compiled_extraction_pipeline
        self.downstream_pipeline = compiled_downstream_pipeline

    async def extract_soap(self, transcript: str) -> ClinicalSOAPExtraction:
        """Runs Step 1: Extracts structured SOAP from transcript for doctor review."""
        initial_state = AgentState(transcription=transcript)
        result = await self.extraction_pipeline.ainvoke(initial_state)
        soap_data = result.get("soap")
        if not soap_data:
            raise RuntimeError("Agent extraction pipeline failed to produce structured SOAP data.")
        return soap_data

    async def generate_documents(
        self,
        soap: ClinicalSOAPExtraction,
        generate_case_sheet: bool = True,
    ) -> Dict[str, Any]:
        """
        Runs Step 2: Generates Patient Summary (fixed) + Case Sheet (frontend flag).
        Discharge Instructions and Referral Letter are autonomously decided by the AI from the SOAP.
        """
        initial_state = DownstreamAgentState(
            soap=soap,
            generate_case_sheet=generate_case_sheet,
        )
        result = await self.downstream_pipeline.ainvoke(initial_state)
        return result

    # Backwards compatibility helper
    async def generate_summary(self, transcript: str) -> Dict[str, Any]:
        """Legacy helper: extracts SOAP and generates documents."""
        soap = await self.extract_soap(transcript)
        docs = await self.generate_documents(soap, generate_case_sheet=True)
        return {
            "soap": soap,
            "case_sheet_summary": docs.get("case_sheet_summary"),
            "patient_visit_summary": docs.get("patient_visit_summary"),
        }

agent = MediScribeAgent()