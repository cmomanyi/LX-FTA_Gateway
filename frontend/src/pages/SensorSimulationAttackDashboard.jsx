import React, { useEffect, useState } from "react";
import axios from "axios";
import { saveAs } from "file-saver";
import Layout from "../components/Layout";


const SensorSimulationAttackDashboard = () => {
    const [sensorTypes, setSensorTypes] = useState([]);
    const [sensorIds, setSensorIds] = useState([]);
    const [selectedType, setSelectedType] = useState("");
    const [selectedId, setSelectedId] = useState("");
    const [attackType, setAttackType] = useState("");
    const [formData, setFormData] = useState({});
    const [logs, setLogs] = useState([]);

    const attackFields = {
        ddos: ["threshold"],
        spoofing: ["payload", "ecc_signature"],
        firmware_injection: ["firmware_signature"],
        replay: ["nonce", "timestamp"],
        drift: ["values"]
    };

    useEffect(() => {
        axios.get("https://api.lx-gateway.tech/api/sensor-types").then((res) => {
            setSensorTypes(res.data.sensor_types || []);
            setSensorIds(res.data.sensor_ids || []);
        });

        const ws = new WebSocket("wss://api.lx-gateway.tech/ws/alerts");
        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                setLogs((prev) => [msg, ...prev]);
            } catch (e) {
                console.error("Invalid WS message", e);
            }
        };
        ws.onerror = (err) => console.error("WebSocket error:", err);
        return () => ws.close();
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const simulateAttack = async () => {
        try {
            let url = "";
            let payload = { sensor_id: selectedId };

            switch (attackType) {
                case "ddos":
                    url = "https://api.lx-gateway.tech/sensor/threat/ddos";
                    payload.threshold = parseInt(formData.threshold) || 10;
                    break;
                case "spoofing":
                    url = "https://api.lx-gateway.tech/api/validate";
                    payload.payload = formData.payload;
                    payload.ecc_signature = formData.ecc_signature;
                    break;
                case "firmware_injection":
                    url = "https://api.lx-gateway.tech/api/detect/firmware_injection";
                    payload.firmware_signature = formData.firmware_signature;
                    break;
                case "replay":
                    url = "https://api.lx-gateway.tech/api/replay-protect";
                    payload.nonce = formData.nonce;
                    payload.timestamp = formData.timestamp;
                    break;
                case "drift":
                    url = "https://api.lx-gateway.tech/api/drift-detect";
                    payload.values = formData.values.split(",").map(Number);
                    break;
                default:
                    return;
            }

            const res = await axios.post(url, payload);
            setLogs((prev) => [res.data, ...prev]);
        } catch (err) {
            console.error("Attack simulation failed", err);
        }
    };

    const exportLogs = () => {
        const csv = logs.map((log) =>
            `${log.timestamp},${log.sensor_id},${log.attack_type},${log.message}`
        ).join("\n");

        const blob = new Blob(["Timestamp,Sensor ID,Attack Type,Message\n" + csv], { type: "text/csv;charset=utf-8" });
        saveAs(blob, "sensor-attack-logs.csv");
    };

    return (
        <Layout>
            <div className="p-4">
                <h2 className="text-xl font-bold mb-2">Sensor Attack Simulator</h2>

                <div className="mb-4">
                    <label className="block font-medium">Sensor Type</label>
                    <select
                        className="border p-2 w-full"
                        value={selectedType}
                        onChange={(e) => setSelectedType(e.target.value)}
                    >
                        <option value="">Select Type</option>
                        {sensorTypes.map((type) => (
                            <option key={type}>{type}</option>
                        ))}
                    </select>
                </div>

                <div className="mb-4">
                    <label className="block font-medium">Sensor ID</label>
                    <select
                        className="border p-2 w-full"
                        value={selectedId}
                        onChange={(e) => setSelectedId(e.target.value)}
                    >
                        <option value="">Select Sensor ID</option>
                        {sensorIds.map((id) => (
                            <option key={id}>{id}</option>
                        ))}
                    </select>
                </div>

                <div className="mb-4">
                    <label className="block font-medium">Attack Type</label>
                    <select
                        className="border p-2 w-full"
                        value={attackType}
                        onChange={(e) => {
                            setAttackType(e.target.value);
                            setFormData({});
                        }}
                    >
                        <option value="">Select Attack</option>
                        {Object.keys(attackFields).map((type) => (
                            <option key={type}>{type}</option>
                        ))}
                    </select>
                </div>

                {attackType && attackFields[attackType]?.map((field) => (
                    <div key={field} className="mb-2">
                        <label className="block font-medium">{field}</label>
                        <input
                            className="border p-2 w-full"
                            name={field}
                            value={formData[field] || ""}
                            onChange={handleInputChange}
                            placeholder={`Enter ${field}`}
                        />
                    </div>
                ))}

                <button
                    className="bg-blue-600 text-white px-4 py-2 rounded"
                    onClick={simulateAttack}
                    disabled={!attackType || !selectedId}
                >
                    Simulate Attack
                </button>

                <button
                    className="ml-4 bg-green-600 text-white px-4 py-2 rounded"
                    onClick={exportLogs}
                    disabled={logs.length === 0}
                >
                    Export Logs to CSV
                </button>

                <div className="mt-6">
                    <h3 className="text-lg font-semibold mb-2">Live Alerts</h3>
                    <ul className="space-y-2 max-h-80 overflow-y-scroll">
                        {logs.map((log, i) => (
                            <li key={i} className="border p-2 rounded bg-gray-100">
                                <strong>{log.timestamp}</strong> – {log.sensor_id} – {log.attack_type}
                                <div>{log.message}</div>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </Layout>
    );
};

export default SensorSimulationAttackDashboard;
