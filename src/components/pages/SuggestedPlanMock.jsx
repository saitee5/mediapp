import { useState, useRef } from "react";
import { 
  AlertTriangle, Download, ShieldAlert, Info, 
  Calendar, Fingerprint, FilePlus, Clock, 
  Bold, Italic, List, ListOrdered, Link2, Image as ImageIcon, Sparkles, ClipboardList,
  ChevronDown, ChevronUp
} from "lucide-react";

export default function SuggestedPlanMock() {
  const [activeTab, setActiveTab] = useState('soap');
  const [isGeneratingAll, setIsGeneratingAll] = useState(false);
  const [isAlertsOpen, setIsAlertsOpen] = useState(false);
  const fileInputRef = useRef(null);
  
  // Advanced alerts mock data
  const [alerts, setAlerts] = useState([
    {
      id: 1,
      type: "critical",
      title: "Severe Drug-Drug Interaction",
      description: "Lisinopril and existing Potassium supplements may cause hyperkalemia. Consider alternative.",
      icon: ShieldAlert,
      color: "red",
      actionText: "Review"
    },
    {
      id: 2,
      type: "warning",
      title: "Missing Clinical Information",
      description: "Patient's recent creatinine levels are missing.",
      icon: AlertTriangle,
      color: "amber",
      actionText: "Request Labs"
    }
  ]);

  const tabs = [
    { id: 'soap', label: 'SOAP Notes' },
    { id: 'summary', label: 'Patient Visit Summary' },
    { id: 'referral', label: 'Discharge Report / Referral' },
    { id: 'instructions', label: 'Discharge Instructions' },
  ];

  const [documents, setDocuments] = useState({
    soap: `Subjective:\nPatient complains of severe headaches and mild chest pain.\n\nObjective:\nBP: 140/90, HR: 88, Temp: 98.6F\n\nAssessment:\nHypertension, Tension Headache\n\nPlan:\n1. Prescribe Lisinopril 10mg daily.\n2. Recommend OTC pain relievers (Acetaminophen).\n3. Schedule follow-up ECG next week.`,
    summary: `Patient: Selena Gomez\nDate: 2023-10-24\n\nReason for Visit: Follow-up for hypertension and headaches.\n\nSummary of Visit:\nPatient was seen for ongoing headaches and mild chest pain. Vitals were taken and showed elevated blood pressure. A treatment plan involving Lisinopril and Acetaminophen was discussed and agreed upon. Follow-up is scheduled for next week.`,
    referral: `Referral Letter / Discharge Report\n\nTo: Cardiology Department\nFrom: Dr. Smith\n\nPatient Selena Gomez is being referred for a follow-up ECG due to mild chest pain and elevated blood pressure. Please evaluate for any underlying cardiac conditions.`,
    instructions: `Discharge Instructions for Selena Gomez:\n\n1. Take Lisinopril 10mg once daily in the morning.\n2. Take Acetaminophen as needed for headaches, not exceeding 3000mg per day.\n3. Monitor blood pressure daily and keep a log.\n4. Return to the clinic if chest pain worsens or becomes severe.`
  });

  const handleTextChange = (e) => {
    setDocuments({
      ...documents,
      [activeTab]: e.target.value
    });
  };

  const handleGenerateAllPDFs = () => {
    setIsGeneratingAll(true);
    setTimeout(() => {
      setIsGeneratingAll(false);
      alert("All 4 PDFs Generated Successfully!");
    }, 1500);
  };
  
  const dismissAlert = (id) => {
    setAlerts(alerts.filter(a => a.id !== id));
  };

  const handleImageClick = () => {
    // Mock opening a file picker
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 bg-white min-h-screen font-sans text-slate-800">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold font-display text-slate-900 tracking-tight">
            Review Generated Documents
          </h1>
          <p className="text-sm text-slate-500 font-medium mt-2">
            Review the 4 generated documents, resolve clinical alerts, and finalize the paperwork.
          </p>
        </div>
        <button
          onClick={handleGenerateAllPDFs}
          disabled={isGeneratingAll}
          className="flex items-center justify-center gap-2 bg-[#007e7a] hover:bg-[#005f5c] disabled:bg-teal-700/50 text-white text-sm font-bold px-6 py-3 rounded-xl transition-all shadow-sm cursor-pointer whitespace-nowrap"
        >
          {isGeneratingAll ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Download className="w-4 h-4" />
          )}
          Generate All PDFs
        </button>
      </div>

      {/* Enhanced Alerts Section */}
      {alerts.length > 0 && (
        <div className="bg-slate-50 rounded-3xl border border-slate-100 overflow-hidden transition-all">
          <div 
            className="px-6 py-4 flex items-center justify-between cursor-pointer hover:bg-slate-100/50 transition-colors"
            onClick={() => setIsAlertsOpen(!isAlertsOpen)}
          >
            <h2 className="text-sm font-bold text-slate-800 flex items-center gap-2 uppercase tracking-wider">
              Clinical Alerts
              <span className="bg-red-100 text-red-700 py-0.5 px-2 rounded-full text-xs">{alerts.length}</span>
            </h2>
            <button className="text-slate-400 hover:text-slate-600 transition-colors">
              {isAlertsOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </button>
          </div>
          
          {isAlertsOpen && (
            <div className="px-6 pb-6 pt-2 border-t border-slate-100/50">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {alerts.map(alert => {
                  const Icon = alert.icon;
                  const colorClasses = {
                    red: "bg-red-50 border-red-200 text-red-800",
                    amber: "bg-amber-50 border-amber-200 text-amber-800",
                    blue: "bg-blue-50 border-blue-200 text-blue-800",
                  }[alert.color];

                  return (
                    <div key={alert.id} className={`border rounded-2xl p-4 flex flex-col justify-between transition-all hover:shadow-md ${colorClasses}`}>
                      <div>
                        <div className="flex items-start justify-between mb-3">
                          <div className="p-2 rounded-xl bg-white/60 backdrop-blur-sm border border-white/40 shadow-sm">
                            <Icon className={`w-5 h-5 ${alert.color === 'red' ? 'text-red-600' : alert.color === 'amber' ? 'text-amber-600' : 'text-blue-600'}`} />
                          </div>
                          <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-full bg-white/60 backdrop-blur-sm border border-white/40 shadow-sm ${alert.color === 'red' ? 'text-red-700' : alert.color === 'amber' ? 'text-amber-700' : 'text-blue-700'}`}>
                            {alert.type}
                          </span>
                        </div>
                        <h3 className="font-bold text-sm mb-1">{alert.title}</h3>
                        <p className="text-xs opacity-80 leading-relaxed font-medium mb-4">
                          {alert.description}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 mt-auto pt-4 border-t border-black/5">
                        <button className={`flex-1 text-xs font-bold py-2 px-3 rounded-lg transition-colors ${alert.color === 'red' ? 'bg-red-100 hover:bg-red-200 text-red-700' : alert.color === 'amber' ? 'bg-amber-100 hover:bg-amber-200 text-amber-700' : 'bg-blue-100 hover:bg-blue-200 text-blue-700'}`}>
                          {alert.actionText}
                        </button>
                        <button 
                          onClick={() => dismissAlert(alert.id)}
                          className="text-xs font-bold py-2 px-3 rounded-lg hover:bg-black/5 transition-colors opacity-70 hover:opacity-100">
                          Dismiss
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="pt-4 space-y-8">
        {/* Patient Header Section */}
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-[#e6f4f1] text-[#007e7a] flex items-center justify-center">
            <ClipboardList className="w-7 h-7" />
          </div>
          <div>
            <div className="text-xs font-medium text-slate-400 uppercase tracking-wide">Patient</div>
            <div className="text-2xl font-extrabold text-slate-900 font-display">Selena Gomez</div>
          </div>
        </div>

        {/* 4 Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="border border-slate-200 rounded-3xl p-4 flex items-center gap-4 hover:shadow-sm transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-[#e6f4f1] text-[#007e7a] flex items-center justify-center shrink-0">
              <Calendar className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Visit Date</div>
              <div className="text-sm font-bold text-slate-800">Oct 24, 2023</div>
            </div>
          </div>
          
          <div className="border border-slate-200 rounded-3xl p-4 flex items-center gap-4 hover:shadow-sm transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-[#e6f4f1] text-[#007e7a] flex items-center justify-center shrink-0">
              <Fingerprint className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">ID</div>
              <div className="text-sm font-bold text-slate-800">#SG-9921</div>
            </div>
          </div>

          <div className="border border-slate-200 rounded-3xl p-4 flex items-center gap-4 hover:shadow-sm transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-[#e6f4f1] text-[#007e7a] flex items-center justify-center shrink-0">
              <FilePlus className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Type</div>
              <div className="text-sm font-bold text-slate-800">Follow-up</div>
            </div>
          </div>

          <div className="border border-slate-200 rounded-3xl p-4 flex items-center gap-4 hover:shadow-sm transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-[#e6f4f1] text-[#007e7a] flex items-center justify-center shrink-0">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Status</div>
              <div className="mt-0.5">
                <span className="bg-[#e6f4f1] text-[#007e7a] text-[10px] font-bold px-2 py-0.5 rounded-full">Drafting</span>
              </div>
            </div>
          </div>
        </div>

        {/* Editor Container */}
        <div className="border border-slate-200 rounded-[2rem] overflow-hidden bg-white shadow-sm">
          {/* Tabs Header */}
          <div className="flex items-center justify-between px-2 pt-2 border-b border-slate-100 bg-white">
            <div className="flex overflow-x-auto hide-scrollbar">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-6 py-4 text-sm font-bold transition-colors relative whitespace-nowrap ${
                    activeTab === tab.id 
                      ? 'text-[#007e7a]' 
                      : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  {tab.label}
                  {activeTab === tab.id && (
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#007e7a] rounded-t-full" />
                  )}
                </button>
              ))}
            </div>
            <div className="px-6 hidden sm:block">
              <div className="flex items-center gap-1.5 bg-[#e6f4f1] text-[#007e7a] px-3 py-1.5 rounded-full text-[10px] font-bold tracking-wide uppercase">
                <Sparkles className="w-3 h-3" />
                AI Generated
              </div>
            </div>
          </div>

          {/* Toolbar */}
          <div className="flex items-center justify-between px-6 py-3 border-b border-slate-100 bg-white">
            <div className="flex items-center gap-4 text-slate-500">
              <button className="p-1.5 hover:bg-slate-100 rounded-md transition-colors"><Bold className="w-4 h-4" /></button>
              <button className="p-1.5 hover:bg-slate-100 rounded-md transition-colors"><Italic className="w-4 h-4" /></button>
              <button className="p-1.5 hover:bg-slate-100 rounded-md transition-colors"><List className="w-4 h-4" /></button>
              <button className="p-1.5 hover:bg-slate-100 rounded-md transition-colors"><ListOrdered className="w-4 h-4" /></button>
              <div className="w-px h-4 bg-slate-200 mx-1" />
              <button className="p-1.5 hover:bg-slate-100 rounded-md transition-colors"><Link2 className="w-4 h-4" /></button>
              <button 
                className="p-1.5 hover:bg-slate-100 rounded-md transition-colors relative group"
                onClick={handleImageClick}
              >
                <ImageIcon className="w-4 h-4" />
                <span className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                  Add Image
                </span>
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  className="hidden" 
                  accept="image/*"
                  onChange={() => alert("Image upload mock clicked")}
                />
              </button>
            </div>
            <div className="text-[11px] font-medium text-slate-400">
              Last saved 2m ago
            </div>
          </div>

          {/* Editor Area */}
          <div className="p-6">
            <textarea
              value={documents[activeTab]}
              onChange={handleTextChange}
              className="w-full h-[400px] bg-transparent text-slate-800 text-sm focus:outline-none resize-none font-medium leading-relaxed"
              placeholder={`Start typing your ${tabs.find(t => t.id === activeTab)?.label.toLowerCase()} here...`}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
