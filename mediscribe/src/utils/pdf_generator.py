import io
from typing import Optional
from fpdf import FPDF
from src.api.schemas import CaseSheetSummary
from src.utils.logger import logger

class CaseSheetPDF(FPDF):
    """
    FPDF subclass reproducing the exact clinical Case Sheet layout.
    Clinic header is rendered only once on the first page.
    """
    def header(self):
        # Hospital Header should ONLY appear once on the first page
        if self.page_no() == 1:
            self.set_font('helvetica', 'B', 16)
            self.cell(0, 8, 'EZOVION MULTI SPECIALTY HOSPITAL', align='C', new_x="LMARGIN", new_y="NEXT")
            self.set_font('helvetica', '', 10)
            self.cell(0, 6, 'Chennai - 600044', align='C', new_x="LMARGIN", new_y="NEXT")
            self.ln(6)
            
            # Title
            self.set_font('helvetica', 'BU', 14)
            self.cell(0, 10, 'Case Sheet Summary', align='C', new_x="LMARGIN", new_y="NEXT")
            self.ln(2)
            
            # Simulate Barcode
            self.set_font('courier', '', 14)
            self.cell(0, 10, '||| |||| || |||||||| ||||', align='C', new_x="LMARGIN", new_y="NEXT")
            self.ln(4)

    def footer(self):
        # Clean page number footer
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
        self.set_text_color(0, 0, 0)

    def draw_section_line(self):
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)


def generate_case_sheet_pdf(data: CaseSheetSummary, output_filename: Optional[str] = None) -> bytes:
    """
    Generates a formatted PDF for a CaseSheetSummary.
    Returns the generated PDF as raw bytes (and optionally writes to file).
    """
    pdf = CaseSheetPDF()
    pdf.add_page()

    # Patient Details Grid
    y_before = pdf.get_y()
    
    # Left Column
    pdf.set_font('helvetica', '', 10)
    pdf.cell(25, 6, 'Name', new_x="RIGHT")
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(75, 6, str(data.patient_name or "N/A"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font('helvetica', '', 10)
    pdf.cell(25, 6, 'Gender', new_x="RIGHT")
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(75, 6, str(data.gender or "N/A"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font('helvetica', '', 10)
    pdf.cell(25, 6, 'Age', new_x="RIGHT")
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(75, 6, str(data.age or "N/A"), new_x="RIGHT")

    # Right Column
    pdf.set_xy(120, y_before)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(25, 6, 'Patient No.', new_x="RIGHT")
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 6, str(data.patient_no or "N/A"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_xy(120, y_before + 6)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(25, 6, 'Doctor', new_x="RIGHT")
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 6, str(data.doctor or "N/A"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_xy(120, y_before + 12)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(25, 6, 'Date', new_x="RIGHT")
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 6, str(data.date or "N/A"), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.draw_section_line()

    # Helper for label: value
    def add_field(label: str, value: Optional[str]):
        display_val = str(value or "N/A")
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(pdf.get_string_width(label) + 2, 8, label, new_x="RIGHT")
        pdf.set_font('helvetica', '', 10)
        pdf.multi_cell(0, 8, display_val, new_x="LMARGIN", new_y="NEXT")
        pdf.draw_section_line()

    add_field('Chief Complaints :', data.chief_complaints)
    add_field('Vitals :', data.vitals)
    add_field('Examination : Findings :', data.examination_findings)
    add_field('Investigation :', data.investigations)
    add_field('Diagnosis :', data.diagnosis)

    # Prescription Section
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 8, 'Prescription :', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    
    # Table Header
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(10, 8, '#', new_x="RIGHT")
    pdf.cell(80, 8, 'Medicine', new_x="RIGHT")
    pdf.cell(50, 8, 'Dosage', new_x="RIGHT")
    pdf.cell(0, 8, 'Duration', new_x="LMARGIN", new_y="NEXT")

    # Table Rows
    pdf.set_font('helvetica', '', 10)
    prescriptions = data.prescriptions or []
    if prescriptions:
        for idx, p in enumerate(prescriptions, 1):
            pdf.cell(10, 8, str(idx), new_x="RIGHT")
            pdf.cell(80, 8, str(p.medicine), new_x="RIGHT")
            pdf.cell(50, 8, str(p.dosage), new_x="RIGHT")
            pdf.cell(0, 8, str(p.duration), new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 8, 'No prescriptions recorded.', new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(2)
    pdf.draw_section_line()

    add_field('Treatment Plan :', data.treatment_plan)

    # Therapy Section
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 8, 'Therapy', new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(100, 8, 'Description', new_x="RIGHT")
    pdf.cell(0, 8, 'Result', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('helvetica', '', 10)
    pdf.cell(100, 8, str(data.therapy_description or "None"), new_x="RIGHT")
    pdf.cell(0, 8, str(data.therapy_result or "N/A"), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 8, 'Notes', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 10)
    pdf.multi_cell(0, 8, str(data.notes or "None"), new_x="LMARGIN", new_y="NEXT")
    pdf.draw_section_line()

    add_field('Instructions :', data.instructions)

    if output_filename:
        pdf.output(output_filename)
        logger.info(f"PDF saved to file: {output_filename}")

    # Output as raw bytes
    pdf_bytes = bytes(pdf.output())
    return pdf_bytes
