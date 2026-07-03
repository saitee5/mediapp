import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/pages/Login";
import Dashboard from "./components/pages/Dashboard";
import SoapNoteEditor from "./components/pages/SoapNoteEditor";
import LiveConsultation from "./components/pages/LiveConsultation";
import PatientSummary from "./components/pages/PatientSummary";
import AppLayout from "./Layouts/AppLayout";
import Directives from "./components/pages/Directives";
import History from "./components/pages/History";

function App() {
  const [doctorInfo, setDoctorInfo] = useState(null);

  const handleLogin = (info) => {
    setDoctorInfo(info);
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<Navigate to={doctorInfo ? "/Dashboard" : "/login"} />}
        />

        <Route
          path="/login"
          element={
            doctorInfo ? (
              <Navigate to="/Dashboard" />
            ) : (
              <Login onLogin={handleLogin} />
            )
          }
        />

        <Route
          element={
            doctorInfo ? <AppLayout doctorInfo={doctorInfo} /> : <Navigate to="/login" />
          }
        >
          <Route path="/Dashboard" element={<Dashboard />} />
          <Route path="/soapnotes/:id" element={<SoapNoteEditor />} />
          <Route path="/live-scribe" element={<LiveConsultation />} />
          <Route path="/patients/:id" element={<PatientSummary />} />
          <Route path="/directives" element={<Directives />} />
          <Route path="/History" element={<History />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;