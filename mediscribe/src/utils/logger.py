import logging
import sys
from pathlib import Path
from .config import settings

def setup_logger(name: str = "MediScribe", log_file: str = "mediscribe.log") -> logging.Logger:
    """Configures and returns a logger instance with console and file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Stream Handler (stdout)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        # File Handler
        try:
            settings.LOGS_PATH.mkdir(parents=True, exist_ok=True)
            file_path = settings.LOGS_PATH / log_file
            file_handler = logging.FileHandler(file_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            pass  # Fallback to console only if file access fails

    return logger

logger = setup_logger()
