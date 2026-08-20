import io
import re
from typing import Optional, Dict, Any, List
from fpdf import FPDF
from src.api.schemas import (
    CaseSheetSummary,
    PatientVisitSummary,
    DischargeInstructions,
    ReferralLetter,
)
from src.utils.logger import logger

def sanitize_pdf_text(text: Optional[str]) -> str:
    """Replaces Unicode characters not supported by standard FPDF helvetica font."""
    if not text:
        return ""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "--",
        "\u2022": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2028": "\n",
        "\u2029": "\n",
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    # Remove any remaining non-latin-1 characters
    return text.encode("latin-1", "replace").decode("latin-1")


class HospitalPDF(FPDF):
    """
    Standard hospital FPDF subclass with header, barcode, patient info grid,
    and footer.
    """
    def __init__(self, doc_title: str = "Clinical Document", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.doc_title = doc_title

    def header(self):
        # Header rendered only on the first page
        if self.page_no() == 1:
            self.set_font('helvetica', 'B', 15)
            self.cell(0, 8, 'EZOVION MULTI SPECIALTY HOSPITAL', align='C', new_x="LMARGIN", new_y="NEXT")
            self.set_font('helvetica', '', 9)
            self.cell(0, 5, 'Chennai - 600044 | Contact: +91 44 2200 8800', align='C', new_x="LMARGIN", new_y="NEXT")
            self.ln(3)

            # Document Title
            self.set_font('helvetica', 'BU', 13)
            self.cell(0, 8, sanitize_pdf_text(self.doc_title), align='C', new_x="LMARGIN", new_y="NEXT")
            self.ln(1)

            # Simulated Barcode
            self.set_font('courier', '', 12)
            self.cell(0, 6, '||| |||| || |||||||| ||||', align='C', new_x="LMARGIN", new_y="NEXT")
            self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 10, f'Page {self.page_no()} | EZOVION Healthcare System - Confidential Medical Record', align='C')
        self.set_text_color(0, 0, 0)

    def draw_section_line(self):
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)

    def add_patient_grid(
        self,
        name: Optional[str] = "N/A",
        gender: Optional[str] = "N/A",
        age: Optional[str] = "N/A",
        patient_no: Optional[str] = "N/A",
        doctor: Optional[str] = "N/A",
        date: Optional[str] = "N/A",
    ):
        y_before = self.get_y()

        # Left Column
        self.set_font('helvetica', '', 9)
        self.cell(24, 5, 'Patient Name', new_x="RIGHT")
        self.set_font('helvetica', 'B', 9)
        self.cell(70, 5, sanitize_pdf_text(name or "N/A"), new_x="LMARGIN", new_y="NEXT")

        self.set_font('helvetica', '', 9)
        self.cell(24, 5, 'Gender', new_x="RIGHT")
        self.set_font('helvetica', 'B', 9)
        self.cell(70, 5, sanitize_pdf_text(gender or "N/A"), new_x="LMARGIN", new_y="NEXT")

        self.set_font('helvetica', '', 9)
        self.cell(24, 5, 'Age', new_x="RIGHT")
        self.set_font('helvetica', 'B', 9)
        self.cell(70, 5, sanitize_pdf_text(age or "N/A"), new_x="RIGHT")

        # Right Column
        self.set_xy(115, y_before)
        self.set_font('helvetica', '', 9)
        self.cell(24, 5, 'Patient No.', new_x="RIGHT")
        self.set_font('helvetica', 'B', 9)
        self.cell(0, 5, sanitize_pdf_text(patient_no or "N/A"), new_x="LMARGIN", new_y="NEXT")

        self.set_xy(115, y_before + 5)
        self.set_font('helvetica', '', 9)
        self.cell(24, 5, 'Attending Dr.', new_x="RIGHT")
        self.set_font('helvetica', 'B', 9)
        self.cell(0, 5, sanitize_pdf_text(doctor or "N/A"), new_x="LMARGIN", new_y="NEXT")

        self.set_xy(115, y_before + 10)
        self.set_font('helvetica', '', 9)
        self.cell(24, 5, 'Date', new_x="RIGHT")
        self.set_font('helvetica', 'B', 9)
        self.cell(0, 5, sanitize_pdf_text(date or "N/A"), new_x="LMARGIN", new_y="NEXT")

        self.ln(3)
        self.draw_section_line()

    def add_section_field(self, label: str, value: Optional[str]):
        clean_val = sanitize_pdf_text(str(value or "N/A"))
        self.set_font('helvetica', 'B', 9)
        self.cell(self.get_string_width(label) + 2, 6, label, new_x="RIGHT")
        self.set_font('helvetica', '', 9)
        self.multi_cell(0, 6, clean_val, new_x="LMARGIN", new_y="NEXT")
        self.draw_section_line()

    def add_bullet_list(self, label: str, items: List[str]):
        self.set_font('helvetica', 'B', 9)
        self.cell(0, 6, label, new_x="LMARGIN", new_y="NEXT")
        self.set_font('helvetica', '', 9)
        if items:
            for item in items:
                self.cell(6, 5, "-", align="R", new_x="RIGHT")
                self.multi_cell(0, 5, sanitize_pdf_text(item), new_x="LMARGIN", new_y="NEXT")
        else:
            self.cell(0, 5, "None specified.", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
        self.draw_section_line()


# ==============================================================================
# 1. Case Sheet Summary PDF Generator
# ==============================================================================

def generate_case_sheet_pdf(data: CaseSheetSummary, output_filename: Optional[str] = None) -> bytes:
    pdf = HospitalPDF(doc_title="Clinical Case Sheet Summary")
    pdf.add_page()
    pdf.add_patient_grid(
        name=data.patient_name,
        gender=data.gender,
        age=data.age,
        patient_no=data.patient_no,
        doctor=data.doctor,
        date=data.date,
    )

    pdf.add_section_field('Chief Complaints :', data.chief_complaints)
    pdf.add_section_field('Vitals :', data.vitals)
    pdf.add_section_field('Examination Findings :', data.examination_findings)
    pdf.add_section_field('Investigation / Labs :', data.investigations)
    pdf.add_section_field('Diagnosis :', data.diagnosis)

    # Prescription Section Table
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(0, 6, 'Prescription :', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(10, 6, '#', new_x="RIGHT")
    pdf.cell(80, 6, 'Medicine', new_x="RIGHT")
    pdf.cell(50, 6, 'Dosage', new_x="RIGHT")
    pdf.cell(0, 6, 'Duration', new_x="LMARGIN", new_y="NEXT")

    pdf.set_font('helvetica', '', 9)
    prescriptions = data.prescriptions or []
    if prescriptions:
        for idx, p in enumerate(prescriptions, 1):
            pdf.cell(10, 6, str(idx), new_x="RIGHT")
            pdf.cell(80, 6, sanitize_pdf_text(p.medicine), new_x="RIGHT")
            pdf.cell(50, 6, sanitize_pdf_text(p.dosage), new_x="RIGHT")
            pdf.cell(0, 6, sanitize_pdf_text(p.duration), new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, 'No prescriptions recorded.', new_x="LMARGIN", new_y="NEXT")

    pdf.ln(1)
    pdf.draw_section_line()

    pdf.add_section_field('Treatment Plan :', data.treatment_plan)

    # Therapy Section
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(0, 6, 'Therapy / Procedure :', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(100, 6, 'Description', new_x="RIGHT")
    pdf.cell(0, 6, 'Result', new_x="LMARGIN", new_y="NEXT")

    pdf.set_font('helvetica', '', 9)
    pdf.cell(100, 6, sanitize_pdf_text(data.therapy_description or "None"), new_x="RIGHT")
    pdf.cell(0, 6, sanitize_pdf_text(data.therapy_result or "N/A"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.draw_section_line()

    pdf.add_section_field('Clinical Notes :', data.notes)
    pdf.add_section_field('Instructions :', data.instructions)

    if output_filename:
        pdf.output(output_filename)

    return bytes(pdf.output())


# ==============================================================================
# 2. Patient Visit Summary PDF Generator (After-Visit Summary / AVS)
# ==============================================================================

def generate_patient_summary_pdf(data: PatientVisitSummary, output_filename: Optional[str] = None) -> bytes:
    pdf = HospitalPDF(doc_title="Patient Visit Summary (After-Visit Care Report)")
    pdf.add_page()
    pdf.add_patient_grid(
        name=data.patient_name,
        doctor=data.doctor_name,
        date=data.visit_date,
    )

    pdf.add_section_field('Reason for Visit :', data.reason_for_visit)
    pdf.add_bullet_list('What We Found & Checked Today :', data.what_was_found)
    pdf.add_section_field('Your Diagnosis Explained :', data.diagnoses_explained)
    pdf.add_bullet_list('Prescribed Medications & Treatment :', data.medications_and_treatments)
    pdf.add_bullet_list('Your Action Plan at Home :', data.home_action_plan)

    # Warning Box
    pdf.set_fill_color(254, 242, 242)
    pdf.set_draw_color(239, 68, 68)
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(0, 6, ' Warning Signs to Contact the Doctor Immediately:', fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 9)
    for w in data.warning_signs_to_call_doctor or ["Persistent worsening pain or unexpected dizziness"]:
        pdf.cell(6, 5, "-", align="R", new_x="RIGHT")
        pdf.multi_cell(0, 5, sanitize_pdf_text(w), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.draw_section_line()

    pdf.add_section_field('Follow-up Instructions :', data.follow_up_instructions)

    if output_filename:
        pdf.output(output_filename)

    return bytes(pdf.output())


# ==============================================================================
# 3. Discharge Instructions PDF Generator (Discharge Packet)
# ==============================================================================

def generate_discharge_instructions_pdf(data: DischargeInstructions, output_filename: Optional[str] = None) -> bytes:
    pdf = HospitalPDF(doc_title="Patient Discharge Instructions & Care Plan")
    pdf.add_page()
    pdf.add_patient_grid(
        name=data.patient_name,
        doctor=data.attending_physician,
        date=data.discharge_date,
    )

    pdf.add_section_field('Discharge Diagnosis :', data.discharge_diagnosis)

    # Medication Schedule Table
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(0, 6, 'Discharge Medication Schedule :', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(50, 6, 'Medicine', new_x="RIGHT")
    pdf.cell(55, 6, 'Purpose', new_x="RIGHT")
    pdf.cell(50, 6, 'Schedule & How to Take', new_x="RIGHT")
    pdf.cell(0, 6, 'Duration', new_x="LMARGIN", new_y="NEXT")

    pdf.set_font('helvetica', '', 8)
    meds = data.medication_schedule or []
    if meds:
        for m in meds:
            pdf.cell(50, 6, sanitize_pdf_text(m.medicine), new_x="RIGHT")
            pdf.cell(55, 6, sanitize_pdf_text(m.purpose), new_x="RIGHT")
            pdf.cell(50, 6, sanitize_pdf_text(m.how_to_take), new_x="RIGHT")
            pdf.cell(0, 6, sanitize_pdf_text(m.duration), new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 6, 'No discharge medications ordered.', new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.draw_section_line()

    pdf.add_bullet_list('Activity, Lifting & Dietary Restrictions :', data.activity_and_diet_restrictions)
    if data.wound_and_site_care:
        pdf.add_section_field('Wound & Incision Care :', data.wound_and_site_care)

    # Emergency Red Flags Callout Box
    pdf.set_fill_color(255, 237, 213)
    pdf.set_draw_color(249, 115, 22)
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(0, 6, ' EMERGENCY RED-FLAG WARNING SIGNS (Call 911 / Seek Immediate ER Care):', fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 9)
    for flag in data.emergency_red_flags or ["Severe sudden chest pain", "Difficulty breathing", "Uncontrolled bleeding"]:
        pdf.cell(6, 5, "-", align="R", new_x="RIGHT")
        pdf.multi_cell(0, 5, sanitize_pdf_text(flag), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.draw_section_line()

    pdf.add_section_field('Follow-up Appointments :', data.follow_up_appointments)

    if output_filename:
        pdf.output(output_filename)

    return bytes(pdf.output())


# ==============================================================================
# 4. Specialist Referral Letter PDF Generator
# ==============================================================================

def generate_referral_letter_pdf(data: ReferralLetter, output_filename: Optional[str] = None) -> bytes:
    pdf = HospitalPDF(doc_title="Clinical Consultation & Referral Letter")
    pdf.add_page()

    # Referring Doctor & Specialist Target Header
    y_before = pdf.get_y()
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(28, 5, 'To (Specialist):', new_x="RIGHT")
    pdf.set_font('helvetica', '', 9)
    pdf.cell(70, 5, sanitize_pdf_text(data.target_specialist_or_department), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(28, 5, 'From (Doctor):', new_x="RIGHT")
    pdf.set_font('helvetica', '', 9)
    pdf.cell(70, 5, sanitize_pdf_text(data.referring_doctor), new_x="LMARGIN", new_y="NEXT")

    pdf.set_xy(115, y_before)
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(25, 5, 'Referral Date:', new_x="RIGHT")
    pdf.set_font('helvetica', '', 9)
    pdf.cell(0, 5, sanitize_pdf_text(data.referral_date), new_x="LMARGIN", new_y="NEXT")

    pdf.set_xy(115, y_before + 5)
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(25, 5, 'Patient ID:', new_x="RIGHT")
    pdf.set_font('helvetica', '', 9)
    pdf.cell(0, 5, sanitize_pdf_text(data.patient_id or "N/A"), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.draw_section_line()

    pdf.add_section_field('Patient Information :', f"{data.patient_name} ({data.patient_age_gender})")
    pdf.add_section_field('Primary Reason for Referral :', data.reason_for_referral)
    pdf.add_section_field('Clinical History & Background :', data.clinical_history)
    pdf.add_section_field('Exam Observations & Diagnostic Findings :', data.examination_and_diagnostics)
    pdf.add_section_field('Current Medications & Allergies :', data.current_medications_and_allergies)
    pdf.add_section_field('Requested Evaluation & Actions :', data.clinical_question_and_requested_actions)

    # Signature line
    pdf.ln(8)
    pdf.set_font('helvetica', '', 9)
    pdf.cell(0, 5, f"Sincerely,", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(0, 5, sanitize_pdf_text(data.referring_doctor), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', 'I', 8)
    pdf.cell(0, 5, "Attending Physician | EZOVION Multi Specialty Hospital", new_x="LMARGIN", new_y="NEXT")

    if output_filename:
        pdf.output(output_filename)

    return bytes(pdf.output())
