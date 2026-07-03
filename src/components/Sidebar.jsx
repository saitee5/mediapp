import { NavLink } from "react-router-dom";
import {
  LayoutGrid,
  Users,
  Mic,
  FileText,
  Plus,
  Settings,
  HelpCircle,
} from "lucide-react";


const navItems = [
  { to: "/Dashboard", label: "Dashboard", icon: LayoutGrid },
  { to: "/patients/p001", label: "Patients", icon: Users },
  { to: "/live-scribe", label: "Live Scribe", icon: Mic },
  { to: "/soapnotes/n001", label: "SOAP Notes", icon: FileText },
];

export default function Sidebar({ doctorInfo }) {
  return (
    <aside className="w-64 h-screen bg-white border-r border-slate-200/80 flex flex-col shrink-0">
    
      <div className="flex items-center gap-3 px-6 py-6">
        <div className="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center text-white font-bold text-sm">
          AS
        </div>
        <div>
          <p className="font-bold text-slate-900 font-display text-sm leading-tight">
            Ambient Scribe
          </p>
          <p className="text-[11px] text-slate-400 font-medium">
            Clinical Assistant
          </p>
        </div>
      </div>

      
      <nav className="flex-1 px-3 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-colors ${
                isActive
                  ? "bg-[#e6f5f4] text-[#007e7a]"
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-700"
              }`
            }
          >
            <Icon className="w-4.5 h-4.5" />
            {label}
          </NavLink>
        ))}
      </nav>

    
      <div className="px-3 mb-4">
        <NavLink
          to="/live-scribe"
          className="w-full flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-white text-sm font-bold py-3 rounded-xl transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Consultation
        </NavLink>
      </div>

      
      <div className="px-3 space-y-1 mb-4">
        <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-500 hover:bg-slate-50 hover:text-slate-700 transition-colors">
          <Settings className="w-4.5 h-4.5" />
          Settings
        </button>
        <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-500 hover:bg-slate-50 hover:text-slate-700 transition-colors">
          <HelpCircle className="w-4.5 h-4.5" />
          Support
        </button>
      </div>

  
      <div className="border-t border-slate-100 px-4 py-4 flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-slate-200 overflow-hidden shrink-0">
          {doctorInfo?.avatarUrl ? (
            <img
              src={doctorInfo.avatarUrl}
              alt={doctorInfo?.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-xs font-bold text-slate-500">
              {(doctorInfo?.name || "DR")
                .split(" ")
                .map((n) => n[0])
                .join("")
                .slice(0, 2)}
            </div>
          )}
        </div>
        <div>
          <p className="text-sm font-bold text-slate-800 leading-tight">
            {doctorInfo?.name || "Dr. Julian Vance"}
          </p>
          <p className="text-[11px] font-semibold text-emerald-600 flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
            ON DUTY
          </p>
        </div>
      </div>
    </aside>
  );
}