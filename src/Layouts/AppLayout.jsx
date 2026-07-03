import { useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

export default function AppLayout({ doctorInfo }) {
  const navigate = useNavigate();
  const [alertsCount] = useState(3);

  const handleMetricClick = (metricId) => {
    switch (metricId) {
      case "patients":
        navigate("/patients");
        break;
      case "alerts":
        navigate("/Dashboard");
        break;
      case "soap":
        navigate("/soapnotes");
        break;
      default:
        console.log("Metric clicked:", metricId);
    }
  };

  const handlePatientClick = (patient) => {
    if (!patient) {
      navigate("/patients");
      return;
    }
    navigate(`/patients/${patient.id ?? patient.name}`);
  };

  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar doctorInfo={doctorInfo} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Topbar doctorInfo={doctorInfo} alertsCount={alertsCount} />
        <main className="flex-1 overflow-y-auto">
          <Outlet
            context={{
              doctorInfo,
              alertsCount,
              onMetricClick: handleMetricClick,
              onPatientClick: handlePatientClick,
            }}
          />
        </main>
      </div>
    </div>
  );
}