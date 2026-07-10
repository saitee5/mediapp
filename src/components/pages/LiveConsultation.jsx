import { useState, useEffect, useRef } from "react";
import {
  Play,
  Activity,
  HeartPulse,
  ArrowRight,
  Sparkles,
} from "lucide-react";


const mockPatient = {
  name: "Elena Rodriguez",
  age: 72,
  gender: "Female",
  room: "Room 402 • Post-Op",
  avatarUrl: null,
  medicalHistory: [
    "Hypertension",
    "Type 2 Diabetes",
    "Osteoarthritis in knees",
    "History of atrial fibrillation (diagnosed 2018)",
  ],
  allergies: ["Penicillin", "Latex"],
  activeMedications: ["Lisinopril 10mg QD", "Metformin 500mg BID", "Eliquis 5mg BID"],
};

const mockTranscriptScript = [
  { speaker: "Doctor", text: "Good morning, Elena. How are you feeling today following your surgery? I noticed your mobility is improving." },
  { speaker: "Patient", text: "I'm doing okay, doctor. The pain in my knee is much better." },
  { speaker: "Doctor", text: "That's great to hear. Any dizziness or lightheadedness when you stand up?" },
  { speaker: "Patient", text: "Actually yes, a couple of times this week when I got out of bed." },
];

const mockInsights = {
  symptoms: ["Orthostatic Dizziness", "Chest Thumping", "Decreased Hydration"],
  conditions: [
    { name: "Orthostatic Hypotension", confidence: "72%" },
    { name: "Atrial Flutter Recurrence", confidence: "38%" },
  ],
  vitals: [
    { label: "Blood Pressure", value: "112/78", status: "Stable" },
    { label: "Heart Rate", value: "82 bpm", status: "Regular" },
  ],
};

export default function LiveConsultation() {
  const [isListening, setIsListening] = useState(false);
  const [activeSpeaker, setActiveSpeaker] = useState("Doctor");
  const [transcript, setTranscript] = useState([]);
  const [statusText, setStatusText] = useState("Ready to start");
  const [latency, setLatency] = useState(null);

  const transcriptEndRef = useRef(null);
  const wsRef = useRef(null);
  const streamRef = useRef(null);
  const currentRecorderRef = useRef(null);
  const isListeningRef = useRef(false);
  const activeSpeakerRef = useRef("Doctor");

  useEffect(() => {
    isListeningRef.current = isListening;
  }, [isListening]);

  useEffect(() => {
    activeSpeakerRef.current = activeSpeaker;
  }, [activeSpeaker]);

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [transcript]);

  const recordSegment = () => {
    if (!isListeningRef.current || !streamRef.current || !wsRef.current) return;
    if (wsRef.current.readyState !== WebSocket.OPEN) return;

    try {
      const options = MediaRecorder.isTypeSupported("audio/webm")
        ? { mimeType: "audio/webm" }
        : {};
      const recorder = new MediaRecorder(streamRef.current, options);
      currentRecorderRef.current = recorder;

      recorder.ondataavailable = async (e) => {
        if (e.data && e.data.size > 0 && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          const arrayBuffer = await e.data.arrayBuffer();
          wsRef.current.send(arrayBuffer);
        }
      };

      recorder.onstop = () => {
        if (isListeningRef.current) {
          recordSegment();
        }
      };

      recorder.start();

      setTimeout(() => {
        if (recorder.state === "recording") {
          recorder.stop();
        }
      }, 3500);
    } catch (err) {
      console.error("Error in recordSegment:", err);
      setStatusText("Recording error");
      stopListening();
    }
  };

  const startListening = async () => {
    try {
      setStatusText("Connecting to server...");
      setTranscript([]);
      setLatency(null);

      const wsUrl = "ws://localhost:8000/api/ws/transcribe";
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = async () => {
        setStatusText("Requesting microphone...");
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          streamRef.current = stream;
          setIsListening(true);
          setStatusText("Listening...");
          recordSegment();
        } catch (err) {
          console.error("Microphone access error:", err);
          setStatusText("Microphone access denied");
          ws.close();
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "transcript" && data.text) {
            const speaker = activeSpeakerRef.current;
            setLatency(data.latency_ms);

            setTranscript((prev) => {
              if (prev.length === 0) {
                return [{ speaker, text: data.text, timestamp: data.timestamp }];
              }
              const last = prev[prev.length - 1];
              if (last.speaker === speaker) {
                const updatedLast = {
                  ...last,
                  text: last.text.endsWith(".") || last.text.endsWith("?") || last.text.endsWith("!")
                    ? `${last.text} ${data.text}`
                    : `${last.text}. ${data.text}`
                };
                return [...prev.slice(0, -1), updatedLast];
              } else {
                return [...prev, { speaker, text: data.text, timestamp: data.timestamp }];
              }
            });
          } else if (data.type === "error") {
            console.error("API error:", data.message);
          }
        } catch (e) {
          console.error("Error parsing WebSocket message:", e);
        }
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        setStatusText("Connection error");
      };

      ws.onclose = () => {
        console.log("WebSocket closed");
        cleanup();
      };
    } catch (err) {
      console.error("Error starting consultation:", err);
      setStatusText("Failed to start");
    }
  };

  const stopListening = () => {
    setIsListening(false);
    setStatusText("Ready to start");
    cleanup();
  };

  const toggleListening = async () => {
    if (isListening) {
      stopListening();
    } else {
      await startListening();
    }
  };

  const cleanup = () => {
    if (currentRecorderRef.current && currentRecorderRef.current.state !== "inactive") {
      try {
        currentRecorderRef.current.stop();
      } catch (e) {}
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (wsRef.current) {
      if (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING) {
        wsRef.current.close();
      }
      wsRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      cleanup();
    };
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Patient Info */}
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 flex flex-col">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-14 h-14 rounded-full bg-slate-200 overflow-hidden flex items-center justify-center text-base font-bold text-slate-500 shrink-0">
              {mockPatient.avatarUrl ? (
                <img src={mockPatient.avatarUrl} alt={mockPatient.name} className="w-full h-full object-cover" />
              ) : (
                mockPatient.name.split(" ").map((n) => n[0]).join("").slice(0, 2)
              )}
            </div>
            <div>
              <h2 className="font-bold text-slate-900 font-display text-lg leading-tight">
                {mockPatient.name}
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                {mockPatient.age} Years • {mockPatient.gender}
              </p>
            </div>
          </div>
          <span className="self-start mt-1 mb-5 px-2.5 py-1 bg-[#e6f5f4] text-[#007e7a] text-[11px] font-bold rounded-full">
            {mockPatient.room}
          </span>

          <div className="space-y-5 flex-1">
            <div>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-2">
                Medical History
              </p>
              <p className="text-sm text-slate-600 leading-relaxed">
                {mockPatient.medicalHistory.join(", ")}
              </p>
            </div>

            <div>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-2">
                Allergies
              </p>
              <div className="flex flex-wrap gap-2">
                {mockPatient.allergies.map((a) => (
                  <span
                    key={a}
                    className="px-2.5 py-1 bg-red-50 text-red-700 text-xs font-bold rounded-full border border-red-100"
                  >
                    {a}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-2">
                Active Medications
              </p>
              <ul className="text-sm text-slate-600 space-y-1">
                {mockPatient.activeMedications.map((m) => (
                  <li key={m}>{m}</li>
                ))}
              </ul>
            </div>
          </div>

          <button
            onClick={toggleListening}
            className={`mt-6 w-full flex items-center justify-center gap-2 text-sm font-bold py-3 rounded-xl transition-colors cursor-pointer ${
              isListening
                ? "bg-red-600 hover:bg-red-700 text-white"
                : "bg-slate-900 hover:bg-slate-800 text-white"
            }`}
          >
            {isListening ? (
              <>
                <span className="w-2.5 h-2.5 bg-white rounded-sm shrink-0" />
                <span>Stop Consultation</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current shrink-0" />
                <span>Start Consultation</span>
              </>
            )}
          </button>
        </div>

        {/* Transcript */}
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 flex flex-col h-160">
          <div className="flex items-center justify-between gap-2 mb-4 border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              {isListening ? (
                <span className="w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse" />
              ) : (
                <span className="w-2.5 h-2.5 bg-slate-300 rounded-full" />
              )}
              <h3 className="font-bold text-slate-800 font-display text-sm">
                {statusText}
              </h3>
            </div>
            {isListening && (
              <div className="flex items-center bg-slate-100 rounded-xl p-1 text-[11px] font-semibold">
                <button
                  onClick={() => setActiveSpeaker("Doctor")}
                  className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                    activeSpeaker === "Doctor"
                      ? "bg-slate-900 text-white shadow-sm"
                      : "text-slate-500 hover:text-slate-800"
                  }`}
                >
                  Doctor
                </button>
                <button
                  onClick={() => setActiveSpeaker("Patient")}
                  className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                    activeSpeaker === "Patient"
                      ? "bg-[#007e7a] text-white shadow-sm"
                      : "text-slate-500 hover:text-slate-800"
                  }`}
                >
                  Patient
                </button>
              </div>
            )}
          </div>

          <div className="flex-1 overflow-y-auto space-y-4 pr-1">
            {transcript.map((line, i) => (
              <div key={i} className="animate-fade-in">
                <p
                  className={`text-[10px] font-bold mb-0.5 uppercase tracking-wide ${
                    line.speaker === "Doctor" ? "text-slate-500" : "text-[#007e7a]"
                  }`}
                >
                  {line.speaker}
                </p>
                <p className="text-sm text-slate-700 leading-relaxed font-medium">{line.text}</p>
              </div>
            ))}
            {transcript.length === 0 && (
              <p className="text-sm text-slate-400">
                {isListening
                  ? "Waiting for speech... Speak into your microphone."
                  : "Transcript will appear here once the consultation starts."}
              </p>
            )}
            <div ref={transcriptEndRef} />
          </div>

          {latency !== null && isListening && (
            <div className="text-[10px] text-slate-400 text-right mt-2 border-t border-slate-100 pt-2 font-medium">
              API Latency: {latency}ms
            </div>
          )}
        </div>

        
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 flex flex-col">
          <div className="flex items-center gap-2 mb-5">
            <Sparkles className="w-4 h-4 text-[#007e7a]" />
            <h3 className="font-bold text-slate-800 font-display">AI Insights</h3>
          </div>

          <div className="space-y-5 flex-1">
            <div>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-2">
                Extracted Symptoms
              </p>
              <div className="flex flex-wrap gap-2">
                {mockInsights.symptoms.map((s) => (
                  <span
                    key={s}
                    className="px-2.5 py-1 bg-[#e6f5f4] text-[#007e7a] text-xs font-bold rounded-full"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-2">
                Possible Conditions
              </p>
              <div className="space-y-2">
                {mockInsights.conditions.map((c) => (
                  <div
                    key={c.name}
                    className="flex items-center justify-between px-3 py-2 bg-slate-50 rounded-xl"
                  >
                    <span className="text-sm font-semibold text-slate-700">{c.name}</span>
                    <span className="text-xs font-bold text-[#007e7a]">{c.confidence}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-2">
                Real-Time Vitals
              </p>
              <div className="grid grid-cols-2 gap-3">
                {mockInsights.vitals.map((v) => (
                  <div key={v.label} className="bg-slate-50 rounded-xl p-3">
                    <div className="flex items-center gap-1.5 mb-1">
                      {v.label === "Heart Rate" ? (
                        <HeartPulse className="w-3.5 h-3.5 text-red-500" />
                      ) : (
                        <Activity className="w-3.5 h-3.5 text-slate-400" />
                      )}
                      <span className="text-[10px] font-bold text-slate-400 uppercase">
                        {v.label}
                      </span>
                    </div>
                    <p className="text-lg font-extrabold text-slate-900">{v.value}</p>
                    <p className="text-[11px] font-semibold text-emerald-600">{v.status}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <button className="mt-6 w-full flex items-center justify-center gap-2 bg-[#007e7a] hover:bg-[#005f5c] text-white text-sm font-bold py-3 rounded-xl transition-colors">
            View Suggested Plan
            <ArrowRight className="w-4 h-4" />
          </button>

          <p className="mt-4 text-[11px] text-slate-400 leading-relaxed">
            AI model is monitoring for medication conflicts with Eliquis and Lisinopril based on patient's current symptoms.
          </p>
        </div>
      </div>
    </div>
  );
}