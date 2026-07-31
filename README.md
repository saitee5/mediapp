# 🏥 MedOS: The Open Source Medical Operating System

![MedOS Banner](https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80)

**MedOS** is a cutting-edge, open-source medical operating system designed for modern daily clinics. It empowers medical professionals by automating administrative burdens, extracting structured clinical concepts from doctor-patient conversations in real-time, and generating flawless Case Sheet Summaries instantly. 

Bring the power of advanced AI right into your clinic—without the exorbitant costs of proprietary software!

## ✨ Features

- **🎙️ Real-time Audio Transcription**: Powered by Groq's Whisper API, capturing every detail of the patient encounter instantly.
- **🧠 Clinical Concept Extraction**: Advanced AI automatically identifies symptoms, diagnoses, medications, and treatment plans using the SOAP framework.
- **📝 Intelligent Patient Summaries**: Generates a structured, editable Patient Summary Report immediately after the consultation.
- **⚠️ RAG-Based Clinical Alerts**: Integrates a Retrieval-Augmented Generation (RAG) system to cross-reference prescribed medications with medical knowledge bases, instantly alerting the doctor to potential drug interactions or contraindications.
- **📄 Instant PDF Generation**: Export professional, standardized case sheets with a single click.
- **🔒 Bring Your Own Key (BYOK)**: Full control over your AI usage and data. Plug in your own Groq API key and you're ready to go!
- **🚀 One-Click Local Deployment**: Run the entire system locally on your own hardware using Docker, keeping your patient data secure.

## 🚀 Quick Start Guide

You can launch the entire MedOS stack in minutes on any local system using Docker Compose.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine.
- A free API Key from [Groq](https://console.groq.com/).

### 1. Setup Your Environment (BYOK)

Navigate to the `backend` directory and create your environment file:

```bash
cd backend
cp .env.example .env
```

Open the `.env` file and insert your Groq API Key:

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

### 3. Access MedOS

- **Frontend Application**: Open your browser and go to `http://localhost`
- **Backend API**: Accessible at `http://localhost:8000`
- **API Documentation (Swagger)**: Explore the API endpoints at `http://localhost:8000/docs`

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS
- **Backend**: Python, FastAPI, WebSockets
- **AI / LLMs**: Groq (Whisper-large-v3-turbo, Llama-3.3-70b-versatile)
- **Data Schemas**: Pydantic

## 🤝 Contributing

We welcome contributions from developers, doctors, and tech enthusiasts! Whether it's adding new document templates, improving the UI, or optimizing the AI prompts, your help makes MedOS better for clinics everywhere.

## 📄 License

This project is open-source and available under the MIT License.
