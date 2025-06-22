// DashboardMain.jsx
import React, { useEffect, useState } from "react";

const DashboardMain = () => {
    const [sensorTypes, setSensorTypes] = useState([]);
    const [sensorIds, setSensorIds] = useState([]);
    const [sensorType, setSensorType] = useState("soil");
    const [sensorNumber, setSensorNumber] = useState(1);
    const [attackTypes, setAttackTypes] = useState([]);
    const [attackType, setAttackType] = useState("");
    const [metric, setMetric] = useState(30.0);
    const [nonce, setNonce] = useState(Date.now().toString());
    const [wsStatus, setWsStatus] = useState("Disconnected");
    const [logs, setLogs] = useState([]);
    const [samplePayload, setSamplePayload] = useState("");

    const sensorId = `${sensorType}-${String(sensorNumber).padStart(4, "0")}`;

    useEffect(() => {
        fetch("https://api.lx-gateway.tech/api/sensor-types")
            .then(res => res.json())
            .then(data => {
                if (data && data.sensor_types?.length) {
                    setSensorTypes(data.sensor_types);
                    setSensorIds(data.sensor_ids);
                    setSensorType(data.sensor_types[0]);
                }
            })
            .catch(err => console.error("Failed to fetch sensor types", err));

        fetch("https://api.lx-gateway.tech/api/attack-types")
            .then(res => res.json())
            .then(data => {
                if (data?.attack_types?.length) {
                    setAttackTypes(data.attack_types);
                    setAttackType(data.attack_types[0].type);
                }
            })
            .catch(err => console.error("Failed to fetch attack types", err));
    }, []);

    useEffect(() => {
        const ws = new WebSocket("wss://api.lx-gateway.tech/ws/alerts");

        ws.onopen = () => setWsStatus("Connected");
        ws.onclose = () => setWsStatus("Disconnected");
        ws.onerror = () => setWsStatus("Error");
        ws.onmessage = (event) => {
            const alert = JSON.parse(event.data);
            setLogs(prev => [alert, ...prev]);
        };

        return () => ws.close();
    }, []);

    const getSensorNumbersForType = (type) => {
        return sensorIds
            .filter(id => id.startsWith(type))
            .map(id => parseInt(id.split("-")[1]))
            .filter(num => !isNaN(num));
    };

    const getSampleAttackPayload = () => {
        const timestamp = new Date().toISOString();
        const base = { sensor_id: sensorId, timestamp };

        switch (attackType) {
            case "spoofing":
                return JSON.stringify({ ...base, payload: "abc123", ecc_signature: "wronghash" }, null, 2);
            case "replay":
                return JSON.stringify({ ...base, nonce: `nonce-${Date.now()}` }, null, 2);
            case "firmware":
                return JSON.stringify({ ...base, firmware_version: "1.0.3", firmware_signature: "invalid_signature" }, null, 2);
            case "ml_evasion":
                return JSON.stringify({ ...base, values: Array(10).fill(Math.random() * 100) }, null, 2);
            case "ddos":
                return JSON.stringify({ ...base, threshold: 10 }, null, 2);
            default:
                return "{}";
        }
    };

    useEffect(() => {
        setSamplePayload(getSampleAttackPayload());
    }, [sensorType, sensorNumber, attackType]);

    const simulateSensor = async () => {
        const payload = JSON.parse(samplePayload);

        const endpointMap = {
            spoofing: "/api/validate",
            replay: "/api/replay-protect",
            firmware: "/api/detect/firmware_injection",
            ml_evasion: "/api/drift-detect",
            ddos: "/sensor/threat/ddos"
        };

        const endpoint = endpointMap[attackType];
        if (!endpoint) return;

        try {
            const res = await fetch(`https://api.lx-gateway.tech${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.message || data.attack_type) {
                setLogs(prev => [data, ...prev]);
            }
        } catch (err) {
            console.error("Failed to simulate sensor", err);
        }
    };

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4">📡 Sensor Simulator</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded shadow">
                    <label className="block font-medium">Sensor Type</label>
                    <select
                        className="w-full border p-2 rounded mb-2"
                        value={sensorType}
                        onChange={e => {
                            setSensorType(e.target.value);
                            setSensorNumber(getSensorNumbersForType(e.target.value)[0] || 1);
                        }}
                    >
                        {sensorTypes.map(type => (
                            <option key={type} value={type}>{type}</option>
                        ))}
                    </select>

                    <label className="block font-medium">Sensor Number</label>
                    <select
                        className="w-full border p-2 rounded mb-2"
                        value={sensorNumber}
                        onChange={e => setSensorNumber(Number(e.target.value))}
                    >
                        {getSensorNumbersForType(sensorType).map(n => (
                            <option key={n} value={n}>Sensor {n}</option>
                        ))}
                    </select>

                    <label className="block font-medium">Attack Type</label>
                    <select
                        className="w-full border p-2 rounded mb-2"
                        value={attackType}
                        onChange={e => setAttackType(e.target.value)}
                    >
                        {attackTypes.map(atk => (
                            <option key={atk.type} value={atk.type}>{atk.type} — {atk.description}</option>
                        ))}
                    </select>

                    <label className="block font-medium">Sample Attack Payload</label>
                    <textarea
                        readOnly
                        className="w-full border p-2 mb-2 rounded bg-gray-100 text-xs"
                        value={samplePayload}
                        rows={6}
                    />

                    <button
                        onClick={simulateSensor}
                        className="w-full bg-blue-600 text-white px-4 py-2 mt-2 rounded hover:bg-blue-700"
                    >
                        🚀 Simulate Attack
                    </button>
                </div>

                <div className="bg-white p-4 shadow rounded">
                    <p className="text-sm text-gray-500 mb-2">
                        WebSocket Status: {" "}
                        <span className={wsStatus === "Connected" ? "text-green-600" : "text-red-600"}>{wsStatus}</span>
                    </p>
                    <div className="overflow-auto max-h-96">
                        <table className="min-w-full text-sm">
                            <thead>
                            <tr>
                                <th className="px-2 py-1">Time</th>
                                <th className="px-2 py-1">Sensor</th>
                                <th className="px-2 py-1">Type</th>
                                <th className="px-2 py-1">Severity</th>
                                <th className="px-2 py-1">Status</th>
                            </tr>
                            </thead>
                            <tbody>
                            {logs.map((log, i) => (
                                <tr key={i}>
                                    <td className="px-2 py-1">{new Date(log.timestamp).toLocaleString()}</td>
                                    <td className="px-2 py-1">{log.sensor_id}</td>
                                    <td className="px-2 py-1">{log.attack_type || "Normal"}</td>
                                    <td className="px-2 py-1">{log.severity || "Low"}</td>
                                    <td className="px-2 py-1">{log.status || "accepted"}</td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardMain;
