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
  const [visibleLines, setVisibleLines] = useState(0);
  const transcriptEndRef = useRef(null);

  
  useEffect(() => {
    if (!isListening || visibleLines >= mockTranscriptScript.length) return;
    const timer = setTimeout(() => {
      setVisibleLines((v) => v + 1);
    }, 1400);
    return () => clearTimeout(timer);
  }, [isListening, visibleLines]);

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [visibleLines]);

  const handleStart = () => {
    setIsListening(true);
    setVisibleLines(1);
  };

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
            onClick={handleStart}
            disabled={isListening}
            className="mt-6 w-full flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-bold py-3 rounded-xl transition-colors"
          >
            <Play className="w-4 h-4 fill-current" />
            {isListening ? "Consultation In Progress" : "Start Consultation"}
          </button>
        </div>

        {/* Transcript */}
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 flex flex-col h-160">
          <div className="flex items-center gap-2 mb-4">
            {isListening && (
              <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            )}
            <h3 className="font-bold text-slate-800 font-display">
              {isListening ? "Listening..." : "Ready to start"}
            </h3>
          </div>

          <div className="flex-1 overflow-y-auto space-y-4 pr-1">
            {mockTranscriptScript.slice(0, visibleLines).map((line, i) => (
              <div key={i}>
                <p
                  className={`text-xs font-bold mb-1 ${
                    line.speaker === "Doctor" ? "text-slate-700" : "text-[#007e7a]"
                  }`}
                >
                  {line.speaker}
                </p>
                <p className="text-sm text-slate-600 leading-relaxed">{line.text}</p>
              </div>
            ))}
            {!isListening && (
              <p className="text-sm text-slate-400">
                Transcript will appear here once the consultation starts.
              </p>
            )}
            <div ref={transcriptEndRef} />
          </div>
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