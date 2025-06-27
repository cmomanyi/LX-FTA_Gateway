// ThreatDashboard.jsx
import React, { useState } from "react";
import Layout from "./Layout";
import Sidebar from "./Sidebar";
import Logs from "../pages/Logs";
import Analytics from "../pages/Analytics";
import SHAPDashboard  from "../pages/SHAPDashboard"
import DashboardMain from "../pages/DashboardMain"; // You can modularize dashboard if needed

const ThreatDashboard = () => {
    const [activeTab, setActiveTab] = useState("dashboard");

    return (
        <Layout>
            <div className="flex">
                <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
                <div className="flex-1 p-6 bg-white min-h-screen">
                    {activeTab === "dashboard" && <DashboardMain />}
                    {activeTab === "logs" && <Logs />}
                    {activeTab === "shap" && <SHAPDashboard />}
                    {activeTab === "analytics" && <Analytics />}
                </div>
            </div>
        </Layout>
    );
};

export default ThreatDashboard;
