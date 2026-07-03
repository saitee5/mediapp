import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Link } from "react-router-dom";
import {
  Search,
  Bell,
  HelpCircle,
  Headphones,
  ChevronDown,
  AlertTriangle,
} from "lucide-react";


const mockCriticalAlerts = [
  {
    patient: "Sarah Rodriguez",
    issue: "Hypertension follow-up overdue — BP 142/91, medication non-adherence noted",
  },
  {
    patient: "Elena Rodriguez",
    issue: "Potential Eliquis + Lisinopril interaction flagged during live consultation",
  },
  {
    patient: "Marcus Chen",
    issue: "SOAP note still in Draft status 48+ hours after visit",
  },
];

export default function Topbar({ doctorInfo, alertsCount = 0 }) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    console.log("Searching for:", query);
  };

  const handleAlertsClick = () => {
    const message = mockCriticalAlerts
      .map((a) => `• ${a.patient}: ${a.issue}`)
      .join("\n\n");
    window.alert(`${mockCriticalAlerts.length} Critical Alerts\n\n${message}`);
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-6 flex items-center justify-between shrink-0">
     
      <form onSubmit={handleSearchSubmit} className="flex-1 max-w-md">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search patients, charts, or directives..."
            className="w-full pl-9 pr-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#007e7a]/30 focus:border-[#007e7a]/50 transition-all"
          />
        </div>
      </form>

 
      <div className="flex items-center gap-6 ml-6">
        <nav className="hidden md:flex items-center gap-5 text-sm font-semibold text-slate-500">
          <Link
             to="/directives"
                   className="hover:text-slate-800 transition-colors"
          >
              Directives
              </Link>
          <button
            onClick={handleAlertsClick}
            className="flex items-center gap-1.5 hover:text-slate-800 transition-colors"
          >
            Alerts
            {alertsCount > 0 && (
              <span className="w-4 h-4 flex items-center justify-center bg-red-500 text-white text-[10px] font-bold rounded-full">
                {alertsCount}
              </span>
            )}
          </button>
            <Link
             to="/history"
              className="hover:text-slate-800 transition-colors"
            >
            History
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          <button
            onClick={handleAlertsClick}
            className="relative p-2 rounded-xl hover:bg-slate-50 transition-colors"
          >
            <Bell className="w-4.5 h-4.5 text-slate-500" />
            {alertsCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white" />
            )}
          </button>
          <button className="p-2 rounded-xl hover:bg-slate-50 transition-colors">
            <HelpCircle className="w-4.5 h-4.5 text-slate-500" />
          </button>
        </div>

        <button
          onClick={() => navigate("/live-scribe")}
          className="flex items-center gap-2 bg-[#007e7a] hover:bg-[#005f5c] text-white text-sm font-bold px-4 py-2.5 rounded-xl transition-colors shadow-sm"
        >
          <Headphones className="w-4 h-4" />
          Live Listen
        </button>

        <div className="relative">
          <button
            onClick={() => setMenuOpen((v) => !v)}
            className="flex items-center gap-1.5"
          >
            <div className="w-8 h-8 rounded-full bg-slate-200 overflow-hidden flex items-center justify-center text-xs font-bold text-slate-500">
              {(doctorInfo?.name || "DR")
                .split(" ")
                .map((n) => n[0])
                .join("")
                .slice(0, 2)}
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {menuOpen && (
            <div className="absolute right-0 mt-2 w-44 bg-white border border-slate-200 rounded-xl shadow-lg py-1.5 z-10">
              <button className="w-full text-left px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50">
                Profile
              </button>
              <button className="w-full text-left px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50">
                Settings
              </button>
              <button className="w-full text-left px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50">
                Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}