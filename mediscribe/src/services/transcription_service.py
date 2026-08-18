import io
import time
import asyncio
from typing import Optional, Dict, Any, Tuple
from groq import AsyncGroq, Groq
from src.utils.config import settings
from src.utils.logger import logger

class GroqTranscriptionService:
    """
    Real-time audio speech-to-text service using Groq Whisper models
    (whisper-large-v3-turbo / whisper-large-v3 / distil-whisper-large-v3-en).
    """

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.DEFAULT_WHISPER_MODEL or "whisper-large-v3-turbo"
        self.client: Optional[AsyncGroq] = None
        self._sync_client: Optional[Groq] = None
        self._init_client()

    def _init_client(self):
        if self.api_key:
            try:
                self.client = AsyncGroq(api_key=self.api_key)
                self._sync_client = Groq(api_key=self.api_key)
                logger.info(f"Groq Whisper STT service initialized successfully with model '{self.model}'.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq STT client: {e}")
                self.client = None
                self._sync_client = None
        else:
            logger.warning("GROQ_API_KEY is not configured in environment. STT service unavailable.")

    def is_configured(self) -> bool:
        return self.client is not None

    async def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.webm",
        mime_type: str = "audio/webm",
        language: str = "en",
        prompt: Optional[str] = "Medical consultation conversation between doctor and patient.",
    ) -> Tuple[str, int]:
        """
        Transcribes raw audio bytes using Groq Whisper.
        Returns: (transcribed_text, latency_in_milliseconds)
        """
        if not self.client:
            raise RuntimeError("Groq STT client is not initialized. Please verify GROQ_API_KEY in .env.")

        if not audio_bytes or len(audio_bytes) < 100:
            # Chunk too small / empty silence
            return "", 0

        start_time = time.perf_counter()
        
        try:
            # Prepare in-memory file tuple for Groq SDK: (filename, bytes, content_type)
            file_tuple = (filename, audio_bytes, mime_type)

            transcription = await self.client.audio.transcriptions.create(
                file=file_tuple,
                model=self.model,
                language=language,
                prompt=prompt,
                response_format="json",
                temperature=0.0,
            )

            latency_ms = int((time.perf_counter() - start_time) * 1000)
            text = (transcription.text or "").strip()
            
            # Filter out common hallucinated filler tokens from silent/empty segments
            filtered_text = self._filter_whisper_hallucinations(text)
            if filtered_text:
                logger.info(f"Groq STT ({latency_ms}ms): '{filtered_text[:60]}...'")
            
            return filtered_text, latency_ms

        except Exception as e:
            logger.error(f"Groq Whisper transcription error: {e}")
            raise

    def _filter_whisper_hallucinations(self, text: str) -> str:
        """Filters out repetitive silent Whisper artifacts like '[Music]', 'Thank you.', etc."""
        if not text:
            return ""
        
        hallucinations = {
            "thank you.", "thank you very much.", "thanks for watching!",
            "you", "bye.", "subs by www.zeoranger.co.uk", "[music]",
            "(music)", "[applause]", "...", ".", "so",
        }
        clean = text.strip()
        if clean.lower() in hallucinations:
            return ""
        return clean

transcription_service = GroqTranscriptionService()
