import React, { useState } from "react";

const Sidebar = ({ activeTab, setActiveTab }) => {
    const [collapsed, setCollapsed] = useState(false);

    const navItems = [
        { id: "dashboard", label: "📊 Dashboard" },
        { id: "logs", label: "🧾 Logs" },
        { id: "shap", label: "🧠 SHAP Insights" },
        { id: "analytics", label: "📈 Analytics" },
    ];

    return (
        <div className={`h-screen bg-gray-800 text-white transition-all duration-300 ${collapsed ? "w-16" : "w-64"}`}>
            <div className="flex justify-between items-center p-4">
                <h1 className={`font-bold text-lg ${collapsed ? "hidden" : "block"}`}>SensorSec</h1>
                <button onClick={() => setCollapsed(!collapsed)} className="text-sm">
                    {collapsed ? "➡️" : "⬅️"}
                </button>
            </div>
            <ul>
                {navItems.map((item) => (
                    <li
                        key={item.id}
                        className={`p-4 cursor-pointer hover:bg-gray-700 ${
                            activeTab === item.id ? "bg-gray-700" : ""
                        }`}
                        onClick={() => setActiveTab(item.id)}
                    >
                        <span className={`${collapsed ? "tooltip tooltip-right" : ""}`}>
                            {item.label}
                        </span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Sidebar;
