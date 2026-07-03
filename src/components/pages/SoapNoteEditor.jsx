import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ClipboardList,
  CalendarDays,
  Fingerprint,
  FilePlus2,
  Timer,
  Sparkles,
  Bold,
  Italic,
  List,
  ListOrdered,
  Link2,
  Image as ImageIcon,
  Download,
  Pencil,
  CheckCheck,
  CheckCircle2,
  Lock,
} from "lucide-react";


const mockNotes = {
  n001: {
    patientName: "Selena Gomez",
    visitDate: "Oct 24, 2023",
    recordId: "#SG-9921",
    type: "Follow-up",
    status: "Drafting",
    lastSaved: "2m ago",
    scribedBy: "Ambient AI",
    reviewedBy: "Nurse Emma",
    sections: {
      subjective:
        "Patient reports persistent palpitations occurring 3-4 times daily, typically lasting 5-10 minutes.\n\nStates the episodes are often associated with mild shortness of breath but denies syncope, lightheadedness, or chest pain. Noted an increase in caffeine intake recently due to work stress.\n\nSleep hygiene has been poor, averaging 5 hours per night.",
      objective:
        "BP 118/76, HR 88 bpm (irregular), RR 16, Temp 98.4°F. Cardiac auscultation reveals occasional ectopic beats, no murmurs. Lungs clear bilaterally. No peripheral edema.",
      assessment:
        "Palpitations, likely related to caffeine intake and poor sleep hygiene versus underlying atrial ectopy. Rule out paroxysmal arrhythmia given irregular rhythm on exam.",
      plan:
        "Order 24-hour Holter monitor. Advise reducing caffeine intake and improving sleep hygiene. Follow up in 2 weeks or sooner if symptoms worsen.",
    },
  },
};

const tabs = [
  { key: "subjective", label: "Subjective" },
  { key: "objective", label: "Objective" },
  { key: "assessment", label: "Assessment" },
  { key: "plan", label: "Plan" },
];

export default function SoapNoteEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const note = mockNotes[id];

  const [activeTab, setActiveTab] = useState("subjective");
  const [sections, setSections] = useState(note?.sections || null);
  const [isEditing, setIsEditing] = useState(false);
  const [status, setStatus] = useState(note?.status);

  if (!note || !sections) {
    return (
      <div className="p-8 max-w-3xl mx-auto text-center">
        <p className="text-slate-500 font-medium mb-4">SOAP note not found.</p>
        <button
          onClick={() => navigate("/Dashboard")}
          className="text-sm font-bold text-[#007e7a] hover:underline"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  const handleChange = (value) => {
    setSections((prev) => ({ ...prev, [activeTab]: value }));
  };

  const handleApprove = () => {
    setStatus("Finalized");
    setIsEditing(false);
  };

  const statusStyle =
    status === "Finalized"
      ? "bg-emerald-50 text-emerald-700"
      : status === "Action Required"
      ? "bg-red-50 text-red-700"
      : "bg-[#e6f5f4] text-[#007e7a]";

  return (
    <div className="max-w-6xl mx-auto p-8 space-y-6">
      {/* Patient header row */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#e6f5f4] text-[#007e7a] flex items-center justify-center shrink-0">
            <ClipboardList className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-400">Patient</p>
            <h1 className="text-xl font-extrabold font-display text-slate-900 leading-tight">
              {note.patientName}
            </h1>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="flex items-center gap-3 bg-white rounded-2xl border border-slate-200/80 shadow-sm px-4 py-3.5">
          <div className="w-9 h-9 rounded-xl bg-[#e6f5f4] text-[#007e7a] flex items-center justify-center shrink-0">
            <CalendarDays className="w-4 h-4" />
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase">Visit Date</p>
            <p className="text-sm font-bold text-slate-800">{note.visitDate}</p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-white rounded-2xl border border-slate-200/80 shadow-sm px-4 py-3.5">
          <div className="w-9 h-9 rounded-xl bg-[#e6f5f4] text-[#007e7a] flex items-center justify-center shrink-0">
            <Fingerprint className="w-4 h-4" />
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase">ID</p>
            <p className="text-sm font-bold text-slate-800">{note.recordId}</p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-white rounded-2xl border border-slate-200/80 shadow-sm px-4 py-3.5">
          <div className="w-9 h-9 rounded-xl bg-[#e6f5f4] text-[#007e7a] flex items-center justify-center shrink-0">
            <FilePlus2 className="w-4 h-4" />
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase">Type</p>
            <p className="text-sm font-bold text-slate-800">{note.type}</p>
          </div>
        </div>

        <div className="flex items-center gap-3 bg-white rounded-2xl border border-slate-200/80 shadow-sm px-4 py-3.5">
          <div className="w-9 h-9 rounded-xl bg-[#e6f5f4] text-[#007e7a] flex items-center justify-center shrink-0">
            <Timer className="w-4 h-4" />
          </div>
          <div>
            <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase">Status</p>
            <span className={`inline-block text-xs font-bold px-2 py-0.5 rounded-full ${statusStyle}`}>
              {status}
            </span>
          </div>
        </div>
      </div>

      
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="flex items-center justify-between px-6 pt-5 border-b border-slate-100">
          <div className="flex items-center gap-6">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-1.5 pb-4 text-sm font-bold border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? "text-[#007e7a] border-[#007e7a]"
                    : "text-slate-400 border-transparent hover:text-slate-600"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
          <span className="hidden sm:flex items-center gap-1.5 mb-4 px-3 py-1.5 bg-[#e6f5f4] text-[#007e7a] text-[11px] font-bold rounded-full">
            <Sparkles className="w-3.5 h-3.5" />
            AI GENERATED
          </span>
        </div>

        <div className="flex items-center justify-between px-6 py-3 border-b border-slate-100">
          <div className="flex items-center gap-1 text-slate-500">
            <button className="p-1.5 rounded-lg hover:bg-slate-100 transition-colors">
              <Bold className="w-4 h-4" />
            </button>
            <button className="p-1.5 rounded-lg hover:bg-slate-100 transition-colors">
              <Italic className="w-4 h-4" />
            </button>
            <button className="p-1.5 rounded-lg hover:bg-slate-100 transition-colors">
              <List className="w-4 h-4" />
            </button>
            <button className="p-1.5 rounded-lg hover:bg-slate-100 transition-colors">
              <ListOrdered className="w-4 h-4" />
            </button>
            <span className="w-px h-4 bg-slate-200 mx-1.5" />
            <button className="p-1.5 rounded-lg hover:bg-slate-100 transition-colors">
              <Link2 className="w-4 h-4" />
            </button>
            <button className="p-1.5 rounded-lg hover:bg-slate-100 transition-colors">
              <ImageIcon className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-slate-400 font-medium">Last saved {note.lastSaved}</p>
        </div>

        
        <div className="px-6 py-6 min-h-70">
          {isEditing ? (
            <textarea
              value={sections[activeTab]}
              onChange={(e) => handleChange(e.target.value)}
              rows={10}
              className="w-full text-sm text-slate-700 leading-relaxed focus:outline-none resize-y"
              autoFocus
            />
          ) : (
            <div className="space-y-4">
              {sections[activeTab].split("\n\n").map((para, i) => (
                <p key={i} className="text-sm text-slate-700 leading-relaxed">
                  {para}
                </p>
              ))}
            </div>
          )}
        </div>

       
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-6 py-5 bg-slate-50 border-t border-slate-100">
          <div className="flex items-center gap-2 text-sm font-semibold text-emerald-700">
            <CheckCircle2 className="w-4 h-4" />
            Ready for physician review
          </div>
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors shadow-sm">
              <Download className="w-4 h-4" />
              Export PDF
            </button>
            <button
              onClick={() => setIsEditing((v) => !v)}
              className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors shadow-sm"
            >
              <Pencil className="w-4 h-4" />
              {isEditing ? "Done" : "Edit"}
            </button>
            <button
              onClick={handleApprove}
              className="flex items-center gap-2 px-4 py-2.5 bg-[#007e7a] hover:bg-[#005f5c] rounded-xl text-sm font-bold text-white transition-colors shadow-sm"
            >
              <CheckCheck className="w-4 h-4" />
              Approve Note
            </button>
          </div>
        </div>
      </div>

      
      <div className="flex flex-wrap items-center justify-between gap-3 px-1">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center text-[10px] font-bold text-slate-500">
            AI
          </div>
          <p className="text-xs text-slate-500 font-medium">
            Scribed by {note.scribedBy}, Reviewed by {note.reviewedBy}
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
          <Lock className="w-3.5 h-3.5" />
          HIPAA Compliant Session
        </div>
      </div>
    </div>
  );
}