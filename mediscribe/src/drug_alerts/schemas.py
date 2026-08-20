from typing import List, Optional
from pydantic import BaseModel, Field

class DrugAlertItem(BaseModel):
    """Structured clinical drug-drug interaction or contraindication alert card."""
    alert_id: str = Field(..., description="Unique alert identifier")
    severity: str = Field(..., description="Alert severity: CRITICAL, HIGH, MODERATE, LOW")
    primary_drug: str = Field(..., description="Primary identified medication")
    interacting_drug: str = Field(..., description="Interacting medication or contraindication substance")
    category: str = Field(..., description="Therapeutic drug category")
    clinical_reason: str = Field(..., description="Adverse physiological mechanism and risk")
    actionable_recommendation: str = Field(..., description="Actionable clinical guidance for provider")
    evidence_text: Optional[str] = Field(None, description="Clinical knowledge base reference snippet")
    match_type: str = Field("rag_llm_synthesized", description="Match method: rag_llm_synthesized or exact_metadata")


class DrugAlertLLMResponse(BaseModel):
    """Structured LLM response for RAG reasoning over retrieved knowledge base documents."""
    detected_medications: List[str] = Field(default_factory=list, description="All pharmaceutical substances and medications identified in the encounter")
    alerts: List[DrugAlertItem] = Field(default_factory=list, description="List of validated clinical drug interaction alerts grounded in retrieved evidence")


class DrugAlertCheckRequest(BaseModel):
    """Request payload to scan for drug interactions."""
    transcript: Optional[str] = Field(None, description="Consultation dialogue or doctor notes")
    medications: Optional[List[str]] = Field(None, description="Explicit list of active or newly prescribed medications")
    patient_history: Optional[List[str]] = Field(None, description="Known patient allergies and chronic medical conditions")
    session_id: Optional[str] = Field(None, description="Optional consultation session ID to fetch existing records")


class DrugAlertCheckResponse(BaseModel):
    """Response containing detected medications and RAG-retrieved drug alerts."""
    status: str = Field("success", description="Scan execution status")
    detected_medications: List[str] = Field(default_factory=list, description="All medications detected from input")
    total_alerts: int = Field(0, description="Total count of triggered interaction alerts")
    has_critical_alerts: bool = Field(False, description="True if any CRITICAL or HIGH severity alerts were detected")
    alerts: List[DrugAlertItem] = Field(default_factory=list, description="List of structured drug alert cards")
    message: str = Field("Drug interaction scan completed.", description="Status message")
