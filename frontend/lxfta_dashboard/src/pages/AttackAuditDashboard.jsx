
import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const ATTACK_TYPES = [
    { id: "ddos", label: "DDoS Attack" },
    { id: "spoofing", label: "Spoofing" },
    { id: "replay", label: "Replay Attack" },
    { id: "drift", label: "ML Evasion (Drift)" },
    { id: "firmware_injection", label: "Firmware Injection" },
    { id: "sensor_hijack", label: "Sensor Hijack" },
    { id: "api_abuse", label: "API Abuse" },
    { id: "tamper_breach", label: "Tamper Breach" },
    { id: "side_channel", label: "Side-Channel Attack" },
    { id: "ddos_flood", label: "DDoS Flood" }
];

const AttackAuditDashboard = () => {
    const [availableSensorTypes, setAvailableSensorTypes] = useState([]);
    const [availableSensorIds, setAvailableSensorIds] = useState([]);
    const [sensorType, setSensorType] = useState("");
    const [sensorId, setSensorId] = useState("");
    const [attackType, setAttackType] = useState("ddos");
    const [message, setMessage] = useState("");
    const [nonce, setNonce] = useState("");
    const [timestamp, setTimestamp] = useState("");
    const [driftValues, setDriftValues] = useState("");
    const [ddosThreshold, setDdosThreshold] = useState(10);
    const [firmwareSignature, setFirmwareSignature] = useState("invalid_signature_xx");
    const [firmwareContent, setFirmwareContent] = useState("unsigned_code_block");
    const [logs, setLogs] = useState([]);
    const [filterText, setFilterText] = useState("");

    const fullSensorId = sensorType && sensorId ? `${sensorType}_${sensorId}` : "";

    useEffect(() => {
        fetch("http://127.0.0.1:8000/api/sensor-types")
            .then(res => res.json())
            .then(data => {
                setAvailableSensorTypes(data.sensor_types);
                setAvailableSensorIds(data.sensor_ids);
            });

        fetchLogs();

        const ws = new WebSocket("ws://127.0.0.1:8000/ws/alerts");
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            toast.error(`🔴 ${data.attack_type.toUpperCase()} on ${data.sensor_id}`, {
                position: "top-right",
                autoClose: 6000,
                theme: "dark",
            });

            const isBlocked = data.blocked === true || /attack detected/i.test(data.message);
            setLogs(prev => [{ ...data, blocked: isBlocked ? "Yes" : "No" }, ...prev]);
        };

        return () => ws.close();
    }, []);

    const fetchLogs = () => {
        fetch("http://127.0.0.1:8000/api/logs")
            .then(res => res.json())
            .then(data => {
                const normalized = (data.logs || []).map(log => ({
                    ...log,
                    blocked: log.blocked === true ? "Yes" : "No"
                }));
                setLogs(normalized);
            });
    };

    const simulateAttack = async () => {
        if (!sensorType || !sensorId || !attackType) return alert("Please fill all fields.");
        if ((attackType === "spoofing" || attackType === "replay") && !message.trim()) return alert("Message is required.");
        if (attackType === "replay" && !nonce.trim()) return alert("Nonce is required.");
        if (attackType === "drift" && !driftValues.trim()) return alert("Drift values required.");

        try {
            let url = "";
            let payload = {};

            switch (attackType) {
                case "ddos":
                    url = "http://127.0.0.1:8000/sensor/threat/ddos";
                    payload = {
                        sensor_id: fullSensorId,
                        attack_type: attackType,
                        message,
                        threshold: ddosThreshold,
                        timestamp: new Date().toISOString()
                    };
                    break;
                case "spoofing":
                    url = "http://127.0.0.1:8000/api/validate";
                    payload = {
                        sensor_id: fullSensorId,
                        payload: message,
                        ecc_signature: "fake_signature_zzz999"
                    };
                    break;
                case "replay":
                    url = "http://127.0.0.1:8000/api/replay-protect";
                    payload = {
                        sensor_id: fullSensorId,
                        payload: message,
                        timestamp: timestamp || new Date().toISOString(),
                        nonce
                    };
                    break;
                case "drift":
                    url = "http://127.0.0.1:8000/api/drift-detect";
                    payload = {
                        sensor_id: fullSensorId,
                        values: driftValues.split(",").map(v => parseFloat(v.trim()))
                    };
                    break;
                case "firmware_injection":
                    url = `http://127.0.0.1:8000/api/detect/firmware_injection`;
                    payload = {
                        sensor_id: fullSensorId,
                        firmware_content: firmwareContent,
                        firmware_signature: firmwareSignature
                    };
                    break;
                default:
                    url = `http://127.0.0.1:8000/api/detect/${attackType}`;
                    payload = { sensor_id: fullSensorId };
                    break;
            }

            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            const isBlocked = data.blocked === true || /attack detected/i.test(data.message);

            toast[data.severity === "High" ? "error" : "success"](data.status, {
                position: "top-right",
                autoClose: 5000,
                theme: data.severity === "High" ? "colored" : "light",
            });

            setLogs(prev => [{
                timestamp: new Date().toISOString(),
                sensor_id: fullSensorId,
                attack_type: attackType,
                message: data.message || message || data.status,
                severity: data.severity || "High",
                blocked: isBlocked ? "Yes" : "No"
            }, ...prev]);

            fetchLogs();
            setMessage("");
        } catch (err) {
            console.error("Simulation error:", err);
            alert("Attack simulation failed");
        }
    };

    return (
        <Layout>
            <ToastContainer />
            <h1 className="text-2xl font-bold mb-4">🚨 Attack Simulation Dashboard</h1>
            <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <label>Sensor Type</label>
                    <select value={sensorType} onChange={(e) => setSensorType(e.target.value)} className="w-full border p-2 rounded">
                        <option value="">Select Sensor Type</option>
                        {availableSensorTypes.map((type) => (
                            <option key={type} value={type}>{type}</option>
                        ))}
                    </select>
                </div>
                <div>
                    <label>Sensor ID</label>
                    <select value={sensorId} onChange={(e) => setSensorId(e.target.value)} className="w-full border p-2 rounded">
                        <option value="">Select Sensor ID</option>
                        {availableSensorIds.map((id) => (
                            <option key={id} value={id}>{id}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="bg-white p-4 rounded shadow mb-6">
                <label>Attack Type</label>
                <select value={attackType} onChange={(e) => setAttackType(e.target.value)} className="w-full border p-2 mb-2 rounded">
                    {ATTACK_TYPES.map((type) => (
                        <option key={type.id} value={type.id}>{type.label}</option>
                    ))}
                </select>

                {attackType === "ddos" && (
                    <>
                        <label>Message</label>
                        <textarea className="w-full border p-2 mb-2" value={message} onChange={(e) => setMessage(e.target.value)} />
                        <label>DDoS Threshold</label>
                        <input type="number" className="w-full border p-2 mb-2" value={ddosThreshold} onChange={(e) => setDdosThreshold(Number(e.target.value))} />
                    </>
                )}

                {attackType === "spoofing" || attackType === "replay" ? (
                    <>
                        <label>Payload</label>
                        <textarea className="w-full border p-2 mb-2" value={message} onChange={(e) => setMessage(e.target.value)} />
                    </>
                ) : null}

                {attackType === "replay" && (
                    <>
                        <label>Nonce</label>
                        <input className="w-full border p-2 mb-2" value={nonce} onChange={(e) => setNonce(e.target.value)} />
                        <label>Timestamp</label>
                        <input className="w-full border p-2 mb-2" value={timestamp} onChange={(e) => setTimestamp(e.target.value)} />
                    </>
                )}

                {attackType === "drift" && (
                    <>
                        <label>Drift Values</label>
                        <input className="w-full border p-2 mb-2" value={driftValues} onChange={(e) => setDriftValues(e.target.value)} />
                    </>
                )}

                {attackType === "firmware_injection" && (
                    <>
                        <label>Firmware Content</label>
                        <textarea className="w-full p-2 border rounded mb-2" value={firmwareContent} onChange={(e) => setFirmwareContent(e.target.value)} />
                        <label>Firmware Signature</label>
                        <select className="w-full p-2 border rounded mb-2" value={firmwareSignature} onChange={(e) => setFirmwareSignature(e.target.value)}>
                            <option value="invalid_signature_xx">🚫 Invalid Signature</option>
                            <option value="valid_signature_123">✅ Valid Signature</option>
                        </select>
                    </>
                )}

                <button onClick={simulateAttack} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">🚨 Launch Attack</button>
            </div>

            <div className="bg-white p-4 rounded shadow">
                <div className="flex justify-between mb-2">
                    <h2 className="text-lg font-semibold">📋 Attack Logs</h2>
                </div>
                <table className="min-w-full text-sm">
                    <thead className="bg-gray-100 sticky top-0">
                    <tr>
                        <th className="px-4 py-2">Timestamp</th>
                        <th className="px-4 py-2">Sensor ID</th>
                        <th className="px-4 py-2">Attack</th>
                        <th className="px-4 py-2">Message</th>
                        <th className="px-4 py-2">Severity</th>
                        <th className="px-4 py-2">Blocked</th>
                    </tr>
                    </thead>
                    <tbody>
                    {logs.map((log, i) => (
                        <tr key={i} className="border-b hover:bg-gray-50">
                            <td className="px-4 py-2">{new Date(log.timestamp).toLocaleString()}</td>
                            <td className="px-4 py-2">{log.sensor_id}</td>
                            <td className="px-4 py-2">{log.attack_type}</td>
                            <td className="px-4 py-2">{log.message}</td>
                            <td className="px-4 py-2">{log.severity}</td>
                            <td className="px-4 py-2 font-semibold">
                                {log.severity === "High" ? (
                                    <span className="text-red-600">🛡️ Blocked</span>
                                ) : (
                                    <span className="text-green-600">✅ Allowed</span>
                                )}
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </Layout>
    );
};

export default AttackAuditDashboard;
