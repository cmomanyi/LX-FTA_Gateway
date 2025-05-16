import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";

const SensorSecurityDashboard = () => {
    const [auditTrail, setAuditTrail] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [selectedAttack, setSelectedAttack] = useState("spoofing");

    useEffect(() => {
        const fetchAuditTrail = async () => {
            try {
                const res = await fetch("http://localhost:8000/api/audit");
                const data = await res.json();
                setAuditTrail(data);
            } catch (err) {
                console.error("Failed to load audit logs", err);
            }
        };

        fetchAuditTrail();
        const interval = setInterval(fetchAuditTrail, 10000);

        const token = localStorage.getItem("token");
        const ws = new WebSocket(`ws://localhost:8000/ws/alerts?token=${token}`);

        ws.onmessage = (event) => {
            const alert = JSON.parse(event.data);
            setAlerts((prev) => [alert, ...prev].slice(0, 20));
            setAuditTrail((prev) => [alert, ...prev].slice(0, 100));
        };

        return () => {
            clearInterval(interval);
            ws.close();
        };
    }, []);

    const handleTrigger = async () => {
        try {
            const res = await fetch(`http://localhost:8000/trigger?attack=${selectedAttack}`);
            const data = await res.json();
            alert(data.status);
        } catch (err) {
            console.error("Failed to trigger attacks", err);
        }
    };

    return (
        <Layout>
            <div className="p-6 bg-gray-50 min-h-screen">
                <div className="flex justify-between items-center mb-4">
                    <h1 className="text-xl font-semibold">Sensor Security Dashboard</h1>
                    <div className="flex items-center gap-2">
                        <select
                            value={selectedAttack}
                            onChange={(e) => setSelectedAttack(e.target.value)}
                            className="border px-2 py-1 rounded"
                        >
                            <option value="spoofing">Spoofing</option>
                            <option value="replay">Replay</option>
                            <option value="firmware">Firmware Injection</option>
                            <option value="ml">ML Evasion</option>
                            <option value="overflow">Overflow</option>
                            <option value="ddos">DDoS</option>
                            <option value="api">API Abuse</option>
                            <option value="sidechannel">Side Channel</option>
                            <option value="tamper">Tamper Breach</option>
                            <option value="hijack">Sensor Hijack</option>
                        </select>
                        <button onClick={handleTrigger} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
                            Trigger Attack
                        </button>
                    </div>
                </div>

                <h2 className="text-lg font-medium mb-2">Live Alerts</h2>
                <ul className="bg-white rounded p-4 shadow space-y-2">
                    {alerts.map((alert, idx) => (
                        <li key={idx} className="text-sm text-red-600">
                            {alert.timestamp} - {alert.sensor} - {alert.attack_type}
                        </li>
                    ))}
                </ul>

                <h2 className="text-lg font-medium mt-6 mb-2">Audit Trail</h2>
                <div className="overflow-auto bg-white p-4 rounded shadow">
                    <table className="min-w-full table-auto">
                        <thead>
                        <tr>
                            <th className="px-4 py-2">Time</th>
                            <th className="px-4 py-2">Sensor</th>
                            <th className="px-4 py-2">Attack</th>
                            <th className="px-4 py-2">Status</th>
                            <th className="px-4 py-2">Target</th>
                        </tr>
                        </thead>
                        <tbody>
                        {auditTrail.map((log, idx) => (
                            <tr key={idx} className="border-t">
                                <td className="px-4 py-2">{log.timestamp}</td>
                                <td className="px-4 py-2">{log.sensor}</td>
                                <td className="px-4 py-2">{log.attack_type}</td>
                                <td className="px-4 py-2">{log.status}</td>
                                <td className="px-4 py-2">{log.target}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </Layout>
    );
};

export default SensorSecurityDashboard;
