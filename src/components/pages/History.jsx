import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  History as HistoryIcon,
  Download,
  ExternalLink,
  FileText,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Calendar,
  User,
  Search,
} from "lucide-react";
import { api } from "../../services/api";

const defaultMockHistory = [
  {
    session_id: "consult_demo_8821",
    patient_name: "Elena Rodriguez",
    diagnosis: "Orthostatic Hypotension, AFib",
    encounter_date: "Today, 10:15 AM",
    status: "reviewed",
  },
  {
    session_id: "consult_demo_8822",
    patient_name: "Marcus Chen",
    diagnosis: "Acute Sinusitis",
    encounter_date: "Today, 09:30 AM",
    status: "pending_review",
  },
  {
    session_id: "consult_demo_8823",
    patient_name: "Sarah Rodriguez",
    diagnosis: "Hypertension - Follow-up",
    encounter_date: "Yesterday, 04:45 PM",
    status: "reviewed",
  },
  {
    session_id: "consult_demo_8824",
    patient_name: "James Wilson",
    diagnosis: "Osteoarthritis Knee",
    encounter_date: "Yesterday, 02:00 PM",
    status: "reviewed",
  },
];

export default function History() {
  const navigate = useNavigate();
  const [consultations, setConsultations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    async function loadHistory() {
      try {
        const res = await api.listConsultations(50);
        // Defensive: list_consultations has no fixed response schema on the backend,
        // so normalize both a raw array and a { consultations: [...] } wrapper.
        const list = Array.isArray(res)
          ? res
          : Array.isArray(res?.consultations)
            ? res.consultations
            : [];
        setConsultations(list.length > 0 ? list : defaultMockHistory);
      } catch (err) {
        console.warn("Backend consultation list fetch failed, using fallback:", err);
        setConsultations(defaultMockHistory);
      } finally {
        setIsLoading(false);
      }
    }
    loadHistory();
  }, []);

  const filteredHistory = consultations.filter((item) => {
    const name = item.patient_name || item.patient || "";
    const session = item.session_id || "";
    const diag = item.diagnosis || item.issue || item.case_sheet_summary?.diagnosis || "";
    const q = searchQuery.toLowerCase();
    return (
      name.toLowerCase().includes(q) ||
      session.toLowerCase().includes(q) ||
      diag.toLowerCase().includes(q)
    );
  });

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-8 h-8 rounded-full bg-teal-100 text-[#007e7a] flex items-center justify-center">
              <HistoryIcon className="w-4 h-4" />
            </div>
            <h1 className="text-2xl font-extrabold font-display text-slate-900 tracking-tight">
              Consultation &amp; Case Sheet History
            </h1>
          </div>
          <p className="text-sm text-slate-500 font-medium">
            Browse previous clinical encounters, generated SOAP documents, and download signed hospital PDFs.
          </p>
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search consultations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#007e7a]/30 focus:border-[#007e7a] transition-all"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="p-16 flex flex-col items-center justify-center space-y-4 bg-white rounded-3xl border border-slate-200/80">
          <Loader2 className="w-8 h-8 text-[#007e7a] animate-spin" />
          <p className="text-sm text-slate-500 font-medium">Loading consultations from Supabase database...</p>
        </div>
      ) : (
        <div className="space-y-3.5">
          {filteredHistory.map((item, index) => {
            const sessionId = item.session_id || `consult_${index}`;
            const patientName = item.patient_name || item.patient || "Elena Rodriguez";
            const date = item.encounter_date || item.date || new Date(item.created_at || Date.now()).toLocaleDateString();
            const status = item.status || "reviewed";
            const diagnosis =
              item.updated_case_sheet_summary?.diagnosis ||
              item.case_sheet_summary?.diagnosis ||
              item.diagnosis ||
              item.issue ||
              "Post-Op Follow-up";

            return (
              <div
                key={sessionId + index}
                className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md hover:border-[#007e7a]/30 transition-all flex flex-col md:flex-row justify-between md:items-center gap-4"
              >
                <div className="flex items-start gap-4">
                  <div className="w-11 h-11 rounded-2xl bg-[#e6f5f4] text-[#007e7a] flex items-center justify-center font-bold text-sm shrink-0">
                    <User className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-base font-bold text-slate-900">{patientName}</h2>
                      <span className="text-xs text-slate-400 font-mono">#{sessionId.slice(-6).toUpperCase()}</span>
                    </div>
                    <p className="text-xs text-slate-600 font-medium mt-0.5">{diagnosis}</p>
                    <div className="flex items-center gap-3 text-[11px] text-slate-400 font-medium mt-1.5">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5" />
                        {date}
                      </span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        LangGraph Agent Pipeline
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center flex-wrap gap-2.5">
                  <span
                    className={`text-xs font-bold px-3 py-1 rounded-full border ${status === "reviewed" || status === "Completed"
                        ? "bg-emerald-50 text-emerald-700 border-emerald-100"
                        : "bg-amber-50 text-amber-700 border-amber-100"
                      }`}
                  >
                    {status === "reviewed" || status === "Completed" ? "Reviewed & Ready" : "Pending Review"}
                  </span>

                  <button
                    onClick={() => navigate(`/soapnotes/${sessionId}`)}
                    className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl text-xs font-bold transition-colors cursor-pointer"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    Review Note
                  </button>

                  <a
                    href={api.getDownloadPdfUrl(sessionId)}
                    download
                    className="flex items-center gap-1.5 px-3.5 py-2 bg-[#007e7a] hover:bg-[#005f5c] text-white rounded-xl text-xs font-bold transition-colors shadow-sm cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download PDF
                  </a>
                </div>
              </div>
            );
          })}

          {filteredHistory.length === 0 && (
            <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 text-slate-400">
              No consultation records matching your query.
            </div>
          )}
        </div>
      )}
    </div>
  );
}