import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import GenericDashboard from "./pages/GenericDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import SensorDashboardWebSocket from "./pages/SensorDashboardWebSocket";
import SensorAnomalyDashboard from "./pages/SensorAnomalyDashboard";
import SensorSecurityDashboard from "./pages/SensorSecurityDashboard";
import FirmwareDashboard from "./pages/FirmwareDashboard";
import AttackSimulationDashboard from "./pages/AttackSimulationDashboard";
import ShapAttackDashboard from "./pages/ShapAttackDashboard";
import Unauthorized from "./pages/Unauthorized";
import ThreatDashboard from "./pages/ThreatDashboard";
import AttackAuditDashboard from "./pages/AttackAuditDashboard"; // create this component for post-login redirect

function App() {
  return (
      <Router>
          <Routes>
              <Route path="/login" element={<LoginPage/>}/>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/genericdashboard" element={<GenericDashboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/unauthorized" element={<Unauthorized />} />
              <Route path="/websocketdashboard" element={<SensorDashboardWebSocket />} />
              <Route path="/viewanomalies" element={<SensorAnomalyDashboard />} />
              <Route path="/securitydashboard" element={<SensorSecurityDashboard/>} />
              <Route path="/firmwaredashboard" element={<FirmwareDashboard />} />
              <Route path="/attacksimulationdashboard" element={<AttackSimulationDashboard />} />
              <Route path="/Shapdashboard" element={<ShapAttackDashboard />} />
              <Route path="/attackV2" element={<ThreatDashboard />} />
              <Route path ="/attacksimulate" element={<AttackAuditDashboard/>}/>
          </Routes>
      </Router>

  );
}

export default App;
