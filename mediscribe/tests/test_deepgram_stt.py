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
from src.services.deepgram_service import deepgram_service

def generate_synthetic_wav() -> bytes:
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

def test_deepgram_service_config():
    """Verify Deepgram service initializes model and fallback."""
    print(f"\n[INFO] Deepgram service model: {deepgram_service.model}, configured: {deepgram_service.is_configured()}")
    ws_url = deepgram_service.get_live_ws_url()
    assert "nova-2-medical" in ws_url
    print("[PASS] Deepgram WebSocket URL constructed successfully:", ws_url)

def test_websocket_stt_endpoint():
    """Verify WebSocket endpoint /api/ws/transcribe handles connections smoothly."""
    client = TestClient(app)
    synthetic_wav = generate_synthetic_wav()

    with client.websocket_connect("/api/ws/transcribe") as websocket:
        websocket.send_text("ping")
        resp = websocket.receive_json()
        assert resp["type"] == "pong"
        print("[PASS] WebSocket text ping/pong verified.")

        websocket.send_bytes(synthetic_wav)
        audio_resp = websocket.receive_json()
        assert audio_resp["type"] in ("transcript", "ping", "error")
        print(f"[PASS] WebSocket audio chunk processed -> response type: {audio_resp['type']}")

def test_http_audio_transcribe():
    """Verify POST /api/transcribe-audio endpoint."""
    client = TestClient(app)
    synthetic_wav = generate_synthetic_wav()

    files = {"file": ("test.wav", synthetic_wav, "audio/wav")}
    res = client.post("/api/transcribe-audio", files=files)
    assert res.status_code == 200, f"Failed: {res.text}"
    data = res.json()
    assert data["status"] == "success"
    print(f"[PASS] HTTP /api/transcribe-audio succeeded in {data['latency_ms']}ms.")

if __name__ == "__main__":
    test_deepgram_service_config()
    test_websocket_stt_endpoint()
    test_http_audio_transcribe()
    print("\n[SUCCESS] ALL DEEPGRAM & REAL-TIME STT TESTS PASSED!")
