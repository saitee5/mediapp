import { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  Play,
  Activity,
  HeartPulse,
  ArrowRight,
  Sparkles,
  Loader2,
  Mic,
  MicOff,
  RotateCcw,
  FileText,
  AlertCircle,
} from "lucide-react";
import { api } from "../../services/api";

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

const sampleScript = [
  { speaker: "Doctor", text: "Good morning, Elena. How are you feeling today following your surgery? I noticed your mobility is improving." },
  { speaker: "Patient", text: "I'm doing okay, doctor. The knee pain is much better, but I've been feeling a bit dizzy when getting out of bed." },
  { speaker: "Doctor", text: "I see. Let's check your blood pressure and review your medications. Are you still taking the Lisinopril and Metformin as prescribed?" },
  { speaker: "Patient", text: "Yes, every morning with breakfast. But I ran out of my Eliquis prescription two days ago." },
  { speaker: "Doctor", text: "That is very important for your atrial fibrillation. I will send an immediate refill for Eliquis 5mg BID to your pharmacy right away, and we will monitor your orthostatic blood pressure." },
];

export default function LiveConsultation() {
  const location = useLocation();
  const navigate = useNavigate();
  const statePatient = location.state?.patientData;

  const parseCommaList = (str) => {
    if (!str) return null;
    const parsed = str.split(",").map((s) => s.trim()).filter(Boolean);
    return parsed.length > 0 ? parsed : null;
  };

  const activePatient = {
    ...mockPatient,
    name: statePatient?.name || mockPatient.name,
    age: statePatient?.age || mockPatient.age,
    gender: statePatient?.gender || mockPatient.gender,
    medicalHistory: parseCommaList(statePatient?.medicalHistory) || mockPatient.medicalHistory,
    allergies: parseCommaList(statePatient?.allergies) || mockPatient.allergies,
    activeMedications: parseCommaList(statePatient?.activeMedications) || mockPatient.activeMedications,
    bloodPressure: statePatient?.bloodPressure || "112/78",
    heartRate: statePatient?.heartRate || "98.6°F",
    temperature: statePatient?.temperature || "98.6°F",
  };

  const [isListening, setIsListening] = useState(false);
  const [activeSpeaker, setActiveSpeaker] = useState("Doctor");
  const [transcript, setTranscript] = useState(sampleScript);
  const [statusText, setStatusText] = useState("Ready to record or edit");
  const [isGenerating, setIsGenerating] = useState(false);
  const [apiError, setApiError] = useState(null);

  const transcriptEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const activeSpeakerRef = useRef("Doctor");
  const isListeningRef = useRef(false);
  // Committed (finalized) text for the line currently being spoken, kept separate from
  // interim text so interim updates never get double-appended once they finalize.
  const committedTextRef = useRef("");

  useEffect(() => {
    activeSpeakerRef.current = activeSpeaker;
    // Speaker changed -> next words start a brand new line, so clear the committed buffer.
    committedTextRef.current = "";
  }, [activeSpeaker]);

  useEffect(() => {
    isListeningRef.current = isListening;
  }, [isListening]);

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [transcript]);

  // Setup Web Speech API for Browser Speech Recognition
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setStatusText("Listening... Speak clearly.");
        setApiError(null);
      };

      recognition.onresult = (event) => {
        let interimTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const piece = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            // Lock this piece into the committed buffer permanently.
            committedTextRef.current = `${committedTextRef.current} ${piece}`.trim();
          } else {
            interimTranscript += piece;
          }
        }

        const combined = `${committedTextRef.current} ${interimTranscript}`.trim();
        if (!combined) return;

        const speaker = activeSpeakerRef.current;
        setTranscript((prev) => {
          if (prev.length === 0) {
            return [{ speaker, text: combined, timestamp: new Date().toLocaleTimeString() }];
          }
          const last = prev[prev.length - 1];
          if (last.speaker === speaker) {
            // Always REPLACE with the full committed+interim text for this line —
            // never append, since `combined` already contains everything said so far.
            const updated = [...prev];
            updated[updated.length - 1] = { ...last, text: combined };
            return updated;
          } else {
            return [...prev, { speaker, text: combined, timestamp: new Date().toLocaleTimeString() }];
          }
        });
      };

      recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        if (event.error === "not-allowed") {
          setStatusText("Microphone access denied. You can type directly into transcript.");
        } else {
          setStatusText(`Speech status: ${event.error}`);
        }
      };

      recognition.onend = () => {
        if (isListeningRef.current) {
          try {
            recognition.start();
          } catch (e) {
            // Already started or restarting
          }
        } else {
          setStatusText("Consultation paused.");
        }
      };

      recognitionRef.current = recognition;
    } else {
      setStatusText("Web Speech API not supported in this browser. You can type transcript manually.");
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const toggleListening = () => {
    if (isListening) {
      setIsListening(false);
      isListeningRef.current = false;
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setStatusText("Consultation paused.");
    } else {
      committedTextRef.current = "";
      setIsListening(true);
      isListeningRef.current = true;
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (e) {
          console.warn("Error starting speech recognition:", e);
        }
      } else {
        setStatusText("Listening (Manual typing mode)");
      }
    }
  };

  const handleResetTranscript = () => {
    committedTextRef.current = "";
    setTranscript([]);
    setStatusText("Transcript cleared.");
  };

  const handleLoadSample = () => {
    committedTextRef.current = "";
    setTranscript(sampleScript);
    setStatusText("Sample clinical dialogue loaded.");
  };

  const handleSpeakerChange = (speaker) => {
    committedTextRef.current = "";
    setActiveSpeaker(speaker);
  };

  const getFormattedTranscript = () => {
    if (!transcript || transcript.length === 0) {
      return "Doctor: Patient presents for routine follow-up. Vital signs and examination stable.";
    }
    return transcript
      .map((item) => `${item.speaker}: ${item.text}`)
      .join("\n\n");
  };

  const handleGenerateSummary = async () => {
    setIsGenerating(true);
    setApiError(null);
    const rawTranscript = getFormattedTranscript();
    const sessionId = `consult_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    const patientId = activePatient.name.replace(/\s+/g, "_").toLowerCase();

    try {
      // Call backend API (FastAPI / LangGraph 2-agent pipeline)
      const res = await api.generateSummary({
        transcript: rawTranscript,
        sessionId,
        patientId,
      });

      console.log("Summary generation response:", res);

      // Navigate to review screen with live generated data
      navigate("/suggested-plan", {
        state: {
          sessionId: res.session_id || sessionId,
          caseStudySummary: res.case_study_summary,
          soap: res.soap,
          transcript: rawTranscript,
          patientData: activePatient,
        },
      });
    } catch (err) {
      console.error("Backend generation error:", err);
      setApiError(err.message || "Failed to generate summary with backend AI.");

      // Fallback transition so doctor can continue document review
      setTimeout(() => {
        navigate("/suggested-plan", {
          state: {
            sessionId,
            transcript: rawTranscript,
            patientData: activePatient,
            backendError: err.message,
          },
        });
      }, 1200);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {apiError && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded-2xl flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" />
          <div>
            <span className="font-bold">Backend notice:</span> {apiError} (Proceeding in offline/fallback mode)
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Patient Info Column */}
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 flex flex-col justify-between">
          <div className="space-y-5">
            <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
              <div className="w-14 h-14 rounded-full bg-slate-200 overflow-hidden flex items-center justify-center text-base font-bold text-slate-500 shrink-0">
                {activePatient.avatarUrl ? (
                  <img src={activePatient.avatarUrl} alt={activePatient.name} className="w-full h-full object-cover" />
                ) : (
                  activePatient.name.split(" ").map((n) => n[0]).join("").slice(0, 2)
                )}
              </div>
              <div>
                <h2 className="font-bold text-slate-900 font-display text-lg leading-tight">
                  {activePatient.name}
                </h2>
                <p className="text-xs text-slate-500 font-medium">
                  {activePatient.age} Years • {activePatient.gender}
                </p>
                <span className="inline-block mt-1 px-2.5 py-0.5 bg-[#e6f5f4] text-[#007e7a] text-[10px] font-bold rounded-full">
                  {activePatient.room}
                </span>
              </div>
            </div>

            <div>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-1.5">
                Medical History
              </p>
              <p className="text-xs text-slate-600 leading-relaxed font-medium">
                {Array.isArray(activePatient.medicalHistory) ? activePatient.medicalHistory.join(", ") : activePatient.medicalHistory}
              </p>
            </div>

            <div>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-1.5">
                Allergies
              </p>
              <div className="flex flex-wrap gap-1.5">
                {(Array.isArray(activePatient.allergies) ? activePatient.allergies : [activePatient.allergies]).map((a) => (
                  <span
                    key={a}
                    className="px-2 py-0.5 bg-red-50 text-red-700 text-xs font-bold rounded-full border border-red-100"
                  >
                    {a}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-1.5">
                Active Medications
              </p>
              <ul className="text-xs text-slate-600 space-y-1 font-medium">
                {(Array.isArray(activePatient.activeMedications) ? activePatient.activeMedications : [activePatient.activeMedications]).map((m) => (
                  <li key={m} className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-[#007e7a] rounded-full"></span>
                    {m}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-2">
                Patient Vitals
              </p>
              <div className="grid grid-cols-2 gap-2.5">
                <div className="bg-slate-50 rounded-xl p-2.5 border border-slate-100">
                  <div className="flex items-center gap-1 mb-0.5">
                    <Activity className="w-3.5 h-3.5 text-slate-400" />
                    <span className="text-[9px] font-bold text-slate-400 uppercase">BP</span>
                  </div>
                  <p className="text-base font-extrabold text-slate-900">{activePatient.bloodPressure}</p>
                </div>
                <div className="bg-slate-50 rounded-xl p-2.5 border border-slate-100">
                  <div className="flex items-center gap-1 mb-0.5">
                    <HeartPulse className="w-3.5 h-3.5 text-red-500" />
                    <span className="text-[9px] font-bold text-slate-400 uppercase">Pulse</span>
                  </div>
                  <p className="text-base font-extrabold text-slate-900">{activePatient.heartRate}</p>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={toggleListening}
            className={`mt-6 w-full flex items-center justify-center gap-2 text-sm font-bold py-3.5 rounded-xl transition-all shadow-sm cursor-pointer ${isListening
                ? "bg-red-600 hover:bg-red-700 text-white animate-pulse"
                : "bg-slate-900 hover:bg-slate-800 text-white"
              }`}
          >
            {isListening ? (
              <>
                <MicOff className="w-4 h-4 shrink-0" />
                <span>Pause Recording</span>
              </>
            ) : (
              <>
                <Mic className="w-4 h-4 shrink-0" />
                <span>Start Live Scribe</span>
              </>
            )}
          </button>
        </div>

        {/* Live Transcript Column */}
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 flex flex-col h-[600px]">
          <div className="flex items-center justify-between gap-2 mb-4 border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              {isListening ? (
                <span className="w-2.5 h-2.5 bg-red-500 rounded-full animate-ping" />
              ) : (
                <span className="w-2.5 h-2.5 bg-slate-300 rounded-full" />
              )}
              <h3 className="font-bold text-slate-800 font-display text-sm truncate max-w-[200px]">
                {statusText}
              </h3>
            </div>

            <div className="flex items-center gap-2">
              <div className="flex items-center bg-slate-100 rounded-xl p-1 text-[11px] font-semibold">
                <button
                  type="button"
                  onClick={() => handleSpeakerChange("Doctor")}
                  className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${activeSpeaker === "Doctor"
                      ? "bg-slate-900 text-white shadow-sm"
                      : "text-slate-500 hover:text-slate-800"
                    }`}
                >
                  Doctor
                </button>
                <button
                  type="button"
                  onClick={() => handleSpeakerChange("Patient")}
                  className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${activeSpeaker === "Patient"
                      ? "bg-[#007e7a] text-white shadow-sm"
                      : "text-slate-500 hover:text-slate-800"
                    }`}
                >
                  Patient
                </button>
              </div>

              <button
                onClick={handleResetTranscript}
                title="Clear transcript"
                className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto space-y-4 pr-1">
            {transcript.map((line, i) => (
              <div key={i} className="animate-fade-in bg-slate-50/50 p-3 rounded-2xl border border-slate-100">
                <div className="flex items-center justify-between mb-1">
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider ${line.speaker === "Doctor" ? "text-slate-600" : "text-[#007e7a]"
                      }`}
                  >
                    {line.speaker}
                  </span>
                  <span className="text-[9px] text-slate-400 font-medium">
                    {line.timestamp || "Live"}
                  </span>
                </div>
                <p
                  className="text-sm text-slate-700 leading-relaxed font-medium focus:outline-none focus:bg-white p-1 rounded-lg transition-colors"
                  contentEditable={true}
                  suppressContentEditableWarning={true}
                  onBlur={(e) => {
                    const newText = e.currentTarget.textContent;
                    setTranscript((prev) => {
                      const next = [...prev];
                      next[i] = { ...next[i], text: newText };
                      return next;
                    });
                  }}
                >
                  {line.text}
                </p>
              </div>
            ))}
            {transcript.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400 space-y-3">
                <FileText className="w-10 h-10 text-slate-300 stroke-1" />
                <p className="text-sm">
                  {isListening
                    ? "Listening to conversation... Speak into your mic."
                    : "No dialogue recorded yet. Speak into mic or load sample dialogue."}
                </p>
                <button
                  onClick={handleLoadSample}
                  className="text-xs font-bold text-[#007e7a] hover:underline"
                >
                  Load Sample Clinical Dialogue
                </button>
              </div>
            )}
            <div ref={transcriptEndRef} />
          </div>

          <div className="text-[11px] text-slate-400 flex items-center justify-between mt-3 pt-3 border-t border-slate-100 font-medium">
            <span>Click any dialogue line to edit inline</span>
            <button
              onClick={handleLoadSample}
              className="text-[#007e7a] font-bold hover:underline"
            >
              Reset Sample
            </button>
          </div>
        </div>

        {/* AI Processing & Action Column */}
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 flex flex-col justify-between">
          <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-[#e6f5f4] text-[#007e7a] flex items-center justify-center shadow-inner">
              <Sparkles className="w-8 h-8" />
            </div>
            <div>
              <h3 className="font-extrabold text-slate-900 font-display text-2xl tracking-tight">
                AI Clinical Engine
              </h3>
              <p className="text-xs text-slate-500 font-medium mt-1 max-w-xs leading-relaxed">
                Processes dialogue through our 2-agent LangGraph pipeline: extracts clinical SOAP concepts and synthesizes case sheet summary.
              </p>
            </div>

            <div className="w-full bg-slate-50 rounded-2xl p-4 border border-slate-100 text-left space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
                <span className="w-2 h-2 rounded-full bg-[#007e7a]"></span>
                Agent 1: Clinical SOAP Extraction
              </div>
              <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
                <span className="w-2 h-2 rounded-full bg-teal-500"></span>
                Agent 2: Case Sheet Summary Generator
              </div>
              <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                Hospital PDF Report Renderer
              </div>
            </div>
          </div>

          <button
            onClick={handleGenerateSummary}
            disabled={isGenerating}
            className="w-full flex items-center justify-center gap-2 bg-[#007e7a] hover:bg-[#005f5c] disabled:bg-teal-700/60 text-white text-sm font-bold py-4 rounded-2xl transition-all shadow-md cursor-pointer mt-6"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Running AI Pipeline...</span>
              </>
            ) : (
              <>
                <span>Generate AI Case Study</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}