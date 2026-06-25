import io
import os
import time
import asyncio
import logging
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import AsyncGroq

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LiveTranscriber")

# Load env
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY is not set in environment variables.")

# Initialize Groq Async Client
groq_client = AsyncGroq(api_key=GROQ_API_KEY)

app = FastAPI(
    title="Live Audio Transcribing API",
    description="Real-time speech-to-text WebSocket backend using Groq Whisper API",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "groq_configured": bool(GROQ_API_KEY),
        "model": "whisper-large-v3-turbo"
    }

@app.websocket("/api/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"Client connected: {websocket.client}")

    # Session variables
    audio_format = "webm" # Default format from React MediaRecorder
    model_name = "whisper-large-v3-turbo"
    language = "en"

    try:
        while True:
            # Receive message from client (could be bytes audio chunk or text config)
            message = await websocket.receive()

            if "text" in message and message["text"]:
                # Handle control/config JSON messages
                try:
                    import json
                    data = json.loads(message["text"])
                    if data.get("type") == "config":
                        audio_format = data.get("format", "webm")
                        model_name = data.get("model", "whisper-large-v3-turbo")
                        language = data.get("language", "en")
                        logger.info(f"Updated session config: format={audio_format}, model={model_name}, lang={language}")
                        await websocket.send_json({"type": "config_ack", "status": "success"})
                except Exception as e:
                    logger.error(f"Error parsing control message: {e}")
                continue

            if "bytes" in message and message["bytes"]:
                audio_bytes = message["bytes"]
                
                # Ignore very tiny audio frames (e.g. empty buffers < 100 bytes)
                if len(audio_bytes) < 100:
                    continue

                start_time = time.time()
                try:
                    # Wrap audio bytes into in-memory buffer
                    buffer = io.BytesIO(audio_bytes)
                    buffer.name = f"chunk.{audio_format}"

                    # Call Groq Whisper API
                    kwargs = {
                        "file": (buffer.name, buffer),
                        "model": model_name,
                        "response_format": "json",
                        "temperature": 0.0
                    }
                    if language and language != "auto":
                        kwargs["language"] = language

                    transcription = await groq_client.audio.transcriptions.create(**kwargs)

                    latency_ms = round((time.time() - start_time) * 1000)
                    text = transcription.text.strip()

                    # Send transcribed text back to frontend
                    await websocket.send_json({
                        "type": "transcript",
                        "text": text,
                        "latency_ms": latency_ms,
                        "timestamp": time.time(),
                        "bytes_received": len(audio_bytes)
                    })

                except Exception as api_err:
                    logger.error(f"Groq API Error: {api_err}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(api_err),
                        "latency_ms": round((time.time() - start_time) * 1000)
                    })

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {websocket.client}")
    except Exception as e:
        logger.error(f"Unexpected WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
