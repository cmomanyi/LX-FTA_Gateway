import React, { useState, useEffect } from "react";
import axios from "axios";
import Layout from "../components/Layout";

const AttackSimulationDashboard = () => {
    const [attackType, setAttackType] = useState("spoofing");
    const [attackResult, setAttackResult] = useState(null);
    const [attackLog, setAttackLog] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchLog = async () => {
        try {
            const response = await axios.get("http://localhost:8000/attack-log");
            setAttackLog(response.data);
        } catch (error) {
            console.error("Failed to fetch log", error);
        }
    };

    const simulateAttack = async () => {
        setLoading(true);
        try {
            const form = new FormData();
            form.append("attack_type", attackType);
            const response = await axios.post("http://localhost:8000/simulate-attack", form);
            setAttackResult(response.data);
            fetchLog();
        } catch (error) {
            setAttackResult({ status: "Error", message: "Simulation failed." });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLog();
    }, []);

    return (
        <Layout>
            <div className="p-6 max-w-5xl mx-auto">
                <h1 className="text-2xl font-bold mb-4">🛡️ Attack Simulation Dashboard</h1>

                <div className="flex items-center gap-4 mb-4">
                    <select
                        value={attackType}
                        onChange={(e) => setAttackType(e.target.value)}
                        className="border px-4 py-2 rounded shadow"
                    >
                        <option value="spoofing">Spoofing</option>
                        <option value="replay">Replay Attack</option>
                        <option value="ml_evasion">ML Evasion</option>
                        <option value="firmware_injection">Firmware Injection</option>
                        <option value="sensor_hijack">Sensor Hijack</option>
                        <option value="api_abuse">API Abuse</option>
                        <option value="tamper_breach">Tamper Breach</option>
                        <option value="side_channel">Side-Channel Attack</option>
                        <option value="ddos_flood">DDoS Flood</option>
                    </select>

                    <button
                        onClick={simulateAttack}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                        disabled={loading}
                    >
                        {loading ? "Simulating..." : "Simulate"}
                    </button>
                </div>

                {attackResult && (
                    <div className="border p-4 rounded mb-6 bg-gray-100">
                        <h2 className="font-semibold text-lg mb-1">🔍 Result:</h2>
                        <pre className="text-sm text-gray-800">{JSON.stringify(attackResult, null, 2)}</pre>
                    </div>
                )}

                <h2 className="text-xl font-semibold mb-2">📜 Attack Log</h2>
                <div className="bg-white border rounded p-4 mb-6 max-h-80 overflow-auto">
                    {attackLog.length === 0 ? (
                        <p>No attacks logged yet.</p>
                    ) : (
                        attackLog.map((log, index) => (
                            <div key={index} className="mb-3 border-b pb-2">
                <span
                    className={`inline-block w-2 h-2 rounded-full mr-2 ${
                        log.status === "Blocked" ? "bg-red-500" : "bg-green-500"
                    }`}
                ></span>
                                <strong>{log.attack_type}</strong> — {log.status} —
                                <span className="text-sm text-gray-500"> {log.message}</span>
                                <div className="text-xs text-gray-400">{log.timestamp}</div>
                            </div>
                        ))
                    )}
                </div>

                <h2 className="text-xl font-semibold mb-2">🧠 SHAP/XAI Explanation</h2>
                <div className="bg-white border p-4 rounded">
                    <p className="text-sm text-gray-600">
                        SHAP visual explanation would appear here, showing the most influential features that
                        triggered the access denial (e.g., sensor_id anomaly, temperature drift, frequency spike).
                        Integrate this with SHAP plots once model integration is available.
                    </p>
                    {/* You can embed a placeholder image or iframe of SHAP visualization here */}
                </div>
            </div>
        </Layout>
    );
};

export default AttackSimulationDashboard;
