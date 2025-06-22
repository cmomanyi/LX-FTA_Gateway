// ThreatDashboard.jsx
import React, { useState } from "react";
import Layout from "../components/Layout";
import Sidebar from "../components/Sidebar";
import Logs from "./Logs";
import Analytics from "./Analytics";
import DashboardMain from "./DashboardMain"; // You can modularize dashboard if needed

const ThreatDashboard = () => {
    const [activeTab, setActiveTab] = useState("dashboard");

    return (
        <Layout>
            <div className="flex">
                <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
                <div className="flex-1 p-6 bg-white min-h-screen">
                    {activeTab === "dashboard" && <DashboardMain />}
                    {activeTab === "logs" && <Logs />}
                    {activeTab === "analytics" && <Analytics />}
                </div>
            </div>
        </Layout>
    );
};

export default ThreatDashboard;
