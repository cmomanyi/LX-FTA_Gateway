import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import Sidebar from "../components/Sidebar";

const ATTACK_TYPES = {
    spoofing: {
        endpoint: "/api/validate",
        payload: (sensorId, valid = true) => ({
            sensor_id: sensorId,
            payload: "testPayload",
            ecc_signature: valid
                ? window.btoa(sensorId + "testPayload")
                : "invalid_signature"
        })
    },
    replay: {
        endpoint: "/api/replay-protect",
        payload: (sensorId) => ({
            sensor_id: sensorId,
            timestamp: new Date().toISOString(),
            nonce: `${sensorId}-${Date.now()}`
        })
    },
    firmware: {
        endpoint: "/api/detect/firmware_injection",
        payload: (sensorId) => ({
            sensor_id: sensorId,
            firmware_version: "1.0.3",
            firmware_signature: "invalid_signature"
        })
    },
    ddos: {
        endpoint: "/sensor/threat/ddos",
        payload: (sensorId) => ({ sensor_id: sensorId, threshold: 10 })
    },
    ml: {
        endpoint: "/api/drift-detect",
        payload: (sensorId) => ({ sensor_id: sensorId, values: Array(10).fill(Math.random() * 100) })
    }
};

const ThreatDashboard = () => {
    const [sensorTypes, setSensorTypes] = useState([]);
    const [sensorIds, setSensorIds] = useState([]);
    const [selectedType, setSelectedType] = useState("threat");
    const [selectedSensorId, setSelectedSensorId] = useState("");
    const [selectedAttack, setSelectedAttack] = useState("spoofing");
    const [response, setResponse] = useState(null);

    useEffect(() => {
        fetch("https://api.lx-gateway.tech/api/sensor-types")
            .then(res => res.json())
            .then(data => {
                setSensorTypes(data.sensor_types);
                filterSensorIds(data.sensor_ids, selectedType);
            });
    }, []);

    useEffect(() => {
        fetch("https://api.lx-gateway.tech/api/sensor-types")
            .then(res => res.json())
            .then(data => {
                filterSensorIds(data.sensor_ids, selectedType);
            });
    }, [selectedType]);

    const filterSensorIds = (allIds, type) => {
        const filtered = allIds.filter(id => id.startsWith(type));
        setSensorIds(filtered);
        setSelectedSensorId(filtered[0] || "");
    };

    const simulateAttack = async () => {
        const config = ATTACK_TYPES[selectedAttack];
        if (!config) return alert("Invalid attack selected");
        const body = config.payload(selectedSensorId);

        try {
            const res = await fetch(`https://api.lx-gateway.tech${config.endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            });
            const data = await res.json();
            setResponse(data);
        } catch (err) {
            console.error("Attack simulation failed", err);
            alert("Failed to simulate attack");
        }
    };

    return (
        <Layout>
            <div className="flex">
                <Sidebar />
                <div className="flex-1 p-6 bg-white min-h-screen">
                    <h1 className="text-2xl font-semibold mb-4">⚠️ Threat Simulation</h1>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div>
                            <label className="block mb-1">Sensor Type</label>
                            <select
                                className="border p-2 w-full"
                                value={selectedType}
                                onChange={e => setSelectedType(e.target.value)}
                            >
                                {sensorTypes.map(type => (
                                    <option key={type} value={type}>{type}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block mb-1">Sensor ID</label>
                            <select
                                className="border p-2 w-full"
                                value={selectedSensorId}
                                onChange={e => setSelectedSensorId(e.target.value)}
                            >
                                {sensorIds.map(id => (
                                    <option key={id} value={id}>{id}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block mb-1">Attack Type</label>
                            <select
                                className="border p-2 w-full"
                                value={selectedAttack}
                                onChange={e => setSelectedAttack(e.target.value)}
                            >
                                {Object.keys(ATTACK_TYPES).map(type => (
                                    <option key={type} value={type}>{type}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <button
                        onClick={simulateAttack}
                        className="bg-red-600 text-white px-6 py-2 rounded hover:bg-red-700"
                    >
                        Simulate Attack
                    </button>

                    {response && (
                        <div className="mt-6 bg-gray-50 p-4 border rounded">
                            <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                                {JSON.stringify(response, null, 2)}
                            </pre>
                        </div>
                    )}
                </div>
            </div>
        </Layout>
    );
};

export default ThreatDashboard;
