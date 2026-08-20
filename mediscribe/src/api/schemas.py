from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# ==============================================================================
# 1. Agent 1: Structured SOAP Data Extraction Schema
# ==============================================================================

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
    follow_up: Optional[str] = Field(default=None, description="When the patient should return or specialty referrals.")

class ClinicalSOAPExtraction(BaseModel):
    administrative_data: AdministrativeData
    subjective: Subjective
    objective: Objective
    assessment_plan: AssessmentPlan


# ==============================================================================
# 2. Document 1: Patient Visit Summary (After-Visit Summary / AVS) - Fixed
# ==============================================================================

class PatientVisitSummary(BaseModel):
    patient_name: Optional[str] = Field(default=None, description="Patient full name")
    doctor_name: Optional[str] = Field(default=None, description="Attending physician name")
    visit_date: Optional[str] = Field(default=None, description="Date and time of visit")
    reason_for_visit: str = Field(description="Summary of why the patient visited in plain, empathetic language")
    what_was_found: List[str] = Field(description="Key observations, vital checks, and findings in plain, non-jargon language")
    diagnoses_explained: str = Field(description="Clear explanation of the diagnosis at a 6th-8th grade reading level")
    medications_and_treatments: List[str] = Field(description="List of prescribed medicines with simple instructions and purpose")
    home_action_plan: List[str] = Field(description="Clear, actionable steps the patient should follow at home (diet, activity, rest)")
    warning_signs_to_call_doctor: List[str] = Field(description="Symptoms that require contacting the doctor or clinic")
    follow_up_instructions: str = Field(description="When and where the patient should return for follow-up")


# ==============================================================================
# 3. Document 2: Clinical Case Sheet Summary (Hospital / EMR) - Frontend Flag
# ==============================================================================

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

CaseStudySummary = CaseSheetSummary


# ==============================================================================
# 4. Document 3: Discharge Instructions (Discharge Packet) - AI Decided
# ==============================================================================

class DischargeMedicationItem(BaseModel):
    medicine: str = Field(description="Name and strength of the medication")
    purpose: str = Field(description="Why this medication was prescribed in simple terms")
    how_to_take: str = Field(description="Exact schedule and instructions (e.g., 1 tablet twice daily with meals)")
    duration: str = Field(description="How long to take it")
    precautions: Optional[str] = Field(None, description="Special instructions, precautions, or side effects to watch for")

class DischargeInstructions(BaseModel):
    patient_name: Optional[str] = Field(default=None, description="Patient name")
    discharge_date: Optional[str] = Field(default=None, description="Date of discharge")
    attending_physician: Optional[str] = Field(default=None, description="Supervising physician")
    discharge_diagnosis: str = Field(description="Primary diagnosis at time of discharge")
    medication_schedule: List[DischargeMedicationItem] = Field(default_factory=list, description="List of discharge medications with instructions")
    activity_and_diet_restrictions: List[str] = Field(default_factory=list, description="Clear restrictions on physical activity, lifting, driving, and diet")
    wound_and_site_care: Optional[str] = Field(None, description="Wound, incision, or post-procedure hygiene instructions")
    emergency_red_flags: List[str] = Field(default_factory=list, description="Critical red-flag symptoms requiring immediate 911 / emergency room care")
    follow_up_appointments: str = Field(description="Scheduled follow-up dates, locations, and contact information")


# ==============================================================================
# 5. Document 4: Clinical Referral Letter (Specialist Referral) - AI Decided
# ==============================================================================

class ReferralLetter(BaseModel):
    patient_name: str = Field(description="Patient Name")
    patient_age_gender: str = Field(description="Age and Gender (e.g., 58 y/o Male)")
    patient_id: Optional[str] = Field(default="N/A", description="Patient Identification Number")
    referring_doctor: str = Field(description="Name and credentials of the referring physician")
    referral_date: str = Field(description="Date of the referral letter")
    target_specialist_or_department: str = Field(description="Specialty or specialist name (e.g., Department of Orthopedics, Cardiology, Physical Therapy)")
    reason_for_referral: str = Field(description="Primary clinical reason for specialist evaluation or procedure")
    clinical_history: str = Field(description="Concise summary of history of present illness and relevant past medical conditions")
    examination_and_diagnostics: str = Field(description="Key physical exam observations, vitals, and relevant lab/imaging findings")
    current_medications_and_allergies: str = Field(description="Active prescriptions and known patient allergies")
    clinical_question_and_requested_actions: str = Field(description="Specific evaluation, intervention, or management recommendations requested from the specialist")


# ==============================================================================
# 6. Autonomous Routing Decision Model
# ==============================================================================

class ClinicalDocumentRoutingDecision(BaseModel):
    needs_discharge_instructions: bool = Field(
        description="True if the patient was given new medications, post-op instructions, wound care, or care transition guidelines; False if routine check with no new med changes."
    )
    needs_referral_letter: bool = Field(
        description="True if the clinician referred the patient to an outside specialist, department, or procedure (e.g. Orthopedics, Cardiology, PT, Surgery); False otherwise."
    )
    reasoning: Optional[str] = Field(default=None, description="Brief clinical rationale for the document generation decisions")


# ==============================================================================
# 7. Pipeline State Models
# ==============================================================================

class AgentState(BaseModel):
    """State for initial extraction pass."""
    transcription: Optional[str] = None
    soap: Optional[ClinicalSOAPExtraction] = None

class DownstreamAgentState(BaseModel):
    """State for downstream multi-document generation pass from verified SOAP."""
    soap: Optional[ClinicalSOAPExtraction] = None
    generate_case_sheet: bool = True  # Frontend decides this
    needs_discharge_instructions: bool = False  # AI autonomously decides this
    needs_referral_letter: bool = False  # AI autonomously decides this
    patient_visit_summary: Optional[PatientVisitSummary] = None
    case_sheet_summary: Optional[CaseSheetSummary] = None
    discharge_instructions: Optional[DischargeInstructions] = None
    referral_letter: Optional[ReferralLetter] = None


# ==============================================================================
# 8. Request & Response API Models
# ==============================================================================

# --- Step 1: Extract SOAP for Doctor Review ---
class ExtractSOAPRequest(BaseModel):
    transcript: str = Field(..., description="The raw conversation transcript to process.")
    session_id: Optional[str] = Field(None, description="Optional custom session or consultation ID.")
    patient_id: Optional[str] = Field(None, description="Optional patient ID reference.")

class ExtractSOAPResponse(BaseModel):
    session_id: str
    status: str = Field("pending_review", description="Status: pending_review")
    soap: ClinicalSOAPExtraction = Field(..., description="Extracted structured SOAP note for physician review")
    message: str = "Clinical SOAP extracted successfully. Ready for physician review."

# Aliases for backwards compatibility
GenerateSummaryRequest = ExtractSOAPRequest
GenerateSummaryResponse = ExtractSOAPResponse


# --- Step 2: Generate Downstream Documents from Verified SOAP ---
class GenerateDocumentsRequest(BaseModel):
    session_id: str = Field(..., description="The consultation session ID.")
    verified_soap: ClinicalSOAPExtraction = Field(..., description="The verified / edited SOAP note confirmed by the physician.")
    generate_case_sheet: bool = Field(True, description="Whether to generate the Clinical Case Sheet Summary (Hospital/EMR).")

class GenerateDocumentsResponse(BaseModel):
    session_id: str
    status: str = Field("completed", description="Status: completed")
    patient_visit_summary: PatientVisitSummary = Field(..., description="Patient-facing After-Visit Summary (Fixed)")
    case_sheet_summary: Optional[CaseSheetSummary] = Field(None, description="Clinical Case Sheet (Frontend Decided)")
    discharge_instructions: Optional[DischargeInstructions] = Field(None, description="Discharge Instructions (AI Decided)")
    referral_letter: Optional[ReferralLetter] = Field(None, description="Specialist Referral Letter (AI Decided)")
    message: str = "Clinical documents generated successfully from verified SOAP."

# Aliases for backwards compatibility
ReviewSummaryRequest = GenerateDocumentsRequest
ReviewSummaryResponse = GenerateDocumentsResponse


# --- Step 3: PDF Generation Models ---
class GeneratedPDFItem(BaseModel):
    document_type: str = Field(description="'case_sheet_summary' | 'patient_visit_summary' | 'discharge_instructions' | 'referral_letter'")
    title: str
    filename: str
    pdf_url: str
    download_url: str

class GeneratePDFRequest(BaseModel):
    session_id: str = Field(..., description="The consultation session ID")
    document_type: Optional[str] = Field("all", description="'all' or specific document ('case_sheet', 'patient_summary', 'discharge', 'referral')")

class GeneratePDFResponse(BaseModel):
    session_id: str
    patient_id: str = Field(default="patient_general", description="Patient identifier used for partitioned storage")
    status: str = "completed"
    pdf_url: str = Field(description="Primary PDF URL")
    download_url: str = Field(description="Primary direct download URL")
    pdf_urls: Dict[str, str] = Field(default_factory=dict, description="Map of document types to Supabase public PDF URLs")
    download_urls: Dict[str, str] = Field(default_factory=dict, description="Map of document types to backend download URLs")
    generated_pdfs: List[GeneratedPDFItem] = Field(default_factory=list, description="List of generated PDF items")
    message: str = "PDFs generated and stored per patient in Supabase Storage successfully."


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
    patient_visit_summary: Optional[PatientVisitSummary] = None
    case_sheet_summary: Optional[CaseSheetSummary] = None
    discharge_instructions: Optional[DischargeInstructions] = None
    referral_letter: Optional[ReferralLetter] = None
    pdf_url: Optional[str] = None
    pdf_urls: Optional[Dict[str, str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    llm_configured: bool
    model: str
    supabase_configured: bool
    agent_ready: bool = True
