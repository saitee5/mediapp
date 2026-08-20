import json
import time
import asyncio
from typing import Optional, Dict, Any, Tuple, AsyncGenerator
import httpx
import websockets
from src.utils.config import settings
from src.utils.logger import logger
from src.services.transcription_service import transcription_service as groq_transcription_service

class DeepgramService:
    """
    Real-time continuous audio streaming and batch speech-to-text service using Deepgram Nova-2 Medical.
    Supports true full-duplex live WebSocket streaming with interim results and zero word cut-offs.
    """

    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY
        self.model = settings.DEFAULT_DEEPGRAM_MODEL or "nova-2-medical"
        self._init_service()

    def _init_service(self):
        if self.api_key:
            logger.info(f"Deepgram STT service configured with model '{self.model}'.")
        else:
            logger.info("DEEPGRAM_API_KEY not yet set. Real-time STT will use Groq Whisper fallback.")

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def get_live_ws_url(self) -> str:
        """Constructs the Deepgram live streaming WebSocket URL with medical parameters."""
        params = [
            f"model={self.model}",
            "smart_format=true",
            "interim_results=true",
            "endpointing=300",
            "punctuate=true",
            "language=en",
        ]
        return f"wss://api.deepgram.com/v1/listen?{'&'.join(params)}"

    async def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        mime_type: str = "audio/webm",
        language: str = "en",
    ) -> Tuple[str, int]:
        """
        Transcribes an audio buffer using Deepgram Nova-2 Medical REST API.
        Falls back to Groq Whisper if Deepgram API key is not configured.
        """
        if not self.is_configured():
            # Fallback to Groq Whisper
            return await groq_transcription_service.transcribe_audio_bytes(
                audio_bytes=audio_bytes,
                mime_type=mime_type,
                language=language,
            )

        start_time = time.perf_counter()
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": mime_type,
        }
        url = f"https://api.deepgram.com/v1/listen?model={self.model}&smart_format=true&punctuate=true&language={language}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, content=audio_bytes)
                response.raise_for_status()
                data = response.json()

            latency_ms = int((time.perf_counter() - start_time) * 1000)
            
            # Extract transcript from Deepgram JSON structure
            channels = data.get("results", {}).get("channels", [])
            transcript = ""
            if channels and len(channels) > 0:
                alternatives = channels[0].get("alternatives", [])
                if alternatives:
                    transcript = alternatives[0].get("transcript", "").strip()

            logger.info(f"Deepgram Nova-2 ({latency_ms}ms): '{transcript[:60]}...'")
            return transcript, latency_ms

        except Exception as e:
            logger.warning(f"Deepgram transcription error: {e}. Falling back to Groq Whisper...")
            return await groq_transcription_service.transcribe_audio_bytes(
                audio_bytes=audio_bytes,
                mime_type=mime_type,
                language=language,
            )

deepgram_service = DeepgramService()
