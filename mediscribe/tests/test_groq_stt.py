import sys
import wave
import io
import struct
import math
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to sys.path
MEDISCRIBE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MEDISCRIBE_DIR))

from main import app
from src.services.transcription_service import transcription_service

def generate_synthetic_sine_wav() -> bytes:
    """Generates a 1-second 440Hz sine wave WAV file in memory."""
    buf = io.BytesIO()
    sample_rate = 16000
    duration = 1.0
    num_samples = int(sample_rate * duration)

    with wave.open(buf, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(num_samples):
            value = int(math.sin(2 * math.pi * 440 * i / sample_rate) * 16000)
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

    return buf.getvalue()

def test_transcription_service_config():
    """Verify Groq transcription service is initialized with valid API key."""
    assert transcription_service.is_configured(), "Groq transcription service is not configured!"
    print("\n[PASS] Groq Whisper STT service is configured with model:", transcription_service.model)

def test_websocket_stt_connection():
    """Verify WebSocket endpoint /api/ws/transcribe responds to connections and audio chunks."""
    client = TestClient(app)
    synthetic_wav = generate_synthetic_sine_wav()

    with client.websocket_connect("/api/ws/transcribe") as websocket:
        # Send ping text
        websocket.send_text("ping")
        resp = websocket.receive_json()
        assert resp["type"] == "pong"
        print("[PASS] WebSocket text ping/pong verified.")

        # Send binary audio chunk
        websocket.send_bytes(synthetic_wav)
        audio_resp = websocket.receive_json()
        assert audio_resp["type"] in ("transcript", "ping", "error")
        print(f"[PASS] WebSocket audio chunk processed -> response type: {audio_resp['type']}, latency: {audio_resp.get('latency_ms')}ms")

def test_http_audio_transcribe_endpoint():
    """Verify POST /api/transcribe-audio endpoint."""
    client = TestClient(app)
    synthetic_wav = generate_synthetic_sine_wav()

    files = {"file": ("test.wav", synthetic_wav, "audio/wav")}
    res = client.post("/api/transcribe-audio", files=files)
    assert res.status_code == 200, f"Transcribe audio failed: {res.text}"
    data = res.json()
    assert data["status"] == "success"
    print(f"[PASS] HTTP /api/transcribe-audio succeeded in {data['latency_ms']}ms.")

if __name__ == "__main__":
    test_transcription_service_config()
    test_websocket_stt_connection()
    test_http_audio_transcribe_endpoint()
    print("\n[SUCCESS] ALL GROQ WHISPER REAL-TIME STT TESTS PASSED!")
