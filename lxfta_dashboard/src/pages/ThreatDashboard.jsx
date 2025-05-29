import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { Radar } from "react-chartjs-2";
import { saveAs } from "file-saver";
import {
    Chart as ChartJS,
    RadialLinearScale,
    PointElement,
    LineElement,
    Filler,
    Tooltip,
    Legend,
} from "chart.js";

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

const SENSOR_TYPES = ["soil", "water", "plant", "atmospheric", "threat"];
const SENSOR_NUMBERS = [1, 2, 3, 4, 5];

const ATTACK_OPTIONS = [
    { label: "Spoofing", id: "spoofing", sensor_id: "unauthorized_99", description: "Unauthorized sensor mimicking a legitimate one" },
    { label: "Replay", id: "replay", sensor_id: "soil_01", description: "Old data with reused nonce to confuse systems" },
    { label: "Firmware Tampering", id: "firmware", sensor_id: "plant_02", description: "Modified sensor firmware sent without integrity check" },
    { label: "Overflow", id: "overflow", sensor_id: "water_01", description: "Excessively large or malformed metric values sent" }
];

const ThreatDashboard = () => {
    const [sensorType, setSensorType] = useState("soil");
    const [sensorNumber, setSensorNumber] = useState(1);
    const [metric, setMetric] = useState(30.0);
    const [nonce, setNonce] = useState(Date.now().toString());
    const [anomalies, setAnomalies] = useState([]);
    const [selectedAttack, setSelectedAttack] = useState("spoofing");
    const [wsStatus, setWsStatus] = useState("Disconnected");
    const [activeTab, setActiveTab] = useState("dashboard");

    const sensorId = `${sensorType}_${String(sensorNumber).padStart(2, "0")}`;

    useEffect(() => {
        const ws = new WebSocket("ws://127.0.0.1:8000/ws/alerts");
        ws.onopen = () => setWsStatus("Connected");
        ws.onclose = () => setWsStatus("Disconnected");
        ws.onerror = () => setWsStatus("Error");
        ws.onmessage = (event) => {
            const newAlert = JSON.parse(event.data);
            setAnomalies((prev) => [newAlert, ...prev]);
        };
        return () => ws.close();
    }, []);

    // const simulateSensor = async () => {
    //     const payload = {
    //         sensor_id: sensorId,
    //         metric: parseFloat(metric),
    //         nonce,
    //         timestamp: new Date().toISOString(),
    //     };
    //
    //     const res = await fetch("http://127.0.0.1:8000/sensor/threat", {
    //         method: "POST",
    //         headers: { "Content-Type": "application/json" },
    //         body: JSON.stringify(payload),
    //     });
    //
    //     const result = await res.json();
    //     if (result.attack_type || result.message) {
    //         setAnomalies((prev) => [result, ...prev]);
    //     }
    //
    //     setNonce(Date.now().toString());
    // };
    const simulateSensor = async () => {
        // Define clean value ranges for each sensor type
        const SENSOR_METRIC_RANGES = {
            soil: [20, 60],
            water: [5, 15],
            plant: [0.3, 0.9],
            atmospheric: [18, 30],
            threat: [0, 1], // Simulated safe threat reading
        };

        const [min, max] = SENSOR_METRIC_RANGES[sensorType] || [20, 50];
        const cleanMetric = parseFloat((Math.random() * (max - min) + min).toFixed(2));
        const freshNonce = Date.now().toString();
        const cleanTimestamp = new Date().toISOString();

        const payload = {
            sensor_id: sensorId,
            metric: cleanMetric,
            nonce: freshNonce,
            timestamp: cleanTimestamp,
        };

        try {
            const res = await fetch("http://127.0.0.1:8000/sensor/threat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const result = await res.json();
            if (result.attack_type || result.message) {
                setAnomalies((prev) => [result, ...prev]);
            }
            setNonce(Date.now().toString()); // refresh form input
            setMetric(cleanMetric); // update UI
        } catch (error) {
            console.error("Simulation failed:", error);
        }
    };


    const simulateAttack = async () => {
        const attack = ATTACK_OPTIONS.find((a) => a.id === selectedAttack);
        if (!attack) return alert("❌ Invalid attack type selected");

        const payload = {
            sensor_id: attack.sensor_id,
            metric: parseFloat(Math.random() * 100).toFixed(2),
            nonce: selectedAttack === "replay" ? "fixed_nonce_123" : Date.now().toString(),
            timestamp: new Date().toISOString(),
        };

        const res = await fetch("http://127.0.0.1:8000/sensor/threat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const result = await res.json();
        if (result.attack_type || result.message) {
            setAnomalies((prev) => [result, ...prev]);
        }
    };

    const exportLogs = () => {
        const blob = new Blob([JSON.stringify(anomalies, null, 2)], {
            type: "application/json",
        });
        saveAs(blob, "anomaly_logs.json");
    };

    const getRadarData = () => {
        const labels = ["metric", "integrity", "latency", "nonce_reuse", "spoof_risk"];
        const randomScores = Array.from({ length: labels.length }, () =>
            Math.floor(Math.random() * 100)
        );

        return {
            labels,
            datasets: [
                {
                    label: "Anomaly Fingerprint",
                    data: randomScores,
                    backgroundColor: "rgba(255, 99, 132, 0.2)",
                    borderColor: "rgba(255, 99, 132, 1)",
                    borderWidth: 1,
                },
            ],
        };
    };

    return (
        <div className="flex">
            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
            <div className="flex-1 p-6 bg-gray-100 min-h-screen">
                {activeTab === "dashboard" && (
                    <>
                        <h1 className="text-2xl font-bold mb-4">🛡️ Threat Detection Dashboard</h1>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                            {/* Sensor Simulation */}
                            <div className="bg-white p-4 shadow rounded">
                                <h2 className="font-semibold text-lg mb-2">📡 Simulate Sensor</h2>
                                <label className="block font-medium">Sensor Type</label>
                                <select className="w-full border p-2 mb-2 rounded" value={sensorType} onChange={(e) => setSensorType(e.target.value)}>
                                    {SENSOR_TYPES.map((type) => (
                                        <option key={type} value={type}>{type}</option>
                                    ))}
                                </select>

                                <label className="block font-medium">Sensor Number</label>
                                <select className="w-full border p-2 mb-2 rounded" value={sensorNumber} onChange={(e) => setSensorNumber(Number(e.target.value))}>
                                    {SENSOR_NUMBERS.map((num) => (
                                        <option key={num} value={num}>Sensor {num}</option>
                                    ))}
                                </select>

                                <label className="block font-medium">Metric</label>
                                <input type="number" className="w-full border p-2 mb-2 rounded" value={metric} onChange={(e) => setMetric(e.target.value)} />

                                <label className="block font-medium">Nonce</label>
                                <input className="w-full border p-2 mb-2 rounded" value={nonce} onChange={(e) => setNonce(e.target.value)} />

                                <button onClick={simulateSensor} className="w-full bg-blue-600 text-white px-4 py-2 mt-2 rounded hover:bg-blue-700">
                                    🚀 Simulate Sensor
                                </button>
                            </div>

                            {/* Attack Simulation */}
                            <div className="bg-white p-4 shadow rounded">
                                <h2 className="font-semibold text-lg mb-2">⚔️ Simulate Attack</h2>
                                <label className="block font-medium">Attack Type</label>
                                <select className="w-full border p-2 rounded" value={selectedAttack} onChange={(e) => setSelectedAttack(e.target.value)}>
                                    {ATTACK_OPTIONS.map((opt) => (
                                        <option key={opt.id} value={opt.id}>{opt.label}</option>
                                    ))}
                                </select>
                                <p className="text-sm text-gray-600 italic mt-1">{ATTACK_OPTIONS.find((a) => a.id === selectedAttack)?.description}</p>
                                <button onClick={simulateAttack} className="w-full mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
                                    🧪 Simulate Selected Attack
                                </button>
                            </div>
                        </div>

                        {/* Logs */}
                        <div className="mb-4 flex items-center justify-between">
              <span className="text-sm text-gray-600">
                WebSocket Status:{" "}
                  <strong className={wsStatus === "Connected" ? "text-green-600" : "text-red-500"}>
                  {wsStatus}
                </strong>
              </span>
                            <button onClick={exportLogs} className="px-3 py-1 bg-green-600 text-white rounded">
                                📤 Export Logs
                            </button>
                        </div>

                        <div className="overflow-x-auto bg-white shadow-md rounded mb-6">
                            <table className="min-w-full text-sm text-left">
                                <thead className="bg-gray-100 border-b">
                                <tr>
                                    <th className="px-4 py-2">Time</th>
                                    <th className="px-4 py-2">Sensor</th>
                                    <th className="px-4 py-2">Attack</th>
                                    <th className="px-4 py-2">Message</th>
                                    <th className="px-4 py-2">Severity</th>
                                    <th className="px-4 py-2">Status</th>
                                </tr>
                                </thead>
                                <tbody>
                                {anomalies.map((log, index) => (
                                    <tr key={index} className="border-b hover:bg-gray-50">
                                        <td className="px-4 py-2">{new Date(log.timestamp).toLocaleString()}</td>
                                        <td className="px-4 py-2">{log.sensor_id}</td>
                                        <td className="px-4 py-2">{log.attack_type || "Normal"}</td>
                                        <td className="px-4 py-2">{log.message || "No anomaly"}</td>
                                        <td className="px-4 py-2 text-red-600">{log.severity || "Low"}</td>
                                        <td className="px-4 py-2">{log.status || "accepted"}</td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </div>
                    </>
                )}

                {activeTab === "analytics" && (
                    <div className="text-gray-500 italic text-center mt-20">
                        📈 Analytics coming soon...
                    </div>
                )}
            </div>
        </div>
    );
};

export default ThreatDashboard;
