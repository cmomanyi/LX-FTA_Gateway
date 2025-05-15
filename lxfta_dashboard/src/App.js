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
import ShapAttackDashboard from "./pages/ShapAttackDashboard"; // create this component for post-login redirect

function App() {
  return (
      <Router>
          <Routes>
              <Route path="/" element={<LoginPage/>}/>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/genericdashboard" element={<GenericDashboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/websocketdashboard" element={<SensorDashboardWebSocket />} />
              <Route path="/viewanomalies" element={<SensorAnomalyDashboard />} />
              <Route path="/securitydashboard" element={<SensorSecurityDashboard/>} />
              <Route path="/firmwaredashboard" element={<FirmwareDashboard />} />
              <Route path="/attacksimulationdashboard" element={<AttackSimulationDashboard />} />
              <Route path="/Shapdashboard" element={<ShapAttackDashboard />} />
          </Routes>
      </Router>

  );
}

export default App;
