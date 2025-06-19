import React, { useState, useEffect } from "react";
import axios from "axios";
import Layout from "../components/Layout";

const ShapAttackDashboard = () => {
    const [attackType, setAttackType] = useState("spoofing");
    const [attackResult, setAttackResult] = useState(null);
    const [attackLog, setAttackLog] = useState([]);
    const [shapExplanation, setShapExplanation] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchLog = async () => {
        try {
            const response = await axios.get("https://api.lx-gateway.tech/attack-log");
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
            const response = await axios.post("https://api.lx-gateway.tech/simulate-attack", form);
            setAttackResult(response.data);
            fetchLog();

            // Trigger SHAP explanation (simulate realistic inputs)
            const shapInput = {
                temperature: 87.0,
                moisture: 25.0,
                ph: 5.2,
                battery_level: 3.0,
                frequency: 12.0
            };
            const shapRes = await axios.post("http://localhost:8001/explain", shapInput);
            setShapExplanation(shapRes.data);

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
                    {shapExplanation ? (
                        <>
                            <p className="text-sm text-gray-600 mb-2">
                                Prediction: <strong>{shapExplanation.prediction}</strong><br />
                                Base Value: {shapExplanation.base_value}<br />
                                Timestamp: {shapExplanation.timestamp}
                            </p>
                            <ul className="text-sm list-disc pl-5">
                                {shapExplanation.features.map((feat, i) => (
                                    <li key={i}>
                                        {feat.feature}: <span className="text-blue-600 font-medium">{feat.contribution}</span>
                                    </li>
                                ))}
                            </ul>
                        </>
                    ) : (
                        <p className="text-sm text-gray-600">Run a simulation to see SHAP output.</p>
                    )}
                </div>
            </div>
        </Layout>
    );
};

export default ShapAttackDashboard;
