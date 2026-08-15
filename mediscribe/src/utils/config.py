import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory paths
SRC_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = SRC_DIR.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Load environment variables
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

    # API Keys & Auth
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Supabase configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "case-sheets")


    # LLM & Audio Models
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gemini-2.5-flash")
    DEFAULT_VERTEX_LOCATION: str = os.getenv("DEFAULT_VERTEX_LOCATION", "global")
    DEFAULT_WHISPER_MODEL: str = os.getenv("DEFAULT_WHISPER_MODEL", "whisper-large-v3-turbo")
    DEFAULT_EMBEDDING_MODEL: str = os.getenv("DEFAULT_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Audio & Transcription settings
    DEFAULT_AUDIO_FORMAT: str = "webm"
    DEFAULT_LANGUAGE: str = "en"

    # Paths
    BASE_PATH: Path = BASE_DIR
    DATA_PATH: Path = DATA_DIR
    LOGS_PATH: Path = LOGS_DIR

settings = Settings()

