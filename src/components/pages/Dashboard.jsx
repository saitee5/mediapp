import React from 'react'
import { useOutletContext } from "react-router-dom";
import {
  Users,
  Calendar,
  FileText,
  AlertTriangle,
  CalendarClock,
  ArrowRight,
  Sparkles
} from 'lucide-react';

export default function Dashboard() {
  const { doctorInfo, onMetricClick, onPatientClick, alertsCount } = useOutletContext();

  const stats = [
    {
      id: 'patients',
      label: 'TOTAL PATIENTS',
      value: '1,248',
      change: '+12%',
      changeType: 'positive',
      icon: Users,
      iconBg: 'bg-indigo-50 text-indigo-600',
    },
    {
      id: 'consults',
      label: "TODAY'S CONSULTS",
      value: '18',
      change: 'Today',
      changeType: 'neutral',
      icon: Calendar,
      iconBg: 'bg-emerald-50 text-emerald-600',
    },
    {
      id: 'soap',
      label: 'SOAP NOTES',
      value: '842',
      change: '98% Auto',
      changeType: 'positive',
      icon: FileText,
      iconBg: 'bg-amber-50 text-amber-600',
    },
    {
      id: 'alerts',
      label: 'DRUG ALERTS',
      value: alertsCount.toString(),
      change: 'Critical',
      changeType: 'negative',
      icon: AlertTriangle,
      iconBg: 'bg-red-50 text-red-600',
      badgeDot: true,
    },
  ];

  const recentPatients = [
    {
      id: 'p001',
      initials: 'EH',
      name: 'Elena Hayes',
      age: 42,
      diagnosis: 'Type 2 Diabetes Mellitus',
      visitDate: 'Oct 24, 10:15 AM',
      status: 'Completed',
      statusClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
    {
      id: 'p002',
      initials: 'MC',
      name: 'Marcus Chen',
      age: 29,
      diagnosis: 'Acute Sinusitis',
      visitDate: 'Oct 24, 09:30 AM',
      status: 'Draft',
      statusClass: 'bg-slate-100 text-slate-700 border-slate-200',
    },
    {
      id: 'p003',
      initials: 'SR',
      name: 'Sarah Rodriguez',
      age: 64,
      diagnosis: 'Hypertension - Follow-up',
      visitDate: 'Oct 23, 04:45 PM',
      status: 'Action Required',
      statusClass: 'bg-red-50 text-red-700 border-red-200 animate-pulse',
    },
    {
      id: 'p004',
      initials: 'JW',
      name: 'James Wilson',
      age: 51,
      diagnosis: 'Osteoarthritis Knee',
      visitDate: 'Oct 23, 02:00 PM',
      status: 'Completed',
      statusClass: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold font-display text-slate-900 tracking-tight">
            Clinical Overview
          </h1>
          <p className="text-sm text-slate-500 font-medium mt-1">
            Here's what requires your attention today, {doctorInfo?.name || 'Dr. Vance'}.
          </p>
        </div>
        <div className="flex items-center gap-2.5 px-4 py-2.5 bg-white border border-slate-200 rounded-2xl shadow-sm text-sm font-semibold text-slate-700 select-none">
          <CalendarClock className="w-4 h-4 text-slate-400" />
          <span>Oct 24, 2023</span>
        </div>
      </div>

      {/* Grid of Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.id}
              onClick={() => onMetricClick(stat.id)}
              className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm hover:shadow-md hover:border-slate-300 transition-all duration-300 cursor-pointer flex flex-col justify-between h-40 group relative overflow-hidden"
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-slate-400 tracking-wider uppercase">
                  {stat.label}
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 ${
                    stat.changeType === 'positive'
                      ? 'bg-emerald-50 text-emerald-700'
                      : stat.changeType === 'negative'
                      ? 'bg-red-50 text-red-700'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {stat.badgeDot && <span className="w-1.5 h-1.5 bg-red-600 rounded-full"></span>}
                  {stat.change}
                </span>
              </div>
              <div className="flex items-end justify-between mt-4">
                <span className="text-4xl font-extrabold font-display text-slate-900 group-hover:scale-105 transition-transform duration-300 origin-left">
                  {stat.value}
                </span>
                <div className={`p-3 rounded-2xl ${stat.iconBg} transform group-hover:-translate-y-1 transition-transform`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm lg:col-span-2 flex flex-col justify-between min-h-90">
          <div>
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-bold text-slate-800 tracking-tight font-display text-lg">
                Weekly Consultations
              </h3>
              <div className="flex items-center gap-4 text-xs font-semibold text-slate-500">
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 bg-slate-900 rounded-full"></span>
                  In-Person
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 bg-[#007e7a] rounded-full"></span>
                  Telehealth
                </span>
              </div>
            </div>
            <div className="relative w-full h-48 mt-4">
              <svg className="w-full h-full" viewBox="0 0 600 200" preserveAspectRatio="none">
                <line x1="0" y1="50" x2="600" y2="50" stroke="#f1f5f9" strokeWidth="1" strokeDasharray="4 4" />
                <line x1="0" y1="100" x2="600" y2="100" stroke="#f1f5f9" strokeWidth="1" strokeDasharray="4 4" />
                <line x1="0" y1="150" x2="600" y2="150" stroke="#f1f5f9" strokeWidth="1" strokeDasharray="4 4" />
                <path d="M 50 140 Q 175 110, 300 80 T 550 50" fill="none" stroke="#0f172a" strokeWidth="3.5" strokeLinecap="round" />
                <path d="M 50 160 Q 175 90, 300 120 T 550 60" fill="none" stroke="#007e7a" strokeWidth="3.5" strokeLinecap="round" />
                <circle cx="50" cy="140" r="4.5" fill="#0f172a" stroke="#fff" strokeWidth="2" />
                <circle cx="50" cy="160" r="4.5" fill="#007e7a" stroke="#fff" strokeWidth="2" />
                <circle cx="175" cy="125" r="4.5" fill="#0f172a" stroke="#fff" strokeWidth="2" />
                <circle cx="175" cy="110" r="4.5" fill="#007e7a" stroke="#fff" strokeWidth="2" />
                <circle cx="300" cy="80" r="4.5" fill="#0f172a" stroke="#fff" strokeWidth="2" />
                <circle cx="300" cy="120" r="4.5" fill="#007e7a" stroke="#fff" strokeWidth="2" />
                <circle cx="425" cy="65" r="4.5" fill="#0f172a" stroke="#fff" strokeWidth="2" />
                <circle cx="425" cy="90" r="4.5" fill="#007e7a" stroke="#fff" strokeWidth="2" />
                <circle cx="550" cy="50" r="4.5" fill="#0f172a" stroke="#fff" strokeWidth="2" />
                <circle cx="550" cy="60" r="4.5" fill="#007e7a" stroke="#fff" strokeWidth="2" />
              </svg>
              <div className="flex justify-between px-10 text-[10px] font-bold text-slate-400 mt-2">
                <span>MON</span>
                <span>TUE</span>
                <span>WED</span>
                <span>THU</span>
                <span>FRI</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-sm flex flex-col justify-between min-h-90">
          <div>
            <h3 className="font-bold text-slate-800 tracking-tight font-display text-lg mb-6">
              SOAP Notes Generated
            </h3>
            <div className="space-y-5">
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-500">Drafted</span>
                  <span className="text-slate-800">12 Notes</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                  <div className="bg-teal-400 h-full rounded-full" style={{ width: '35%' }}></div>
                </div>
              </div>
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-500">Action Required</span>
                  <span className="text-red-600">3 Notes</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                  <div className="bg-red-500 h-full rounded-full" style={{ width: '15%' }}></div>
                </div>
              </div>
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-500">Finalized</span>
                  <span className="text-slate-800">82 Notes</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                  <div className="bg-[#007e7a] h-full rounded-full" style={{ width: '85%' }}></div>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-6 p-4 bg-[#e6f5f4] rounded-2xl border border-[#b2dfdb]/45 flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-[#007e7a] shrink-0 mt-0.5" />
            <p className="text-xs font-medium text-slate-700 leading-relaxed">
              AI Ambient transcription has saved you approximately{' '}
              <strong className="text-[#007e7a] font-bold">4.2 hours</strong> this week.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
          <h3 className="font-bold text-slate-800 tracking-tight font-display text-lg">
            Recent Patients
          </h3>
          <button
            onClick={() => onPatientClick(null)}
            className="flex items-center gap-1 text-xs font-bold text-[#007e7a] hover:text-[#005f5c] transition-colors cursor-pointer"
          >
            <span>View All Patients</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-[10px] font-bold text-slate-400 tracking-wider border-b border-slate-100">
                <th className="px-6 py-4">PATIENT NAME</th>
                <th className="px-6 py-4">AGE</th>
                <th className="px-6 py-4">DIAGNOSIS</th>
                <th className="px-6 py-4">VISIT DATE</th>
                <th className="px-6 py-4">STATUS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {recentPatients.map((patient, index) => (
                <tr
                  key={index}
                  onClick={() => onPatientClick(patient)}
                  className="hover:bg-slate-50/70 transition-colors cursor-pointer group"
                >
                  <td className="px-6 py-4 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center font-bold text-xs">
                      {patient.initials}
                    </div>
                    <span className="font-semibold text-slate-800 group-hover:text-[#007e7a] transition-colors">
                      {patient.name}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-600 font-medium">{patient.age}</td>
                  <td className="px-6 py-4 text-slate-600 font-medium truncate max-w-55">
                    {patient.diagnosis}
                  </td>
                  <td className="px-6 py-4 text-slate-500 font-medium">{patient.visitDate}</td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-block px-2.5 py-1 rounded-full text-xs font-bold border ${patient.statusClass}`}
                    >
                      {patient.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}