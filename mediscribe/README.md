# MediScribe - AI Clinical Agent (Powered by LangGraph)

MediScribe is an AI-powered clinical documentation and consultation assistant built on **LangGraph**. It processes real-time consultation audio via WebSockets using Groq Whisper (`whisper-large-v3-turbo`), orchestrates multi-step clinical reasoning (`extract_soap` -> `clinical_validation` -> `synthesize_case_sheet` -> `audit_case_sheet`) via LangGraph StateGraphs, and provides interactive clinical decision support with tool calling.

---

## 📁 Project Structure

```
mediscribe/
├── README.md                      # Project overview, setup, usage, and examples
├── requirements.txt               # List of Python dependencies (LangGraph, LangChain, Groq)
├── .env                           # Environment variables and API keys
├── .gitignore                     # Git ignore rules
├── docker-compose.yml             # Container orchestration
├── Dockerfile                     # Container definition
├── main.py                        # Entry point to run FastAPI / Agent Server
│
├── src/                           # Source code for the AI Agent
│   ├── agent/                     # LangGraph workflow, state, nodes, and executor
│   │   ├── __init__.py
│   │   ├── agent.py               # Main MediScribeAgent interface
│   │   ├── executor.py            # LangGraph StateGraph pipeline executor
│   │   ├── graph.py               # LangGraph StateGraph definitions & compilation
│   │   ├── nodes.py               # Discrete LangGraph node execution functions
│   │   ├── state.py               # ClinicalState & InteractiveAgentState schemas
│   │   └── memory.py              # LangGraph MemorySaver checkpointer & session manager
│   │
│   ├── tools/                     # LangChain tool definitions with @tool wrappers
│   │   ├── __init__.py
│   │   ├── search.py              # Medical knowledge base search tool
│   │   ├── calculator.py          # Clinical dosage & math calculation tool
│   │   └── weather.py             # Contextual environment lookup tool
│   │
│   ├── models/                    # LLM clients & configuration
│   │   ├── __init__.py
│   │   ├── llm_client.py          # ChatGroq & AsyncGroq client manager
│   │   └── embeddings.py          # Embedding models
│   │
│   ├── prompts/                   # System & agent prompt templates
│   │   ├── __init__.py
│   │   ├── system_prompts.py      # SOAP & Case Sheet system prompts
│   │   └── agent_prompts.py       # User and task prompt formatters
│   │
│   ├── utils/                     # Helpers, logging, configuration
│   │   ├── __init__.py
│   │   ├── config.py              # Centralized environment configuration
│   │   ├── logger.py              # Logger setup (console + file)
│   │   └── helpers.py             # Audio buffer and latency helpers
│   │
│   └── api/                       # API layer exposing agent (FastAPI)
│       ├── __init__.py
│       ├── routes.py              # Endpoints & WebSocket handler
│       └── schemas.py             # Pydantic data schemas
│
├── tests/                         # Unit tests, graph tests, integration tests
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_graph.py              # LangGraph StateGraph workflow & node tests
│   ├── test_tools.py
│   └── test_api.py
│
├── data/                          # Sample data & evaluation datasets
│   ├── examples.json
│   └── knowledge_base/
│
└── logs/                          # Log files for debugging and monitoring
    └── .gitkeep
```

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.10+
- Groq API Key

### 2. Setup Environment
```bash
# Clone or navigate to the mediscribe folder
cd mediscribe

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure `.env`
Create a `.env` file from `.env.example`:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
PORT=8000
HOST=0.0.0.0
```

### 4. Run the Agent Server
```bash
python main.py
```
API Documentation will be available at: `http://localhost:8000/docs`

---

## 📡 Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health and model status check |
| `POST` | `/api/generate-summary` | Generate SOAP + Case Sheet from raw transcript |
| `POST` | `/api/agent/query` | Interactive query endpoint with tool routing |
| `WS` | `/api/ws/transcribe` | Real-time audio chunk transcription over WebSocket |

---

## 🧪 Running Tests

```bash
pytest tests/
```
