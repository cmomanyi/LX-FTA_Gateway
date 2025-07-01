import React, { useEffect, useState } from "react";

const attackSamples = {
    spoofing: { sensor_id: "sensor-x", payload: "abc123", ecc_signature: "invalid_hash" },
    replay: { sensor_id: "sensor-x", timestamp: "", nonce: "" },
    firmware: { sensor_id: "sensor-x", firmware_version: "1.0.3", firmware_signature: "invalid_signature" },
    ml_evasion: { sensor_id: "sensor-x", values: [1.2, 2.3, 3.4] },
    ddos: { sensor_id: "sensor-x", threshold: 10 },
    sensor_hijack: { sensor_id: "sensor-x", unauthorized_access: true },
    api_abuse: { sensor_id: "sensor-x", excessive_calls: 200 },
    tamper_breach: { sensor_id: "sensor-x", casing_opened: true },
    side_channel: { sensor_id: "sensor-x", timing_leak: "detected" }
};

const sensorPrefixMap = {
    soil: "soil-",
    water: "water-",
    plant: "plant-",
    threat: "threat-",
    atmospheric: "atm-"
};

const DashboardMain = () => {
    const [sensorIDs, setSensorIDs] = useState([]);
    const [groupedSensors, setGroupedSensors] = useState({});
    const [sensorTypes, setSensorTypes] = useState([]);

    const [attackTypes, setAttackTypes] = useState([]);
    const [selectedType, setSelectedType] = useState("");
    const [selectedID, setSelectedID] = useState("");
    const [selectedAttack, setSelectedAttack] = useState("");
    const [attackData, setAttackData] = useState("");
    const [ddosThreshold, setDdosThreshold] = useState(10);
    const [liveLogs, setLiveLogs] = useState([]);
    const [resultMessage, setResultMessage] = useState("");

    useEffect(() => {
        fetch("https://api.lx-gateway.tech/api/sensor-ids")
            .then(res => res.json())
            .then(data => {
                const allIDs = data.sensor_ids || [];
                setSensorIDs(allIDs);

                const groups = {};
                allIDs.forEach(id => {
                    for (const [type, prefix] of Object.entries(sensorPrefixMap)) {
                        if (id.startsWith(prefix)) {
                            if (!groups[type]) groups[type] = [];
                            groups[type].push(id);
                        }
                    }
                });

                setGroupedSensors(groups);
                setSensorTypes(Object.keys(groups));
            });

        fetch("https://api.lx-gateway.tech/api/attack-types")
            .then(res => res.json())
            .then(data => {
                setAttackTypes(data.attack_types || []);
            });
    }, []);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const res = await fetch("https://api.lx-gateway.tech/api/alerts");
                const data = await res.json();
                setLiveLogs(data.alerts || []);
            } catch (err) {
                console.error("Failed to fetch alerts:", err);
            }
        };
        fetchAlerts();
        const interval = setInterval(fetchAlerts, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleAttack = () => {
        if (!selectedID || !selectedAttack) {
            setResultMessage("❗ Please select sensor ID and attack type.");
            return;
        }

        let payload;
        try {
            payload = JSON.stringify(JSON.parse(attackData || "{}"));
        } catch (e) {
            setResultMessage("❗ Invalid JSON in attack data.");
            return;
        }

        fetch(`https://api.lx-gateway.tech/simulate/${selectedAttack}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: payload
        })
            .then(res => res.json())
            .then(result => {
                const isBlocked =
                    result.blocked ||
                    /🛑|high/i.test(result.severity) ||
                    /blocked/i.test(result.message);

                const status = isBlocked ? "🚫 Blocked" : "✅ Allowed";
                setResultMessage(`${status} — ${result.message}`);
            })
            .catch(err => {
                console.error("Attack simulation failed", err);
                setResultMessage("❌ Attack simulation failed.");
            });
    };

    const handleAttackSelect = (val) => {
        setSelectedAttack(val);
        const sample = { ...attackSamples[val] };

        if (val === "replay") {
            sample.timestamp = new Date().toISOString();
            sample.nonce = `nonce-${Math.floor(Math.random() * 1000000)}`;
        }

        if (val === "ddos") {
            sample.threshold = ddosThreshold;
        }

        if (selectedID) {
            sample.sensor_id = selectedID;
        }

        setAttackData(JSON.stringify(sample, null, 2));
    };

    const handleThresholdChange = (val) => {
        setDdosThreshold(val);
        if (selectedAttack === "ddos") {
            const sample = {
                ...attackSamples.ddos,
                sensor_id: selectedID || "sensor-x",
                threshold: parseInt(val)
            };
            setAttackData(JSON.stringify(sample, null, 2));
        }
    };

    return (
        <div className="p-4">
            <h2 className="text-xl font-bold mb-4">Simulate Sensor Attack</h2>

            <div className="grid grid-cols-2 gap-4 mb-4">
                <select onChange={e => setSelectedType(e.target.value)} className="p-2 border rounded">
                    <option value="">Select Sensor Type</option>
                    {sensorTypes.map(type => (
                        <option key={type} value={type}>{type}</option>
                    ))}
                </select>

                <select onChange={e => setSelectedID(e.target.value)} className="p-2 border rounded">
                    <option value="">Select Sensor ID</option>
                    {(groupedSensors[selectedType] || []).map(id => (
                        <option key={id} value={id}>{id}</option>
                    ))}
                </select>

                <select onChange={e => handleAttackSelect(e.target.value)} className="p-2 border rounded">
                    <option value="">Select Attack Type</option>
                    {attackTypes.map(type => (
                        <option key={type.type} value={type.type}>{type.type}</option>
                    ))}
                </select>

                {selectedAttack === "ddos" && (
                    <select
                        value={ddosThreshold}
                        onChange={e => handleThresholdChange(e.target.value)}
                        className="p-2 border rounded"
                    >
                        {[5, 10, 15, 20].map(v => (
                            <option key={v} value={v}>{v}</option>
                        ))}
                    </select>
                )}

                <textarea
                    className="col-span-2 p-2 border rounded"
                    rows={6}
                    placeholder="Paste or modify attack JSON here"
                    value={attackData}
                    onChange={e => setAttackData(e.target.value)}
                />
            </div>

            <button onClick={handleAttack} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition">
                Simulate Attack
            </button>

            {resultMessage && (
                <div className="mt-4 text-sm font-medium text-blue-800 bg-blue-100 p-2 rounded">
                    {resultMessage}
                </div>
            )}

            <div className="mt-8">
                <h3 className="text-lg font-semibold mb-2">Live Audit Trail</h3>
                <div className="bg-gray-100 p-4 rounded max-h-60 overflow-auto text-sm">
                    {liveLogs.map((log, idx) => {
                        const severity = log.severity || "Unknown";
                        const isBlocked =
                            log.blocked ||
                            /🛑|high/i.test(severity) ||
                            /blocked/i.test(log.message);

                        const status = isBlocked ? "🚫 Blocked" : "✅ Allowed";
                        const severityClass = severity.toLowerCase().includes("high") || severity.includes("🛑")
                            ? "text-red-600"
                            : "text-green-600";

                        return (
                            <div key={idx} className="mb-2 border-b pb-2">
                                <p><strong>{log.timestamp || "N/A"}</strong> | {log.sensor_id || "unknown"}</p>
                                <p>{(log.attack_type || "unknown").toUpperCase()}: {log.message || "No message"}</p>
                                <p className={`text-xs ${severityClass}`}>
                                    Status: {status} — Severity: {severity}
                                </p>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default DashboardMain;
