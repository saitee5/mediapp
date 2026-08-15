# MediScribe Backend - AI Clinical Agent & API

MediScribe Backend is an AI-powered clinical intelligence and documentation pipeline built with **FastAPI**, **LangGraph**, and **Supabase**. It transforms raw doctor-patient conversation transcripts into structured clinical **SOAP notes** and professional **Case Sheet Summaries**, allows doctors to review and update records, and automatically generates formatted PDF reports uploaded directly to Supabase Storage.

---

## 🏗️ Architecture & Pipeline

The backend orchestrates a 2-agent LangGraph workflow:

```mermaid
flowchart TD
    A[Raw Consultation Transcript] --> B[Agent 1: SOAPExtractionAgent]
    B -->|Structured Clinical SOAP Data| C[Agent 2: CaseSheetSummaryGen]
    C -->|Synthesized Case Study Summary| D[(Supabase Database)]
    D -->|Initial State: pending_review| E[Frontend Doctor Review]
    E -->|Updated / Validated Summary| F[(Supabase Database - status: reviewed)]
    F --> G[CaseSheetPDF Generator]
    G --> H[(Supabase Storage Bucket: case-sheets)]
    H --> I[Public PDF URL & Download Endpoint]
```

1. **Agent 1 (`SOAPExtractionAgent`)**: Extracts structured clinical concepts (`EncounterDetails`, `Participants`, `HPI`, `Subjective`, `Objective`, `AssessmentPlan`) using structured LLM outputs.
2. **Agent 2 (`CaseSheetSummaryGen`)**: Synthesizes the clinical data into a formatted `CaseSheetSummary` (Patient demographics, vitals, chief complaints, examination findings, diagnosis, prescription table, treatment plan, therapy, and instructions).
3. **Database & Storage (`Supabase`)**: Stores consultation transcripts, SOAP extractions, and case summaries, and stores generated hospital PDFs in the `case-sheets` storage bucket.
4. **PDF Generator (`CaseSheetPDF`)**: Generates clean, multi-page hospital summary sheets with patient demographics, prescription tables, and clinic headers (on page 1).

---

## 📁 Project Structure

```
mediscribe/
├── main.py                             # FastAPI application entry point with CORS & Swagger UI
├── requirements.txt                    # Python dependencies
├── supabase_schema.sql                 # Supabase PostgreSQL DDL migration & Storage setup
├── .env.example                        # Example environment variables
│
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   └── agent.py                    # 2-Agent LangGraph StateGraph pipeline
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                   # Unified FastAPI REST endpoints
│   │   └── schemas.py                  # Pydantic data schemas & API contracts
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── llm_client.py               # Vertex AI / Google GenAI / Groq LLM client factory
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── supabase_service.py         # Supabase CRUD operations, Storage bucket & memory fallback
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py                   # Centralized configuration & environment loader
│       ├── logger.py                   # Structured logger
│       └── pdf_generator.py            # FPDF2 clinical Case Sheet PDF generator
│
└── tests/
    ├── __init__.py
    └── test_pipeline_and_endpoints.py  # End-to-end automated test suite
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Google Cloud Vertex AI credentials / API Key (or Groq API key)
- Supabase Project URL and API Key

### 2. Installation

```bash
# Navigate to backend directory
cd mediscribe

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Supabase Database & Storage
In your [Supabase Dashboard](https://supabase.com/dashboard) SQL Editor, execute the contents of [`supabase_schema.sql`](file:///c:/Users/anshy/Documents/mediapp/mediscribe/supabase_schema.sql):
- Creates `public.consultations` table with JSONB fields and indexes.
- Configures Row Level Security (RLS).
- Creates public `case-sheets` storage bucket for PDF files.

### 4. Configure Environment Variables
Create a `.env` file in `mediscribe/`:

```env
# LLM Provider
DEFAULT_LLM_MODEL=gemini-2.5-flash
GROQ_API_KEY=your_groq_api_key_if_using_groq

# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key
SUPABASE_STORAGE_BUCKET=case-sheets

# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=True
```

### 5. Run the Server
```bash
python main.py
```

- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 📡 API Endpoints

### 1. `POST /api/generate-summary`
Takes raw doctor-patient conversation text and generates the initial Case Study Summary.
- **Request Body**:
  ```json
  {
    "transcript": "Doctor and patient conversation text...",
    "session_id": "consultation_001",
    "patient_id": "PAT-102"
  }
  ```
- **Response**: Returns `session_id`, `status: "pending_review"`, `case_study_summary`, and `soap`.

### 2. `POST /api/update-summary`
Updates the consultation record with the doctor's reviewed/edited Case Study Summary.
- **Request Body**:
  ```json
  {
    "session_id": "consultation_001",
    "updated_case_study_summary": { ... }
  }
  ```
- **Response**: Returns `session_id`, `status: "reviewed"`, and `updated_case_study_summary`.

### 3. `POST /api/generate-pdf`
Generates the hospital PDF from the stored summary and uploads it to Supabase Storage.
- **Request Body**:
  ```json
  {
    "session_id": "consultation_001"
  }
  ```
- **Response**:
  ```json
  {
    "session_id": "consultation_001",
    "status": "reviewed",
    "pdf_url": "https://<supabase-id>.supabase.co/storage/v1/object/public/case-sheets/...",
    "download_url": "http://localhost:8000/api/consultation/consultation_001/download-pdf",
    "message": "PDF generated and uploaded to Supabase Storage successfully."
  }
  ```

### 4. `GET /api/consultation/{session_id}/download-pdf`
Downloads the clinical PDF directly as a file attachment (`Content-Disposition: attachment`).

### 5. `GET /api/consultation/{session_id}/pdf`
Streams the PDF inline for direct browser viewing.

### 6. `GET /api/consultation/{session_id}`
Retrieves the complete consultation record, SOAP data, and summaries.

### 7. `GET /api/consultations`
Lists past consultations stored in the database.

---

## 🧪 Running Tests

Run the automated integration test suite:

```bash
python tests/test_pipeline_and_endpoints.py
```
