import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { User, Activity, FileText, ArrowRight } from "lucide-react";

export default function NewConsultation() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    gender: "Male",
    bloodPressure: "",
    heartRate: "",
    temperature: "",
    reasonForVisit: "",
    medicalHistory: "",
    allergies: "",
    activeMedications: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Navigate to live-scribe and pass the patient data via state
    navigate("/live-scribe", { state: { patientData: formData } });
  };

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-8">
        <div className="mb-8 text-center lg:text-left">
          <h1 className="text-3xl font-extrabold font-display text-slate-900 tracking-tight">
            New Consultation
          </h1>
          <p className="text-sm text-slate-500 font-medium mt-2">
            Enter basic patient information and vitals before starting the live scribe session.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Patient Details Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
              <User className="w-5 h-5 text-[#007e7a]" />
              <h2 className="text-lg font-bold text-slate-800 font-display">Patient Details</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Full Name</label>
                <input
                  type="text"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium"
                  placeholder="E.g. John Doe"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Age</label>
                  <input
                    type="number"
                    name="age"
                    required
                    value={formData.age}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium"
                    placeholder="Years"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Gender</label>
                  <select
                    name="gender"
                    value={formData.gender}
                    onChange={handleChange}
                    className="w-full bg-slate-50 border border-slate-200 text-slate-800 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Vitals Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
              <Activity className="w-5 h-5 text-[#007e7a]" />
              <h2 className="text-lg font-bold text-slate-800 font-display">Vitals</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Blood Pressure</label>
                <input
                  type="text"
                  name="bloodPressure"
                  value={formData.bloodPressure}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium"
                  placeholder="120/80"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Heart Rate</label>
                <input
                  type="text"
                  name="heartRate"
                  value={formData.heartRate}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium"
                  placeholder="bpm"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Temperature</label>
                <input
                  type="text"
                  name="temperature"
                  value={formData.temperature}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium"
                  placeholder="°F / °C"
                />
              </div>
            </div>
          </div>

          {/* Reason for Visit */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
              <FileText className="w-5 h-5 text-[#007e7a]" />
              <h2 className="text-lg font-bold text-slate-800 font-display">Encounter Details</h2>
            </div>
            
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Chief Complaint / Reason for visit</label>
              <textarea
                name="reasonForVisit"
                required
                value={formData.reasonForVisit}
                onChange={handleChange}
                rows={2}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium resize-none"
                placeholder="Briefly describe the reason for the visit..."
              />
            </div>
          </div>

          {/* Medical Information Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
              <FileText className="w-5 h-5 text-[#007e7a]" />
              <h2 className="text-lg font-bold text-slate-800 font-display">Medical Information</h2>
            </div>
            
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Medical History (comma separated)</label>
              <textarea
                name="medicalHistory"
                value={formData.medicalHistory}
                onChange={handleChange}
                rows={2}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium resize-none"
                placeholder="E.g. Hypertension, Type 2 Diabetes"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Allergies (comma separated)</label>
              <textarea
                name="allergies"
                value={formData.allergies}
                onChange={handleChange}
                rows={2}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium resize-none"
                placeholder="E.g. Penicillin, Latex"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wide">Active Medications (comma separated)</label>
              <textarea
                name="activeMedications"
                value={formData.activeMedications}
                onChange={handleChange}
                rows={2}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 px-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium resize-none"
                placeholder="E.g. Lisinopril 10mg QD, Metformin 500mg BID"
              />
            </div>
          </div>

          <div className="pt-4">
            <button
              type="submit"
              className="w-full md:w-auto md:float-right flex items-center justify-center gap-2 bg-[#007e7a] hover:bg-[#005f5c] text-white text-sm font-bold px-6 py-3 rounded-xl transition-colors shadow-sm cursor-pointer"
            >
              Start Consultation
              <ArrowRight className="w-4 h-4" />
            </button>
            <div className="clear-both"></div>
          </div>
        </form>
      </div>
    </div>
  );
}
