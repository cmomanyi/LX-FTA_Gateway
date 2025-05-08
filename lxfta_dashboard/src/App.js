import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import GenericDashboard from "./pages/GenericDashboard";
import AdminDashboard from "./pages/AdminDashboard"; // create this component for post-login redirect

function App() {
  return (
      <Router>
          <Routes>
              <Route path="/" element={<LoginPage/>}/>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/genericdashboard" element={<GenericDashboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
          </Routes>
      </Router>

  );
}

export default App;
