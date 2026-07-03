export interface TranscriptionPacket {
  type: 'transcript' | 'error' | 'config_ack';
  text?: string;
  message?: string;
  latency_ms?: number;
  timestamp?: number;
}

export type MessageCallback = (packet: TranscriptionPacket) => void;
export type StatusCallback = (status: 'disconnected' | 'connecting' | 'connected' | 'recording') => void;

export class AudioStreamer {
  private ws: WebSocket | null = null;
  private mediaStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private chunkInterval: number | null = null;
  private onMessage: MessageCallback;
  private onStatus: StatusCallback;
  private isRecording = false;
  private chunkDurationMs = 5000; // 5-second chunks per user request
  private currentLanguage = 'auto'; // Default to auto-detect multilingual

  constructor(onMessage: MessageCallback, onStatus: StatusCallback) {
    this.onMessage = onMessage;
    this.onStatus = onStatus;
  }

  public setLanguage(lang: string): void {
    this.currentLanguage = lang;
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'config',
        format: 'webm',
        model: 'whisper-large-v3-turbo',
        language: this.currentLanguage
      }));
    }
  }

  public async connect(url = 'ws://localhost:8000/api/ws/transcribe'): Promise<void> {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.onStatus('connecting');
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('[AudioStreamer] WebSocket connected');
        this.onStatus('connected');
        // Send initial config
        this.ws?.send(JSON.stringify({
          type: 'config',
          format: 'webm',
          model: 'whisper-large-v3-turbo',
          language: this.currentLanguage
        }));
        resolve();
      };

      this.ws.onmessage = (event) => {
        try {
          const packet: TranscriptionPacket = JSON.parse(event.data);
          this.onMessage(packet);
        } catch (err) {
          console.error('[AudioStreamer] Error parsing WS message:', err);
        }
      };

      this.ws.onerror = (err) => {
        console.error('[AudioStreamer] WebSocket error:', err);
        reject(err);
      };

      this.ws.onclose = () => {
        console.log('[AudioStreamer] WebSocket closed');
        this.stopRecording();
        this.onStatus('disconnected');
        this.ws = null;
      };
    });
  }

  public async startRecording(): Promise<void> {
    if (this.isRecording) return;

    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      await this.connect();
    }

    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      this.isRecording = true;
      this.onStatus('recording');

      // Start the cycle of recording discrete standalone 5-second WebM chunks
      this.recordNextChunk();
      this.chunkInterval = window.setInterval(() => {
        if (this.isRecording) {
          this.cycleRecorder();
        }
      }, this.chunkDurationMs);

    } catch (err) {
      console.error('[AudioStreamer] Error requesting mic permissions:', err);
      this.onMessage({
        type: 'error',
        message: 'Microphone permission denied or device not found.'
      });
      this.onStatus('connected');
    }
  }

  private recordNextChunk(): void {
    if (!this.mediaStream || !this.isRecording) return;

    // Determine mimeType
    let mimeType = 'audio/webm;codecs=opus';
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      mimeType = 'audio/webm';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = ''; // Let browser pick default
      }
    }

    const chunks: Blob[] = [];
    this.mediaRecorder = new MediaRecorder(this.mediaStream, mimeType ? { mimeType } : undefined);

    this.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunks.push(e.data);
      }
    };

    this.mediaRecorder.onstop = async () => {
      if (chunks.length === 0) return;
      const audioBlob = new Blob(chunks, { type: mimeType || 'audio/webm' });
      
      // Send binary chunk over WebSocket
      if (this.ws && this.ws.readyState === WebSocket.OPEN && audioBlob.size > 100) {
        const buffer = await audioBlob.arrayBuffer();
        this.ws.send(buffer);
      }
    };

    this.mediaRecorder.start();
  }

  private cycleRecorder(): void {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop(); // Triggers onstop, which packages and sends the chunk
    }
    // Immediately spawn next chunk recorder
    this.recordNextChunk();
  }

  public stopRecording(): void {
    if (!this.isRecording) return;
    this.isRecording = false;

    if (this.chunkInterval) {
      clearInterval(this.chunkInterval);
      this.chunkInterval = null;
    }

    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.onStatus('connected');
    } else {
      this.onStatus('disconnected');
    }
  }

  public disconnect(): void {
    this.stopRecording();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.onStatus('disconnected');
  }
}
