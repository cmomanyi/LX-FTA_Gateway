import React, { useEffect, useState } from "react";

const attackSamples = {
    spoofing: {
        sensor_id: "sensor-x",
        payload: "abc123",
        ecc_signature: "invalid_hash"
    },
    replay: {
        sensor_id: "sensor-x",
        timestamp: "",
        nonce: ""
    },
    firmware: {
        sensor_id: "sensor-x",
        firmware_version: "1.0.3",
        firmware_signature: "invalid_signature"
    },
    ml_evasion: {
        sensor_id: "sensor-x",
        values: [1.2, 2.3, 3.4]
    },
    ddos: {
        sensor_id: "sensor-x",
        threshold: 10
    },
    sensor_hijack: {
        sensor_id: "sensor-x",
        unauthorized_access: true
    },
    api_abuse: {
        sensor_id: "sensor-x",
        excessive_calls: 200
    },
    tamper_breach: {
        sensor_id: "sensor-x",
        casing_opened: true
    },
    side_channel: {
        sensor_id: "sensor-x",
        timing_leak: "detected"
    }
};

const DashboardMain = () => {
    const [sensorTypes, setSensorTypes] = useState([]);
    const [sensorIDs, setSensorIDs] = useState([]);
    const [attackTypes, setAttackTypes] = useState([]);
    const [selectedType, setSelectedType] = useState("");
    const [selectedID, setSelectedID] = useState("");
    const [selectedAttack, setSelectedAttack] = useState("");
    const [attackData, setAttackData] = useState("");
    const [ddosThreshold, setDdosThreshold] = useState(10);
    const [liveLogs, setLiveLogs] = useState([]);

    useEffect(() => {
        fetch("https://api.lx-gateway.tech/api/sensor-types")
            .then(res => res.json())
            .then(data => {
                setSensorTypes(data.sensor_types || []);
                setSensorIDs(data.sensor_ids || []);
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
                const response = await fetch("https://api.lx-gateway.tech/api/alerts");
                const data = await response.json();
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
            return alert("Please select sensor ID and attack type.");
        }

        let payload;
        try {
            payload = JSON.stringify(JSON.parse(attackData || "{}"));
        } catch (e) {
            return alert("Invalid JSON in attack data.");
        }

        fetch(`https://api.lx-gateway.tech/simulate/${selectedAttack}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: payload
        })
            .then(res => res.json())
            .then(result => {
                alert(`Attack simulation result: ${result.message}`);
            })
            .catch(err => console.error("Attack simulation failed", err));
    };

    const handleAttackSelect = (val) => {
        setSelectedAttack(val);

        if (attackSamples[val]) {
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
        } else {
            setAttackData("");
        }
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
                    {sensorTypes.map(type => <option key={type} value={type}>{type}</option>)}
                </select>

                <select onChange={e => setSelectedID(e.target.value)} className="p-2 border rounded">
                    <option value="">Select Sensor ID</option>
                    {sensorIDs.filter(id => !selectedType || id.startsWith(selectedType.slice(0, 4))).map(id => <option key={id} value={id}>{id}</option>)}
                </select>

                <select onChange={e => handleAttackSelect(e.target.value)} className="p-2 border rounded">
                    <option value="">Select Attack Type</option>
                    {attackTypes.map(type => <option key={type.type} value={type.type}>{type.type}</option>)}
                </select>

                {selectedAttack === "ddos" && (
                    <select
                        value={ddosThreshold}
                        onChange={e => handleThresholdChange(e.target.value)}
                        className="p-2 border rounded"
                    >
                        <option value={5}>5</option>
                        <option value={10}>10</option>
                        <option value={15}>15</option>
                        <option value={20}>20</option>
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

            <button onClick={handleAttack} className="bg-red-500 text-white px-4 py-2 rounded">Simulate Attack</button>

            <div className="mt-8">
                <h3 className="text-lg font-semibold mb-2">Live Audit Trail</h3>
                <div className="bg-gray-100 p-4 rounded max-h-60 overflow-auto">
                    {liveLogs.map((log, idx) => (
                        <div key={idx} className="mb-2 border-b pb-2">
                            <p><strong>{log.timestamp}</strong> | {log.sensor_id}</p>
                            <p>{(log?.attack_type || "unknown").toUpperCase()}: {log.message}</p>
                            <p className={`text-sm ${log.severity === 'High' ? 'text-red-600' : 'text-green-600'}`}>
                                Status: {log.severity === 'High' ? '🚫 Blocked' : '✅ Allowed'} — Severity: {log.severity}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default DashboardMain;
