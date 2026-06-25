import React, { useState, useEffect, useRef } from 'react';
import { 
  Mic, 
  MicOff, 
  Radio, 
  Copy, 
  Download, 
  Trash2, 
  Zap, 
  Clock, 
  Activity, 
  Check, 
  AlertCircle,
  Globe 
} from 'lucide-react';
import { AudioStreamer, type TranscriptionPacket } from '../services/audioStreamer';

interface TranscriptItem {
  id: string;
  text: string;
  timestamp: string;
  latencyMs: number;
}

export const LiveTranscriber: React.FC = () => {
  const [status, setStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'recording'>('disconnected');
  const [transcripts, setTranscripts] = useState<TranscriptItem[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [lastLatency, setLastLatency] = useState<number | null>(null);
  const [selectedLang, setSelectedLang] = useState('auto');

  const streamerRef = useRef<AudioStreamer | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // Initialize streamer once
  useEffect(() => {
    streamerRef.current = new AudioStreamer(
      (packet: TranscriptionPacket) => {
        if (packet.type === 'transcript' && packet.text) {
          const newItem: TranscriptItem = {
            id: Math.random().toString(36).substring(2, 9),
            text: packet.text,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            latencyMs: packet.latency_ms || 0
          };
          setTranscripts(prev => [...prev, newItem]);
          if (packet.latency_ms) {
            setLastLatency(packet.latency_ms);
          }
          setErrorMsg(null);
        } else if (packet.type === 'error' && packet.message) {
          setErrorMsg(packet.message);
        }
      },
      (newStatus) => {
        setStatus(newStatus);
      }
    );

    // Auto connect on mount
    streamerRef.current.connect().catch(() => {
      // Backend might be offline initially
    });

    return () => {
      streamerRef.current?.disconnect();
    };
  }, []);

  // Auto scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcripts]);

  const handleToggleRecord = async () => {
    if (!streamerRef.current) return;
    setErrorMsg(null);

    if (status === 'recording') {
      streamerRef.current.stopRecording();
    } else {
      await streamerRef.current.startRecording();
    }
  };

  const handleClear = () => {
    setTranscripts([]);
    setLastLatency(null);
  };

  const handleLangChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const lang = e.target.value;
    setSelectedLang(lang);
    streamerRef.current?.setLanguage(lang);
  };

  const fullText = transcripts.map(t => t.text).join(' ');
  const wordCount = fullText.trim() ? fullText.trim().split(/\s+/).length : 0;

  const handleCopy = () => {
    if (!fullText) return;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!fullText) return;
    const element = document.createElement('a');
    const file = new Blob([fullText], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `transcript_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="w-full max-w-5xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8 animate-fade-in">
      
      {/* Top Banner & Status Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800/80 p-6 rounded-3xl backdrop-blur-xl shadow-2xl shadow-cyan-950/20">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 text-xs font-semibold uppercase tracking-wider bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-300 border border-cyan-500/30 rounded-full flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400 animate-pulse" />
              Groq Whisper Large v3 Turbo
            </span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center gap-3 pt-1">
            Real-Time Live Transcription
          </h1>
          <p className="text-slate-400 text-sm">
            Streaming discrete 5-second audio chunks directly to Groq LPU inference.
          </p>
        </div>

        {/* Connection, Language & Latency Badges */}
        <div className="flex flex-wrap items-center gap-3 self-start md:self-center">
          
          {/* Language Selector */}
          <div className="flex items-center gap-2 px-3.5 py-2 bg-slate-950/80 border border-slate-800 hover:border-purple-500/50 transition rounded-2xl text-sm shadow-inner">
            <Globe className="w-4 h-4 text-purple-400 shrink-0" />
            <select
              value={selectedLang}
              onChange={handleLangChange}
              className="bg-transparent text-slate-200 text-xs font-semibold focus:outline-none cursor-pointer pr-1"
            >
              <option value="auto" className="bg-slate-900 text-slate-100">🌐 Multilingual Auto-Detect</option>
              <option value="en" className="bg-slate-900 text-slate-100">🇺🇸 English</option>
              <option value="es" className="bg-slate-900 text-slate-100">🇪🇸 Spanish</option>
              <option value="hi" className="bg-slate-900 text-slate-100">🇮🇳 Hindi</option>
              <option value="fr" className="bg-slate-900 text-slate-100">🇫🇷 French</option>
              <option value="de" className="bg-slate-900 text-slate-100">🇩🇪 German</option>
              <option value="ja" className="bg-slate-900 text-slate-100">🇯🇵 Japanese</option>
              <option value="zh" className="bg-slate-900 text-slate-100">🇨🇳 Chinese</option>
              <option value="ar" className="bg-slate-900 text-slate-100">🇸🇦 Arabic</option>
              <option value="ru" className="bg-slate-900 text-slate-100">🇷🇺 Russian</option>
            </select>
          </div>

          <div className="flex items-center gap-2 px-4 py-2 bg-slate-950/60 border border-slate-800 rounded-2xl text-sm">
            <div className={`w-2.5 h-2.5 rounded-full ${
              status === 'recording' ? 'bg-rose-500 animate-ping' :
              status === 'connected' ? 'bg-emerald-400' :
              status === 'connecting' ? 'bg-amber-400 animate-pulse' : 'bg-slate-600'
            }`} />
            <span className="font-medium capitalize text-slate-300">
              {status === 'recording' ? 'Live Listening' : status}
            </span>
          </div>

          {lastLatency !== null && (
            <div className="flex items-center gap-1.5 px-4 py-2 bg-cyan-950/40 border border-cyan-800/50 rounded-2xl text-sm text-cyan-300 font-mono">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>{lastLatency}ms</span>
            </div>
          )}
        </div>
      </div>

      {/* Error Alert Box */}
      {errorMsg && (
        <div className="flex items-start gap-3 p-4 bg-rose-950/50 border border-rose-800/60 rounded-2xl text-rose-200 text-sm">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <p className="font-semibold text-rose-100">Transcription System Notice</p>
            <p className="text-rose-300">{errorMsg}</p>
          </div>
        </div>
      )}

      {/* Main Interactive Stage */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Control Panel & Audio Visualizer */}
        <div className="lg:col-span-4 space-y-6 flex flex-col justify-between bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl">
          <div className="space-y-6">
            <h2 className="text-lg font-bold text-slate-200 tracking-wide flex items-center gap-2">
              <Radio className="w-5 h-5 text-purple-400" />
              Microphone Feed
            </h2>

            {/* Pulsating Visualizer Ring */}
            <div className="relative py-12 flex items-center justify-center">
              {status === 'recording' && (
                <>
                  <div className="absolute w-36 h-36 bg-cyan-500/20 rounded-full animate-pulse-ring" />
                  <div className="absolute w-48 h-48 bg-purple-500/10 rounded-full animate-pulse-ring" style={{ animationDelay: '0.7s' }} />
                </>
              )}

              <button
                onClick={handleToggleRecord}
                disabled={status === 'connecting'}
                className={`relative z-10 w-28 h-28 rounded-full flex flex-col items-center justify-center gap-1.5 transition-all duration-300 shadow-2xl ${
                  status === 'recording' 
                    ? 'bg-gradient-to-br from-rose-500 to-red-600 hover:from-rose-600 hover:to-red-700 text-white scale-105 ring-4 ring-rose-500/30' 
                    : 'bg-gradient-to-br from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold ring-4 ring-cyan-500/20'
                }`}
              >
                {status === 'recording' ? (
                  <>
                    <MicOff className="w-8 h-8 animate-pulse" />
                    <span className="text-[10px] font-extrabold uppercase tracking-widest">Stop</span>
                  </>
                ) : (
                  <>
                    <Mic className="w-8 h-8" />
                    <span className="text-[10px] font-extrabold uppercase tracking-widest">Start</span>
                  </>
                )}
              </button>
            </div>

            <div className="text-center space-y-1">
              <p className="text-sm font-medium text-slate-300">
                {status === 'recording' ? 'Recording speech chunks...' : 'Mic is idle'}
              </p>
              <p className="text-xs text-slate-500">
                {status === 'recording' 
                  ? 'Sending audio buffers every 5000ms' 
                  : 'Press Start to begin real-time streaming'}
              </p>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-3 pt-6 border-t border-slate-800/80">
            <div className="bg-slate-950/80 rounded-2xl p-3.5 border border-slate-800/60">
              <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                <Clock className="w-3.5 h-3.5 text-cyan-400" />
                <span>Timeslice</span>
              </div>
              <p className="text-lg font-bold text-slate-100">5.0 sec</p>
            </div>

            <div className="bg-slate-950/80 rounded-2xl p-3.5 border border-slate-800/60">
              <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
                <Activity className="w-3.5 h-3.5 text-purple-400" />
                <span>Word Count</span>
              </div>
              <p className="text-lg font-bold text-slate-100">{wordCount}</p>
            </div>
          </div>
        </div>

        {/* Right Live Transcript Feed Container */}
        <div className="lg:col-span-8 flex flex-col bg-slate-900/60 border border-slate-800/80 rounded-3xl backdrop-blur-xl overflow-hidden shadow-2xl min-h-[500px]">
          
          {/* Feed Toolbar */}
          <div className="flex items-center justify-between px-6 py-4 bg-slate-900/90 border-b border-slate-800/80">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <h3 className="font-bold text-slate-200 text-sm tracking-wide uppercase">
                Live Transcribed Feed
              </h3>
              <span className="ml-2 px-2 py-0.5 text-xs font-mono bg-slate-800 text-slate-400 rounded-full">
                {transcripts.length} segments
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                disabled={!fullText}
                className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition disabled:opacity-30 disabled:hover:bg-transparent flex items-center gap-1.5 text-xs font-medium"
                title="Copy Transcript"
              >
                {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                <span className="hidden sm:inline">{copied ? 'Copied' : 'Copy'}</span>
              </button>

              <button
                onClick={handleDownload}
                disabled={!fullText}
                className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition disabled:opacity-30 disabled:hover:bg-transparent flex items-center gap-1.5 text-xs font-medium"
                title="Download .txt"
              >
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline">Save</span>
              </button>

              <button
                onClick={handleClear}
                disabled={transcripts.length === 0}
                className="p-2 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl transition disabled:opacity-30 disabled:hover:bg-transparent"
                title="Clear Feed"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Scrolling Transcript Area */}
          <div className="flex-1 p-6 sm:p-8 overflow-y-auto max-h-[550px] space-y-4">
            {transcripts.length === 0 ? (
              <div className="h-full min-h-[350px] flex flex-col items-center justify-center text-center p-8 border-2 border-dashed border-slate-800/60 rounded-2xl">
                <Radio className="w-12 h-12 text-slate-700 mb-3 animate-bounce" />
                <p className="text-slate-400 font-semibold text-base">No speech transcribed yet</p>
                <p className="text-slate-600 text-sm mt-1 max-w-sm">
                  Click the **Start** button on the left, speak clearly, and your captions will stream here in real time.
                </p>
              </div>
            ) : (
              <div className="bg-slate-950/40 border border-slate-800/50 p-6 sm:p-8 rounded-2xl animate-fade-in min-h-[350px]">
                <p className="text-slate-200 font-normal leading-relaxed text-lg sm:text-xl tracking-normal whitespace-pre-wrap select-text">
                  {transcripts.map((item, idx) => (
                    <span 
                      key={item.id} 
                      className="animate-fade-in transition-colors duration-300 hover:bg-cyan-500/15 hover:text-cyan-200 rounded px-1 -mx-1 py-0.5 inline-block sm:inline cursor-default"
                      title={`Transcribed at ${item.timestamp} (${item.latencyMs}ms latency)`}
                    >
                      {idx > 0 && !item.text.match(/^[.,!?;:]/) ? ' ' : ''}{item.text}
                    </span>
                  ))}
                </p>
                <div ref={bottomRef} />
              </div>
            )}
          </div>

          {/* Footer Bar */}
          <div className="px-6 py-3 bg-slate-950/60 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-500 font-mono">
            <span>FastAPI Backend: ws://localhost:8000/api/ws/transcribe</span>
            <span>Sampling: 16kHz Mono Opus</span>
          </div>
        </div>

      </div>

    </div>
  );
};
