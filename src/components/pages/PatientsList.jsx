import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, User, Calendar, Activity, ChevronRight, Users } from "lucide-react";

export const mockPatientsList = [
  { 
    id: "p001", 
    name: "Eleanor Rigby", 
    age: 65, 
    gender: "Female", 
    patientId: "40261",
    lastVisit: "Oct 24, 2023",
    status: "Stable"
  },
  { 
    id: "p002", 
    name: "Marcus Chen", 
    age: 42, 
    gender: "Male", 
    patientId: "40262",
    lastVisit: "Nov 02, 2023",
    status: "Review"
  },
  { 
    id: "p003", 
    name: "Sarah Rodriguez", 
    age: 28, 
    gender: "Female", 
    patientId: "40263",
    lastVisit: "Nov 15, 2023",
    status: "Critical"
  },
  { 
    id: "p004", 
    name: "James Wilson", 
    age: 55, 
    gender: "Male", 
    patientId: "40264",
    lastVisit: "Nov 20, 2023",
    status: "Stable"
  },
];

export default function PatientsList() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");

  const filteredPatients = mockPatientsList.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    p.patientId.includes(searchQuery)
  );

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-full bg-teal-100 text-[#007e7a] flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
            <h1 className="text-2xl font-extrabold font-display text-slate-900 tracking-tight">
              Patients Directory
            </h1>
          </div>
          <p className="text-sm text-slate-500 font-medium">
            View and manage patient summaries and medical records.
          </p>
        </div>
        
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by name or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#007e7a]/30 focus:border-[#007e7a] transition-all"
          />
        </div>
      </div>

      <div className="space-y-4">
        {filteredPatients.map((patient) => (
          <div 
            key={patient.id}
            onClick={() => navigate(`/patients/${patient.id}`)}
            className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm hover:shadow-md hover:border-[#007e7a]/30 transition-all cursor-pointer group flex flex-col md:flex-row justify-between md:items-center gap-4"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 font-bold text-sm group-hover:bg-[#e6f5f4] group-hover:text-[#007e7a] transition-colors shrink-0">
                {patient.name.split(" ").map(n => n[0]).join("")}
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900 group-hover:text-[#007e7a] transition-colors">
                  {patient.name}
                </h3>
                <div className="flex items-center flex-wrap gap-2 sm:gap-3 text-xs text-slate-500 font-medium mt-1">
                  <span>ID: #{patient.patientId}</span>
                  <span className="hidden sm:block w-1 h-1 rounded-full bg-slate-300"></span>
                  <span className="flex items-center gap-1"><User className="w-3.5 h-3.5" /> {patient.age}Y • {patient.gender}</span>
                  <span className="hidden sm:block w-1 h-1 rounded-full bg-slate-300"></span>
                  <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" /> {patient.lastVisit}</span>
                </div>
              </div>
            </div>

            <div className="flex flex-row md:flex-col items-center md:items-end justify-between md:justify-center gap-3 w-full md:w-auto">
              <span className={`px-3 py-1 rounded-full text-[11px] font-bold border ${
                patient.status === 'Critical' ? 'bg-red-50 text-red-600 border-red-100' :
                patient.status === 'Review' ? 'bg-amber-50 text-amber-600 border-amber-100' :
                'bg-emerald-50 text-emerald-600 border-emerald-100'
              }`}>
                {patient.status}
              </span>
              <div className="flex items-center gap-1 text-xs font-bold text-[#007e7a]">
                <span>View Summary</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </div>
        ))}
        {filteredPatients.length === 0 && (
          <div className="col-span-full py-12 text-center text-slate-500 bg-white rounded-2xl border border-slate-200 border-dashed">
            No patients found matching "{searchQuery}"
          </div>
        )}
      </div>
    </div>
  );
}
