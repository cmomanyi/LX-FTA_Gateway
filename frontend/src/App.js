import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import GenericDashboard from "./pages/GenericDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import FirmwareDashboard from "./pages/FirmwareDashboard";
import Unauthorized from "./pages/Unauthorized";
import ThreatDashboard from "./components/ThreatDashboard";


function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Navigate to="/login" />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/genericdashboard" element={<GenericDashboard />} />
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/unauthorized" element={<Unauthorized />} />
                <Route path="/firmwaredashboard" element={<FirmwareDashboard />} />
                <Route path="/attackV2" element={<ThreatDashboard />} />
                <Route path="*" element={<Navigate to="/unauthorized" />} />
            </Routes>
        </Router>
    );
}

export default App;
