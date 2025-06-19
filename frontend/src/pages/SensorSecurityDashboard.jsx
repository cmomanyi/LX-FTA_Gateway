
import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { Line, Doughnut } from "react-chartjs-2";
import {
    Chart as ChartJS,
    LineElement,
    PointElement,
    CategoryScale,
    LinearScale,
    Title,
    Tooltip,
    Legend,
    ArcElement
} from "chart.js";

ChartJS.register(
    LineElement,
    PointElement,
    CategoryScale,
    LinearScale,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

const SensorSecurityDashboard = () => {
    const [auditTrail, setAuditTrail] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [selectedAttack, setSelectedAttack] = useState("spoofing");
    const [severityFilter, setSeverityFilter] = useState("all");

    useEffect(() => {
        const fetchAuditTrail = async () => {
            try {
                const res = await fetch("https://api.lx-gateway.tech/api/logs");
                const data = await res.json();
                setAuditTrail(data.logs || []);
            } catch (err) {
                console.error("Failed to load audit logs", err);
            }
        };

        fetchAuditTrail();
        const interval = setInterval(fetchAuditTrail, 10000);

        const ws = new WebSocket("ws://api.lx-gateway.tech//ws/alerts");

        ws.onmessage = (event) => {
            const alert = JSON.parse(event.data);
            setAlerts((prev) => [alert, ...prev].slice(0, 50));
            setAuditTrail((prev) => [alert, ...prev].slice(0, 200));
        };

        return () => {
            clearInterval(interval);
            ws.close();
        };
    }, []);

    const handleTrigger = async () => {
        try {
            const res = await fetch(`https://api.lx-gateway.tech/trigger/${selectedAttack}`);
            const data = await res.json();
            alert(data.status || "Attack simulated");
        } catch (err) {
            console.error("Failed to trigger attacks", err);
        }
    };

    const chartData = {
        labels: alerts.slice(0, 10).map(a => new Date(a.timestamp).toLocaleTimeString()),
        datasets: [
            {
                label: "Alerts (last 10)",
                data: alerts.slice(0, 10).map((_, idx) => idx + 1),
                fill: false,
                borderColor: "rgb(255, 99, 132)",
                tension: 0.3,
            },
        ],
    };

    const attackTypeCounts = alerts.reduce((acc, cur) => {
        acc[cur.attack_type] = (acc[cur.attack_type] || 0) + 1;
        return acc;
    }, {});

    const donutChartData = {
        labels: Object.keys(attackTypeCounts),
        datasets: [
            {
                data: Object.values(attackTypeCounts),
                backgroundColor: [
                    "#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#6366F1",
                    "#8B5CF6", "#EC4899", "#F97316", "#14B8A6", "#84CC16"
                ],
                borderWidth: 1
            }
        ]
    };

    const filteredAuditTrail = severityFilter === "all"
        ? auditTrail
        : auditTrail.filter(log => log.severity?.toLowerCase() === severityFilter);

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

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div className="bg-white p-4 rounded shadow">
                        <h2 className="text-lg font-semibold mb-2">📈 Live Alert Metrics</h2>
                        <Line data={chartData} />
                    </div>

                    <div className="bg-white p-4 rounded shadow">
                        <h2 className="text-lg font-semibold mb-2">🔎 Attack Type Distribution</h2>
                        <Doughnut data={donutChartData} />
                    </div>
                </div>

                <div className="flex items-center justify-between mb-2">
                    <h2 className="text-lg font-medium">Audit Trail</h2>
                    <select
                        value={severityFilter}
                        onChange={(e) => setSeverityFilter(e.target.value)}
                        className="border px-2 py-1 rounded"
                    >
                        <option value="all">All Severities</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                    </select>
                </div>

                <div className="overflow-auto bg-white p-4 rounded shadow">
                    <table className="min-w-full table-auto text-sm">
                        <thead>
                        <tr>
                            <th className="px-4 py-2">Time</th>
                            <th className="px-4 py-2">Sensor</th>
                            <th className="px-4 py-2">Attack</th>
                            <th className="px-4 py-2">Message</th>
                            <th className="px-4 py-2">Severity</th>
                        </tr>
                        </thead>
                        <tbody>
                        {filteredAuditTrail.map((log, idx) => (
                            <tr
                                key={idx}
                                className={
                                    log.severity === "High"
                                        ? "bg-red-100"
                                        : log.severity === "Medium"
                                            ? "bg-yellow-100"
                                            : log.severity === "Low"
                                                ? "bg-green-100"
                                                : ""
                                }
                            >
                                <td className="px-4 py-2">{new Date(log.timestamp).toLocaleString()}</td>
                                <td className="px-4 py-2">{log.sensor_id || log.sensor}</td>
                                <td className="px-4 py-2">{log.attack_type}</td>
                                <td className="px-4 py-2">{log.message || log.status}</td>
                                <td className="px-4 py-2">{log.severity}</td>
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
