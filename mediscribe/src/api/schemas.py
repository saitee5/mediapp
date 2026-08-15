from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# --- Agent 1: Structured Data Extraction Schema ---

class EncounterDetails(BaseModel):
    date: Optional[str] = Field(default=None, description="Date of the encounter")
    time: Optional[str] = Field(default=None, description="Time of the encounter")
    location_type: Optional[str] = Field(default=None, description="Location type (e.g., telehealth, clinic, ER)")

class Participants(BaseModel):
    patient_name: Optional[str] = Field(default=None, description="Patient name or demographics")
    provider_name: Optional[str] = Field(default=None, description="Provider name and role")

class AdministrativeData(BaseModel):
    encounter_details: EncounterDetails
    participants: Participants

class HPI(BaseModel):
    onset: Optional[str] = Field(default=None, description="When did the symptom start?")
    provocation_palliation: Optional[str] = Field(default=None, description="What makes it better or worse?")
    quality: Optional[str] = Field(default=None, description="How does it feel? (e.g., dull, sharp, burning)")
    region_radiation: Optional[str] = Field(default=None, description="Where is it located? Does it radiate?")
    severity: Optional[str] = Field(default=None, description="How bad is it? (e.g., 6/10)")
    time: Optional[str] = Field(default=None, description="How often does it happen or how long does it last?")

class Subjective(BaseModel):
    chief_complaint: str = Field(description="The primary reason for the visit in the patient's own words.")
    hpi: HPI = Field(description="History of Present Illness")
    past_medical_history: List[str] = Field(default_factory=list, description="Pre-existing conditions mentioned.")
    medications: List[str] = Field(default_factory=list, description="Current prescriptions and over-the-counter drugs.")
    allergies: List[str] = Field(default_factory=list, description="Any mentioned allergies or adverse reactions.")
    social_family_history: List[str] = Field(default_factory=list, description="Smoking, alcohol, occupational hazards, relevant family conditions.")
    review_of_systems: List[str] = Field(default_factory=list, description="Any other symptoms asked about and whether the patient affirmed or denied them.")

class Objective(BaseModel):
    vitals: List[str] = Field(default_factory=list, description="Temperature, blood pressure, heart rate, weight, etc.")
    physical_exam_findings: List[str] = Field(default_factory=list, description="Observations made or dictated by the physician (e.g., lungs clear, mild swelling).")
    diagnostic_results: List[str] = Field(default_factory=list, description="Any rapid labs or imaging results discussed.")

class AssessmentPlan(BaseModel):
    diagnoses: List[str] = Field(default_factory=list, description="Primary and secondary diagnoses or impressions.")
    orders_prescriptions: List[str] = Field(default_factory=list, description="New medications prescribed, dosages, durations.")
    lab_imaging_orders: List[str] = Field(default_factory=list, description="Tests the patient needs to get done.")
    patient_instructions: List[str] = Field(default_factory=list, description="Advice given to the patient regarding care at home, diet, or symptom monitoring.")
    follow_up: Optional[str] = Field(default=None, description="When the patient should return.")

class ClinicalSOAPExtraction(BaseModel):
    administrative_data: AdministrativeData
    subjective: Subjective
    objective: Objective
    assessment_plan: AssessmentPlan

# --- Agent 2: Synthesize Case Sheet / Case Study Summary ---

class PrescriptionItem(BaseModel):
    medicine: str = Field(description="Name of the medicine")
    dosage: str = Field(description="Dosage instructions (e.g., 0-0-1 After Food)")
    duration: str = Field(description="Duration of the medicine (e.g., 3 Days (Tot: 3 TAB))")

class CaseSheetSummary(BaseModel):
    patient_name: str = Field(description="Patient Name")
    gender: str = Field(description="Gender (e.g. Male, Female, Unknown)")
    age: str = Field(description="Age in years, months, days if possible, or just Years")
    patient_no: str = Field(description="A random or generated Patient No.")
    doctor: str = Field(description="Doctor's name")
    date: str = Field(description="Date and time of visit")
    chief_complaints: str = Field(description="Chief complaints summarized")
    vitals: str = Field(description="Vitals formatted nicely (e.g. Pulse: 99 bpm, BP: 135/95 mmHg...)")
    examination_findings: str = Field(description="Summary of examination findings")
    investigations: str = Field(description="Ordered tests or labs (e.g. BMP, MRI...)")
    diagnosis: str = Field(description="Diagnosis")
    prescriptions: List[PrescriptionItem] = Field(default_factory=list, description="List of prescribed medicines")
    treatment_plan: str = Field(description="Summary of treatment plan")
    therapy_description: str = Field(description="Therapy required, or None")
    therapy_result: str = Field(description="Result of therapy, or N/A")
    notes: str = Field(description="Additional clinical notes")
    instructions: str = Field(description="Instructions to the patient (e.g. Avoid sweets, Return in 2 weeks)")

# Alias for CaseSheetSummary
CaseStudySummary = CaseSheetSummary

# --- Agent Pipeline State ---

class AgentState(BaseModel):
    transcription: Optional[str] = None
    soap: Optional[ClinicalSOAPExtraction] = None
    case_sheet_summary: Optional[CaseSheetSummary] = None

# --- 1. Endpoint: Generate Initial Summary ---
class GenerateSummaryRequest(BaseModel):
    transcript: str = Field(..., description="The raw conversation transcript to process.")
    session_id: Optional[str] = Field(None, description="Optional custom session or consultation ID.")
    patient_id: Optional[str] = Field(None, description="Optional patient ID reference.")

class GenerateSummaryResponse(BaseModel):
    session_id: str
    status: str = Field("pending_review", description="Status: pending_review")
    case_study_summary: CaseSheetSummary = Field(..., description="Generated Case Study Summary for frontend review")
    soap: Optional[ClinicalSOAPExtraction] = Field(None, description="Extracted SOAP clinical concepts")
    message: str = "Case study summary generated successfully. Ready for frontend review."

# --- 2. Endpoint: Update / Save Reviewed Summary ---
class UpdateSummaryRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Session ID (if not passed in path)")
    updated_case_study_summary: CaseSheetSummary = Field(..., description="The updated / reviewed Case Study Summary from frontend")

class UpdateSummaryResponse(BaseModel):
    session_id: str
    status: str = "reviewed"
    updated_case_study_summary: CaseSheetSummary
    message: str = "Case study summary successfully updated in database."

# Aliases for backwards-compatibility
ReviewSummaryRequest = UpdateSummaryRequest
ReviewSummaryResponse = UpdateSummaryResponse

# --- 3. Endpoint: Generate & Upload PDF ---
class GeneratePDFRequest(BaseModel):
    session_id: str = Field(..., description="The consultation session ID to generate PDF for")

class GeneratePDFResponse(BaseModel):
    session_id: str
    status: str
    pdf_url: str = Field(..., description="Public URL to the PDF stored in Supabase Storage")
    download_url: str = Field(..., description="Backend endpoint to download the PDF directly")
    message: str = "PDF generated and uploaded successfully."


# --- Consultation Details & Health ---
class ConsultationDetailResponse(BaseModel):
    session_id: str
    status: str
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    doctor_name: Optional[str] = None
    encounter_date: Optional[str] = None
    transcript: Optional[str] = None
    soap: Optional[ClinicalSOAPExtraction] = None
    case_sheet_summary: Optional[CaseSheetSummary] = None
    updated_case_sheet_summary: Optional[CaseSheetSummary] = None
    pdf_url: Optional[str] = Field(None, description="Public Supabase storage URL for PDF")
    download_url: Optional[str] = Field(None, description="Backend download URL")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    llm_configured: bool
    model: str
    supabase_configured: bool
    agent_ready: bool = True
