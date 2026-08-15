from typing import Optional, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from src.api.schemas import (
    ClinicalSOAPExtraction,
    CaseSheetSummary,
    AgentState,
)
from src.models.llm_client import get_pipeline_llm
from src.utils.logger import logger

# LLM instance configured for structured output
llm = get_pipeline_llm()

# --- Exact Agent Nodes (from main_pipeline_demo.ipynb) ---

def SOAPExtractionAgent(state: AgentState):
    structured_llm = llm.with_structured_output(ClinicalSOAPExtraction)
    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert medical AI assistant. Your task is to analyze clinical conversation transcripts and extract a highly structured JSON schema based on the SOAP framework."),
        ("human", "Please analyze the following conversation transcript and extract the structured clinical concepts:\n\n{transcript}")
    ])

    agent_1_chain = extraction_prompt | structured_llm
    
    logger.info("Agent 1: Extracting structured SOAP data...")
    transcript = state.transcription if hasattr(state, "transcription") else state.get("transcription", "")
    extracted_data: ClinicalSOAPExtraction = agent_1_chain.invoke({"transcript": transcript})
    logger.info("Extraction complete.")
    
    return {"soap": extracted_data}

async def aSOAPExtractionAgent(state: AgentState):
    structured_llm = llm.with_structured_output(ClinicalSOAPExtraction)
    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert medical AI assistant. Your task is to analyze clinical conversation transcripts and extract a highly structured JSON schema based on the SOAP framework."),
        ("human", "Please analyze the following conversation transcript and extract the structured clinical concepts:\n\n{transcript}")
    ])

    agent_1_chain = extraction_prompt | structured_llm
    
    logger.info("Agent 1 (Async): Extracting structured SOAP data...")
    transcript = state.transcription if hasattr(state, "transcription") else state.get("transcription", "")
    extracted_data: ClinicalSOAPExtraction = await agent_1_chain.ainvoke({"transcript": transcript})
    logger.info("Extraction complete.")
    
    return {"soap": extracted_data}

def CaseSheetSummaryGen(state: AgentState):
    final_structured_llm = llm.with_structured_output(CaseSheetSummary)
    
    final_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert clinical documentation AI. Your task is to generate a Patient Summary Report in a highly specific JSON format called 'CaseSheetSummary'.\n"
                   "Rely on the provided JSON schema (SOAP data) for all clinical facts and structured data. "
                   "Use the attached raw transcript ONLY to extract direct quotes, verify tone, or clarify ambiguities.\n"
                   "Fill in all fields. If a field is missing, infer a sensible default or write 'N/A'."),
        ("human", "Here is the Structured Data (JSON):\n{json_data}\n\nHere is the Raw Transcript:\n{transcript}")
    ])
    agent_2_chain = final_prompt | final_structured_llm
    
    logger.info("Agent 2: Synthesizing Case Sheet Summary...")
    transcript = state.transcription if hasattr(state, "transcription") else state.get("transcription", "")
    soap = state.soap if hasattr(state, "soap") else state.get("soap")
    json_data = soap.model_dump_json() if hasattr(soap, "model_dump_json") else str(soap)
    
    case_sheet_data: CaseSheetSummary = agent_2_chain.invoke({
        "json_data": json_data,
        "transcript": transcript
    })
    logger.info("Case Sheet Summary generated.")
    return {"case_sheet_summary": case_sheet_data}

async def aCaseSheetSummaryGen(state: AgentState):
    final_structured_llm = llm.with_structured_output(CaseSheetSummary)
    
    final_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert clinical documentation AI. Your task is to generate a Patient Summary Report in a highly specific JSON format called 'CaseSheetSummary'.\n"
                   "Rely on the provided JSON schema (SOAP data) for all clinical facts and structured data. "
                   "Use the attached raw transcript ONLY to extract direct quotes, verify tone, or clarify ambiguities.\n"
                   "Fill in all fields. If a field is missing, infer a sensible default or write 'N/A'."),
        ("human", "Here is the Structured Data (JSON):\n{json_data}\n\nHere is the Raw Transcript:\n{transcript}")
    ])
    agent_2_chain = final_prompt | final_structured_llm
    
    logger.info("Agent 2 (Async): Synthesizing Case Sheet Summary...")
    transcript = state.transcription if hasattr(state, "transcription") else state.get("transcription", "")
    soap = state.soap if hasattr(state, "soap") else state.get("soap")
    json_data = soap.model_dump_json() if hasattr(soap, "model_dump_json") else str(soap)
    
    case_sheet_data: CaseSheetSummary = await agent_2_chain.ainvoke({
        "json_data": json_data,
        "transcript": transcript
    })
    logger.info("Case Sheet Summary generated.")
    return {"case_sheet_summary": case_sheet_data}

# --- StateGraph Assembly ---

graph = StateGraph(AgentState)
graph.add_node("SOAP_extractor_agent", aSOAPExtractionAgent)
graph.add_node("Case_sheet_gen_agent", aCaseSheetSummaryGen)
graph.add_edge(START, "SOAP_extractor_agent")
graph.add_edge("SOAP_extractor_agent", "Case_sheet_gen_agent")
graph.add_edge("Case_sheet_gen_agent", END)

compiled = graph.compile()

class MediScribeAgent:
    """High-level AI Agent interface for MediScribe pipeline."""
    def __init__(self):
        self.pipeline = compiled

    async def generate_summary(self, transcript: str) -> Dict[str, Any]:
        """Runs the 2-agent LangGraph pipeline and returns soap + case_sheet_summary."""
        initial_state = AgentState(transcription=transcript)
        result = await self.pipeline.ainvoke(initial_state)
        return result

agent = MediScribeAgent()