import { useParams, useNavigate } from "react-router-dom";
import {
  ChevronRight,
  Download,
  Share2,
  Stethoscope,
  CalendarClock,
  Dumbbell,
  Utensils,
  AlertTriangle,
} from "lucide-react";


const mockPatients = {
  p001: {
    id: "p001",
    name: "Eleanor Rigby",
    dob: "12/04/1959",
    age: 65,
    patientId: "40261",
    reportDate: "October 24, 2023",
    physician: "J. Vance, MD",
    physicianTitle: "Faculty, St. Jude Medical Center",
    diagnosis: {
      name: "Type 2 Diabetes Mellitus",
      description:
        "Managed with mild hypertension and hyperlipidemia. Patient currently experiencing moderate glycemic fluctuation.",
      tags: [
        { label: "Chronic", tone: "neutral" },
        { label: "High Priority", tone: "danger" },
      ],
    },
    followUp: {
      title: "Endocrinology Review",
      date: "Jan 14, 6:30 PM",
      note: "Fasting blood work required 48 hrs prior. Bring current glucometer for data sync.",
    },
    medications: [
      { name: "Metformin HCl", dosage: "500 mg", frequency: "Twice daily", instructions: "Take with meals to minimize GI distress." },
      { name: "Lisinopril", dosage: "10 mg", frequency: "Once daily", instructions: "Take in the morning. Monitor for dry cough." },
      { name: "Atorvastatin", dosage: "20 mg", frequency: "Once daily", instructions: "At bedtime. Avoid grapefruit juice." },
    ],
    lifestyle: {
      activity: "Aim for 30 minutes of brisk walking 5 days a week. Resistance training twice weekly.",
      diet: "Increase fiber intake. Limit simple carbohydrates and processed sugars. Mediterranean diet focus.",
      warningSigns: "Contact office immediately if experiencing persistent dizziness, blurred vision, or numbness in extremities.",
    },
    vitalsTrend: [62, 70, 74, 80, 92],
    scribeConfidence: 98.4,
  },
};

export default function PatientSummary() {
  const { id } = useParams();
  const navigate = useNavigate();
  const patient = mockPatients[id];

  if (!patient) {
    return (
      <div className="p-8 max-w-3xl mx-auto text-center">
        <p className="text-slate-500 font-medium mb-4">Patient not found.</p>
        <button
          onClick={() => navigate("/Dashboard")}
          className="text-sm font-bold text-[#007e7a] hover:underline"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 mb-2">
            <button onClick={() => navigate("/patients")} className="hover:text-slate-600 transition-colors">
              Patients
            </button>
            <ChevronRight className="w-3 h-3" />
            <span className="text-slate-500">{patient.name}</span>
          </div>
          <h1 className="text-2xl font-extrabold font-display text-slate-900 tracking-tight">
            Patient Summary
          </h1>
        </div>
        <div className="flex items-center gap-2.5">
          <button className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors shadow-sm">
            <Download className="w-4 h-4" />
            Download PDF
          </button>
          <button className="flex items-center gap-2 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 rounded-xl text-sm font-semibold text-white transition-colors shadow-sm">
            <Share2 className="w-4 h-4" />
            Share to Patient Portal
          </button>
        </div>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-8 space-y-8">
       <div className="flex items-start justify-between pb-6 border-b border-slate-100">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-500 flex items-center justify-center shrink-0">
              <Stethoscope className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-bold text-slate-900 font-display text-lg leading-tight">
                {patient.name}
              </h2>
              <p className="text-xs text-slate-500 font-medium mt-0.5">
                DOB: {patient.dob} ({patient.age}Y) &nbsp;•&nbsp; ID #{patient.patientId}
              </p>
            </div>
          </div>
          <p className="text-xs font-semibold text-slate-400 mt-1">{patient.reportDate}</p>
        </div>

        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-50 rounded-2xl p-5">
            <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-3 flex items-center gap-1.5">
              <Stethoscope className="w-3.5 h-3.5" />
              Clinical Diagnosis
            </p>
            <h3 className="font-bold text-slate-900 text-sm mb-2">{patient.diagnosis.name}</h3>
            <p className="text-xs text-slate-500 leading-relaxed mb-3">
              {patient.diagnosis.description}
            </p>
            <div className="flex flex-wrap gap-2">
              {patient.diagnosis.tags.map((tag) => (
                <span
                  key={tag.label}
                  className={`px-2.5 py-1 rounded-full text-[11px] font-bold ${
                    tag.tone === "danger"
                      ? "bg-red-50 text-red-700"
                      : "bg-slate-200/70 text-slate-600"
                  }`}
                >
                  {tag.label}
                </span>
              ))}
            </div>
          </div>

          <div className="bg-slate-50 rounded-2xl p-5">
            <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-3 flex items-center gap-1.5">
              <CalendarClock className="w-3.5 h-3.5" />
              Follow-up Plan
            </p>
            <h3 className="font-bold text-slate-900 text-sm mb-1">{patient.followUp.title}</h3>
            <p className="text-xs font-bold text-[#007e7a] mb-2">{patient.followUp.date}</p>
            <p className="text-xs text-slate-500 leading-relaxed">{patient.followUp.note}</p>
          </div>
        </div>

     
        <div>
          <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-3">
            Active Medications &amp; Dosage
          </p>
          <div className="overflow-x-auto rounded-2xl border border-slate-100">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 text-[10px] font-bold text-slate-400 tracking-wider">
                  <th className="px-4 py-3">MEDICATION</th>
                  <th className="px-4 py-3">DOSAGE</th>
                  <th className="px-4 py-3">FREQUENCY</th>
                  <th className="px-4 py-3">INSTRUCTIONS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {patient.medications.map((med) => (
                  <tr key={med.name}>
                    <td className="px-4 py-3 font-semibold text-slate-800">{med.name}</td>
                    <td className="px-4 py-3 text-slate-600">{med.dosage}</td>
                    <td className="px-4 py-3 text-slate-600">{med.frequency}</td>
                    <td className="px-4 py-3 text-slate-500">{med.instructions}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

       
        <div>
          <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-3">
            Lifestyle Advice &amp; Notes
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex gap-2.5">
              <Dumbbell className="w-4 h-4 text-[#007e7a] shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-slate-700 mb-1">Physical Activity</p>
                <p className="text-xs text-slate-500 leading-relaxed">{patient.lifestyle.activity}</p>
              </div>
            </div>
            <div className="flex gap-2.5">
              <Utensils className="w-4 h-4 text-[#007e7a] shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-slate-700 mb-1">Dietary Habits</p>
                <p className="text-xs text-slate-500 leading-relaxed">{patient.lifestyle.diet}</p>
              </div>
            </div>
            <div className="flex gap-2.5">
              <AlertTriangle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-red-600 mb-1">Warning Signs</p>
                <p className="text-xs text-slate-500 leading-relaxed">{patient.lifestyle.warningSigns}</p>
              </div>
            </div>
          </div>
        </div>

      
        <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
          <div>
            <p className="font-bold text-slate-800 text-sm italic">{patient.physician}</p>
            <p className="text-xs text-slate-400">{patient.physicianTitle}</p>
          </div>
          <p className="text-[11px] text-slate-400">
            Electronically signed {patient.reportDate}
          </p>
        </div>
      </div>

      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6">
          <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-4">
            Recent Vitals Trend
          </p>
          <div className="flex items-end gap-2 h-24">
            {patient.vitalsTrend.map((val, i) => (
              <div
                key={i}
                className={`flex-1 rounded-lg ${
                  i === patient.vitalsTrend.length - 1 ? "bg-[#007e7a]" : "bg-teal-100"
                }`}
                style={{ height: `${val}%` }}
              />
            ))}
          </div>
        </div>

        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 flex items-center justify-between">
          <div>
            <p className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-2">
              Scribe Confidence Score
            </p>
            <p className="text-2xl font-extrabold text-[#007e7a]">
              {patient.scribeConfidence}%
            </p>
            <p className="text-xs text-slate-400 font-medium mt-1">Approved</p>
          </div>
          <div className="relative w-14 h-14 shrink-0">
            <svg viewBox="0 0 36 36" className="w-14 h-14 -rotate-90">
              <circle cx="18" cy="18" r="16" fill="none" stroke="#e2e8f0" strokeWidth="3" />
              <circle
                cx="18"
                cy="18"
                r="16"
                fill="none"
                stroke="#007e7a"
                strokeWidth="3"
                strokeDasharray={`${(patient.scribeConfidence / 100) * 100.5} 100.5`}
                strokeLinecap="round"
              />
            </svg>
          </div>
        </div>
      </div>

     
      <p className="text-center text-[11px] text-slate-400">
        Confidential Patient Information • HIPAA Compliant Storage • Ambient Clinical Scribe v2.4
      </p>
    </div>
  );
}