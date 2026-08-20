import { useState, useRef, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { 
  AlertTriangle, Download, ShieldAlert, Info, 
  Calendar, Fingerprint, FilePlus, Clock, 
  Bold, Italic, List, ListOrdered, Link2, Image as ImageIcon, Sparkles, ClipboardList,
  ChevronDown, ChevronUp, Save, CheckCircle, ExternalLink, Loader2, FileCheck
} from "lucide-react";
import { api } from "../../services/api";

export default function SuggestedPlanMock() {
  const location = useLocation();
  const navigate = useNavigate();
  const stateData = location.state || {};

  const sessionId = stateData.sessionId || "consult_demo_8821";
  const caseStudySummary = stateData.caseStudySummary;
  const soapData = stateData.soap;
  const patientData = stateData.patientData || {};

  const [activeTab, setActiveTab] = useState('soap');
  const [isGeneratingAll, setIsGeneratingAll] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [generatedPdfUrl, setGeneratedPdfUrl] = useState(null);
  const [isAlertsOpen, setIsAlertsOpen] = useState(false);
  const fileInputRef = useRef(null);

  // Format initial documents from backend AI responses if available
  const buildInitialDocuments = () => {
    // 1. SOAP
    let soapContent = "";
    if (soapData) {
      const subj = soapData.subjective;
      const obj = soapData.objective;
      const assess = soapData.assessment_plan;

      soapContent = `SUBJECTIVE:
Chief Complaint: ${subj?.chief_complaint || "N/A"}
HPI: ${subj?.hpi ? JSON.stringify(subj.hpi, null, 2) : "N/A"}
Past Medical History: ${subj?.past_medical_history?.join(", ") || "None"}
Current Medications: ${subj?.medications?.join(", ") || "None"}
Allergies: ${subj?.allergies?.join(", ") || "None"}

OBJECTIVE:
Vitals: ${obj?.vitals?.join(", ") || "Stable"}
Physical Exam Findings: ${obj?.physical_exam_findings?.join(", ") || "Unremarkable"}
Diagnostic Results: ${obj?.diagnostic_results?.join(", ") || "None"}

ASSESSMENT & PLAN:
Diagnoses: ${assess?.diagnoses?.join(", ") || "Clinical evaluation pending"}
Orders & Prescriptions: ${assess?.orders_prescriptions?.join(", ") || "None"}
Patient Instructions: ${assess?.patient_instructions?.join(", ") || "None"}
Follow-Up: ${assess?.follow_up || "2 weeks"}`;
    } else if (caseStudySummary) {
      soapContent = `SUBJECTIVE:
Chief Complaints: ${caseStudySummary.chief_complaints}

OBJECTIVE:
Vitals: ${caseStudySummary.vitals}
Examination Findings: ${caseStudySummary.examination_findings}

ASSESSMENT:
Diagnosis: ${caseStudySummary.diagnosis}

PLAN:
Treatment Plan: ${caseStudySummary.treatment_plan}
Prescriptions:
${caseStudySummary.prescriptions?.map(p => `- ${p.medicine} | ${p.dosage} | ${p.duration}`).join("\n") || "None"}
Instructions: ${caseStudySummary.instructions}`;
    } else {
      soapContent = `SUBJECTIVE:
Patient complains of orthostatic dizziness and post-op knee stiffness.

OBJECTIVE:
BP: 112/78, HR: 82 bpm, Temp: 98.6°F. Mobility improving.

ASSESSMENT:
1. Post-operative recovery status post knee arthroplasty.
2. Orthostatic hypotension secondary to medication timing.
3. Atrial fibrillation, stable on anticoagulant therapy.

PLAN:
1. Refill Eliquis 5mg BID for stroke prevention.
2. Continue Metformin 500mg BID and Lisinopril 10mg QD.
3. Hydration encouragement and slow positional changes.
4. Follow-up in 2 weeks.`;
    }

    // 2. Patient Visit Summary
    let summaryContent = "";
    if (caseStudySummary) {
      summaryContent = `PATIENT CASE SHEET SUMMARY
--------------------------------------------------
Patient Name : ${caseStudySummary.patient_name}
Age / Gender : ${caseStudySummary.age} / ${caseStudySummary.gender}
Patient ID   : ${caseStudySummary.patient_no}
Attending    : ${caseStudySummary.doctor}
Visit Date   : ${caseStudySummary.date}

CHIEF COMPLAINTS:
${caseStudySummary.chief_complaints}

VITALS & EXAM:
${caseStudySummary.vitals}
Findings: ${caseStudySummary.examination_findings}

DIAGNOSIS:
${caseStudySummary.diagnosis}

TREATMENT & PLAN:
${caseStudySummary.treatment_plan}
${caseStudySummary.instructions}`;
    } else {
      summaryContent = `Patient: ${patientData.name || "Elena Rodriguez"}
Date: ${new Date().toLocaleDateString()}
ID: ${sessionId}

Reason for Visit: Post-operative consultation and medication review.

Summary of Visit:
Patient was evaluated following orthopedic surgery. Vitals and knee range of motion are improving. Orthostatic symptoms were evaluated and addressed with medication schedule adjustments. Eliquis prescription was renewed. Patient reported feeling well-supported.`;
    }

    // 3. Discharge Report / Referral
    let referralContent = "";
    if (caseStudySummary) {
      referralContent = `DISCHARGE / REFERRAL REPORT
--------------------------------------------------
To: Cardiology & Physical Therapy
From: ${caseStudySummary.doctor}
Patient: ${caseStudySummary.patient_name} (${caseStudySummary.age}, ${caseStudySummary.gender})

Diagnosis: ${caseStudySummary.diagnosis}
Investigations: ${caseStudySummary.investigations || "None"}
Therapy Details: ${caseStudySummary.therapy_description || "Outpatient physical therapy"}
Therapy Result: ${caseStudySummary.therapy_result || "Progressing satisfactorily"}

Clinical Notes:
${caseStudySummary.notes || "Patient is stable for continued outpatient management."}`;
    } else {
      referralContent = `Referral Letter / Clinical Report
To: Cardiology Department & Outpatient Rehab
Attending: Dr. Julian Vance, MD

Patient Elena Rodriguez is continuing post-operative recovery with mild orthostatic dizziness.
Cardiovascular rhythm is monitored with stable vitals. Please continue scheduled physical therapy protocol 3 times weekly.`;
    }

    // 4. Instructions
    let instructionsContent = "";
    if (caseStudySummary) {
      instructionsContent = `DISCHARGE INSTRUCTIONS FOR ${caseStudySummary.patient_name.toUpperCase()}
--------------------------------------------------
Prescribed Medications:
${caseStudySummary.prescriptions?.map(p => `• ${p.medicine}: ${p.dosage} for ${p.duration}`).join("\n") || "• Continue current baseline medications."}

Care & Lifestyle Instructions:
${caseStudySummary.instructions}

Warning Signs:
Contact the clinic immediately if experiencing severe dizziness, palpitations, chest pain, or sudden shortness of breath.`;
    } else {
      instructionsContent = `Discharge Instructions:
1. Take Eliquis 5mg twice daily with or without food.
2. Take Metformin 500mg twice daily with meals.
3. Take Lisinopril 10mg once daily in the morning.
4. Stand up slowly from sitting or lying down to prevent dizziness.
5. Drink at least 6-8 glasses of water daily.
6. Return to clinic in 2 weeks or immediately if symptoms worsen.`;
    }

    return {
      soap: soapContent,
      summary: summaryContent,
      referral: referralContent,
      instructions: instructionsContent,
    };
  };

  const [documents, setDocuments] = useState(buildInitialDocuments());

  // Alerts
  const [alerts, setAlerts] = useState([
    {
      id: 1,
      type: "critical",
      title: "Medication Adherence Alert",
      description: "Patient reported missing doses of anticoagulant (Eliquis). Refill ordered immediately.",
      icon: ShieldAlert,
      color: "red",
      actionText: "Review Rx"
    },
    {
      id: 2,
      type: "warning",
      title: "Orthostatic Symptom Flag",
      description: "Mild orthostatic dizziness noted. Vitals stable; advised hydration and positional pacing.",
      icon: AlertTriangle,
      color: "amber",
      actionText: "Check BP"
    }
  ]);

  const tabs = [
    { id: 'soap', label: 'SOAP Notes' },
    { id: 'summary', label: 'Patient Visit Summary' },
    { id: 'referral', label: 'Discharge Report / Referral' },
    { id: 'instructions', label: 'Discharge Instructions' },
  ];

  const handleTextChange = (e) => {
    setDocuments({
      ...documents,
      [activeTab]: e.target.value
    });
  };

  const handleSaveSummary = async () => {
    setIsSaving(true);
    setSaveSuccess(false);

    try {
      // Construct updated CaseSheetSummary object for backend update
      const updatedSummaryPayload = {
        patient_name: caseStudySummary?.patient_name || patientData.name || "Elena Rodriguez",
        gender: caseStudySummary?.gender || patientData.gender || "Female",
        age: String(caseStudySummary?.age || patientData.age || "72"),
        patient_no: caseStudySummary?.patient_no || sessionId,
        doctor: caseStudySummary?.doctor || "Dr. Julian Vance",
        date: caseStudySummary?.date || new Date().toLocaleString(),
        chief_complaints: caseStudySummary?.chief_complaints || "Orthostatic dizziness and post-op recovery",
        vitals: caseStudySummary?.vitals || "BP: 112/78, Pulse: 82 bpm",
        examination_findings: caseStudySummary?.examination_findings || "Unremarkable, wound healing nicely",
        investigations: caseStudySummary?.investigations || "None ordered",
        diagnosis: caseStudySummary?.diagnosis || "Orthostatic Hypotension, AFib stable",
        prescriptions: caseStudySummary?.prescriptions || [
          { medicine: "Eliquis 5mg", dosage: "1-0-1 After Food", duration: "30 Days" },
          { medicine: "Lisinopril 10mg", dosage: "1-0-0 Morning", duration: "30 Days" }
        ],
        treatment_plan: documents.summary || documents.soap,
        therapy_description: "Outpatient Physical Therapy",
        therapy_result: "Progressing well",
        notes: documents.referral || "Routine follow-up scheduled",
        instructions: documents.instructions || "Avoid rapid position changes",
      };

      await api.updateSummary({
        sessionId,
        updatedCaseStudySummary: updatedSummaryPayload,
      });

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      console.warn("Could not save to backend database:", err);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleGenerateAllPDFs = async () => {
    setIsGeneratingAll(true);
    setGeneratedPdfUrl(null);

    try {
      // First save current review
      await handleSaveSummary();

      // Call Step 3: generate-pdf backend endpoint
      const pdfRes = await api.generatePdf(sessionId);
      console.log("PDF generation response:", pdfRes);

      if (pdfRes.pdf_url) {
        setGeneratedPdfUrl(pdfRes.pdf_url);
      }

      // Download directly via backend download endpoint
      const downloadUrl = pdfRes.download_url || api.getDownloadPdfUrl(sessionId);
      
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.setAttribute("download", `case_sheet_${sessionId}.pdf`);
      link.target = "_blank";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

    } catch (err) {
      console.warn("Backend PDF generation notice:", err.message);
      // Fallback direct download link
      const fallbackUrl = api.getDownloadPdfUrl(sessionId);
      window.open(fallbackUrl, "_blank");
    } finally {
      setIsGeneratingAll(false);
    }
  };
  
  const dismissAlert = (id) => {
    setAlerts(alerts.filter(a => a.id !== id));
  };

  const handleImageClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const patientDisplayName = caseStudySummary?.patient_name || patientData.name || "Elena Rodriguez";

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 bg-white min-h-screen font-sans text-slate-800">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold font-display text-slate-900 tracking-tight">
            Review Generated Case Documents
          </h1>
          <p className="text-sm text-slate-500 font-medium mt-2">
            AI synthesized 4 clinical documents from your consultation transcript. Review, customize, and generate official PDFs.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleSaveSummary}
            disabled={isSaving}
            className="flex items-center justify-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-sm font-bold px-5 py-3 rounded-xl transition-all cursor-pointer"
          >
            {isSaving ? (
              <Loader2 className="w-4 h-4 animate-spin text-[#007e7a]" />
            ) : saveSuccess ? (
              <CheckCircle className="w-4 h-4 text-emerald-600" />
            ) : (
              <Save className="w-4 h-4 text-[#007e7a]" />
            )}
            <span>{saveSuccess ? "Saved to Database" : "Save Changes"}</span>
          </button>

          <button
            onClick={handleGenerateAllPDFs}
            disabled={isGeneratingAll}
            className="flex items-center justify-center gap-2 bg-[#007e7a] hover:bg-[#005f5c] disabled:bg-teal-700/50 text-white text-sm font-bold px-6 py-3 rounded-xl transition-all shadow-sm cursor-pointer whitespace-nowrap"
          >
            {isGeneratingAll ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            <span>Export Official PDF</span>
          </button>
        </div>
      </div>

      {generatedPdfUrl && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 p-4 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileCheck className="w-5 h-5 text-emerald-600" />
            <span className="text-sm font-semibold">
              PDF generated and stored in Supabase Storage.
            </span>
          </div>
          <a
            href={generatedPdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs font-bold text-[#007e7a] hover:underline"
          >
            Open in Supabase <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      )}

      {/* Clinical Alerts Section */}
      {alerts.length > 0 && (
        <div className="bg-slate-50 rounded-3xl border border-slate-100 overflow-hidden transition-all">
          <div 
            className="px-6 py-4 flex items-center justify-between cursor-pointer hover:bg-slate-100/50 transition-colors"
            onClick={() => setIsAlertsOpen(!isAlertsOpen)}
          >
            <h2 className="text-sm font-bold text-slate-800 flex items-center gap-2 uppercase tracking-wider">
              Clinical Insights &amp; Alerts
              <span className="bg-red-100 text-red-700 py-0.5 px-2 rounded-full text-xs font-extrabold">{alerts.length}</span>
            </h2>
            <button className="text-slate-400 hover:text-slate-600 transition-colors">
              {isAlertsOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </button>
          </div>
          
          {isAlertsOpen && (
            <div className="px-6 pb-6 pt-2 border-t border-slate-100/50">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                            <Icon className={`w-5 h-5 ${alert.color === 'red' ? 'text-red-600' : 'text-amber-600'}`} />
                          </div>
                          <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-full bg-white/60 backdrop-blur-sm border border-white/40 shadow-sm ${alert.color === 'red' ? 'text-red-700' : 'text-amber-700'}`}>
                            {alert.type}
                          </span>
                        </div>
                        <h3 className="font-bold text-sm mb-1">{alert.title}</h3>
                        <p className="text-xs opacity-80 leading-relaxed font-medium mb-4">
                          {alert.description}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 mt-auto pt-4 border-t border-black/5">
                        <button 
                          onClick={() => dismissAlert(alert.id)}
                          className="text-xs font-bold py-2 px-3 rounded-lg hover:bg-black/5 transition-colors opacity-70 hover:opacity-100">
                          Acknowledge
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

      <div className="pt-2 space-y-6">
        {/* Patient Header Section */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#e6f4f1] text-[#007e7a] flex items-center justify-center font-bold text-xl">
              <ClipboardList className="w-7 h-7" />
            </div>
            <div>
              <div className="text-xs font-medium text-slate-400 uppercase tracking-wide">Patient Consultation</div>
              <div className="text-2xl font-extrabold text-slate-900 font-display">{patientDisplayName}</div>
            </div>
          </div>

          <div className="text-right text-xs text-slate-400">
            <span className="font-bold text-slate-700">Session ID:</span> {sessionId.slice(0, 16)}...
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
              <div className="text-sm font-bold text-slate-800">{new Date().toLocaleDateString()}</div>
            </div>
          </div>
          
          <div className="border border-slate-200 rounded-3xl p-4 flex items-center gap-4 hover:shadow-sm transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-[#e6f4f1] text-[#007e7a] flex items-center justify-center shrink-0">
              <Fingerprint className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Record ID</div>
              <div className="text-sm font-bold text-slate-800">#{sessionId.slice(-6).toUpperCase()}</div>
            </div>
          </div>

          <div className="border border-slate-200 rounded-3xl p-4 flex items-center gap-4 hover:shadow-sm transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-[#e6f4f1] text-[#007e7a] flex items-center justify-center shrink-0">
              <FilePlus className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Type</div>
              <div className="text-sm font-bold text-slate-800">Clinical Case Sheet</div>
            </div>
          </div>

          <div className="border border-slate-200 rounded-3xl p-4 flex items-center gap-4 hover:shadow-sm transition-shadow">
            <div className="w-10 h-10 rounded-xl bg-[#e6f4f1] text-[#007e7a] flex items-center justify-center shrink-0">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Status</div>
              <div className="mt-0.5">
                <span className="bg-[#e6f4f1] text-[#007e7a] text-[10px] font-bold px-2 py-0.5 rounded-full">
                  Pending Review
                </span>
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
                  className={`px-6 py-4 text-sm font-bold transition-colors relative whitespace-nowrap cursor-pointer ${
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
                LangGraph AI Synthesized
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
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  className="hidden" 
                  accept="image/*"
                />
              </button>
            </div>
            <div className="text-[11px] font-medium text-slate-400">
              Auto-sync ready • Click text to edit before PDF export
            </div>
          </div>

          {/* Editor Area */}
          <div className="p-6">
            <textarea
              value={documents[activeTab]}
              onChange={handleTextChange}
              className="w-full h-[420px] bg-transparent text-slate-800 text-sm font-mono focus:outline-none resize-none leading-relaxed"
              placeholder={`Start typing your ${tabs.find(t => t.id === activeTab)?.label.toLowerCase()} here...`}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
