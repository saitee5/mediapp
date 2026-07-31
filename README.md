<div align="center">
  <img src="./public/mediscribe_logo.png" alt="mediScribe Logo" width="300">
  <p><strong>Ambient Clinical Scribe & AI Medical Assistant</strong></p>
  <p><em>Reducing Documentation Burnout Through Ambient Intelligence</em></p>
</div>

**mediScribe** is an automated, AI-driven ambient clinical intelligence system designed to eliminate documentation burnout for physicians. During a patient consultation, the system securely listens, transcribes speech in real time, extracts clinical insights to form structured SOAP notes, cross-references prescriptions with local medical knowledge bases, and automatically packages data for EMR integration — all without the physician touching a keyboard.

## ✨ High-Level Objectives

- **🎙️ Zero-Friction Documentation**: Automate medical charting entirely through ambient listening — no typing, no copy-pasting.
- **🛡️ Clinical Accuracy & Safety**: Leverage specialized medical LLMs and Retrieval-Augmented Generation (RAG) against FDA guidelines to eliminate hallucinations in drug recommendations and flag interactions.
- **⚡ Resource-Efficient Architecture**: Offload heavy compute (Transcription / Inference) to high-speed cloud APIs so the app runs smoothly on standard developer hardware.

## 📄 Automated Documents Generated

| Document | Triggered By | Delivered To |
| :--- | :--- | :--- |
| **Live Transcript** | Real-time during consultation | Physician screen (live view) |
| **SOAP Note** | End of every consultation | EMR / Physician Dashboard |
| **FHIR JSON Payload** | After SOAP note creation | SQLite EMR & export |
| **Drug Interaction Alert** | Medication keyword detected | UI alert card (pre-sign-off) |
| **Patient Visit Summary** | Session termination | Patient portal / printout |
| **Referral Letter** | Specialist mention in transcript | Specialist / external office |
| **Discharge Instructions**| Session termination | Patient (print/digital) |

mediScribe employs a modular, API-first microservices pipeline:

## ⚙️ The Pipeline

1. **Ambient Listening & Chunking**: Frontend captures and chunks audio seamlessly.
2. **High-Speed Transcription**: Audio streams to Groq's LPU infrastructure, returning text in 1-2 seconds.
3. **Clinical Concept Extraction**: LLM identifies symptoms, history, objective findings, and diagnoses.
4. **Safety Check & RAG Routing**: Background listener triggers ChromaDB semantic search for FDA drug interactions.
5. **Structured Charting**: Generates clean professional SOAP note and structured FHIR JSON.
6. **EMR Synchronisation**: Commits payload to the local database and generates post-visit documents.

## 🚀 Quick Start Guide

Launch the mediScribe stack in minutes on any local system using Docker Compose.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- A free API Key from [Groq](https://console.groq.com/) (BYOK - Bring Your Own Key).

### 1. Setup Your Environment

Navigate to the `backend` directory and create your environment file:

```bash
cd backend
cp .env.example .env
```
Add your Groq API Key to the `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
PORT=8000
HOST=0.0.0.0
```

### 2. Launch with Docker Compose

Return to the root directory of the project and start the system:

```bash
cd ..
docker-compose up --build -d
```

### 3. Access mediScribe

- **Frontend Application**: `http://localhost`
- **Backend API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

## 🤝 Contributing

We welcome contributions from developers, doctors, and tech enthusiasts! Whether it's adding new document templates, improving the UI, or optimizing the AI prompts, your help makes mediScribe better for clinics everywhere.

## 📄 License

This project is open-source and available under the MIT License.
