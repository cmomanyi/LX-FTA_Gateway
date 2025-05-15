import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { saveAs } from "file-saver";
import { Line, Bar } from "react-chartjs-2";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import {
    Chart as ChartJS,
    LineElement,
    BarElement,
    CategoryScale,
    LinearScale,
    PointElement,
    Tooltip,
    Legend,
} from "chart.js";

ChartJS.register(LineElement, BarElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

const SENSOR_TYPES = ["soil", "water", "plant", "threat", "atmospheric"];
const STATUS_SECURE = "secure";
const STATUS_BLOCKED = "blocked";

const SensorSecurityDashboard = () => {
    const [sensorStatuses, setSensorStatuses] = useState(() =>
        SENSOR_TYPES.reduce((acc, type) => ({ ...acc, [type]: STATUS_SECURE }), {})
    );
    const [alerts, setAlerts] = useState([]);
    const [auditTrail, setAuditTrail] = useState([]);
    const [search, setSearch] = useState("");
    const [selectedType, setSelectedType] = useState("");
    const [selectedNumber, setSelectedNumber] = useState("");
    const [modalData, setModalData] = useState(null);
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);
    const [shapExplanation, setShapExplanation] = useState(null);
    const [showOnlyBlocked, setShowOnlyBlocked] = useState(false);

    useEffect(() => {
        const fetchLatestAudit = async () => {
            try {
                const res = await fetch("http://localhost:8000/api/audit", {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("token")}`,
                    },
                });
                const data = await res.json();
                if (Array.isArray(data)) {
                    setAuditTrail(data);
                } else if (Array.isArray(data?.audit_logs)) {
                    setAuditTrail(data.audit_logs);
                } else {
                    console.error("Unexpected audit format:", data);
                    setAuditTrail([]);
                }
            } catch (err) {
                console.error("Failed to fetch audit trail", err);
                setAuditTrail([]);
            }
        };

        const interval = setInterval(fetchLatestAudit, 10000);
        fetchLatestAudit();

        const token = localStorage.getItem("token");
        const ws = new WebSocket(`ws://localhost:8000/ws/alerts?token=${token}`);

        ws.onmessage = (event) => {
            const alert = JSON.parse(event.data);
            alert.status = STATUS_BLOCKED;
            alert.highlight = true;
            setAlerts((prev) => [alert, ...prev].slice(0, 20));
            setAuditTrail((prev) => [alert, ...prev].slice(0, 100));

            const sensorType = alert.sensor.split("-")[0];
            setSensorStatuses((prev) => ({ ...prev, [sensorType]: STATUS_BLOCKED }));

            setTimeout(() => {
                setSensorStatuses((prev) => ({ ...prev, [sensorType]: STATUS_SECURE }));
            }, 10000);
        };

        ws.onerror = (err) => console.error("WebSocket error:", err);
        ws.onclose = () => console.warn("WebSocket connection closed");

        return () => {
            clearInterval(interval);
            ws.close();
        };
    }, []);

    const filteredAuditTrail = Array.isArray(auditTrail) ? auditTrail.filter((log) => {
        const matchesTypeAndNumber = !selectedType || (!selectedNumber
            ? log.sensor?.startsWith(`${selectedType}-`)
            : log.sensor?.startsWith(`${selectedType}-`) && log.sensor?.includes(selectedNumber));
        const matchesSearch =
            log.sensor?.toLowerCase().includes(search.toLowerCase()) ||
            log.type?.toLowerCase().includes(search.toLowerCase());
        const matchesDate = (!startDate || new Date(log.time) >= startDate) && (!endDate || new Date(log.time) <= endDate);
        const matchesStatus = !showOnlyBlocked || log.status === STATUS_BLOCKED;
        return matchesTypeAndNumber && matchesSearch && matchesDate && matchesStatus;
    }).slice(0, 100) : [];

    const filteredAlerts = selectedType
        ? auditTrail.filter(
            (alert) => alert.sensor?.startsWith(`${selectedType}-`) && (!selectedNumber || alert.sensor?.includes(selectedNumber))
        )
        : auditTrail;

    const downloadCSV = () => {
        const headers = "Time,Sensor,Attack,Status\n";
        const rows = filteredAuditTrail
            .map((log) => `${log.time},${log.sensor},${log.type},${log.status}`)
            .join("\n");
        const blob = new Blob([headers + rows], { type: "text/csv;charset=utf-8" });
        saveAs(blob, "filtered_audit_trail.csv");
    };

    const chartData = {
        labels: filteredAlerts.slice(0, 10).map((a) => a.time).reverse(),
        datasets: [
            {
                label: "Live Severity",
                data: filteredAlerts.slice(0, 10).map((a) =>
                    a.severity === "High" ? 3 : a.severity === "Medium" ? 2 : 1
                ).reverse(),
                fill: false,
                borderColor: "#f87171",
                tension: 0.1,
            },
        ],
    };

    const blockedCountsByType = SENSOR_TYPES.map(type => {
        const count = Array.isArray(auditTrail) ? auditTrail.filter(
            (log) => log.status === STATUS_BLOCKED && log.sensor?.startsWith(type + "-")
        ).length : 0;
        return { type, count };
    });

    const barChartData = {
        labels: blockedCountsByType.map(item => item.type),
        datasets: [
            {
                label: "Blocked Events",
                data: blockedCountsByType.map(item => item.count),
                backgroundColor: "rgba(239, 68, 68, 0.6)",
                borderColor: "rgba(239, 68, 68, 1)",
                borderWidth: 1,
            },
        ],
    };

    const fetchSHAPExplanation = async (alert) => {
        try {
            const response = await fetch("http://localhost:8001/explain", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    sensor_id: alert.sensor,
                    temperature: alert.temperature || 87.0,
                    moisture: alert.moisture || 25.0,
                    ph: alert.ph || 5.2,
                    battery_level: alert.battery_level || 3.0,
                    frequency: alert.frequency || 12.0,
                }),
            });
            const data = await response.json();
            setShapExplanation(data);
        } catch (err) {
            console.error("SHAP error", err);
        }
    };

    return (
        <Layout>
            <div className="p-6 space-y-6 bg-gray-100 min-h-screen">
                <div className="flex flex-wrap items-center gap-4">
                    <select
                        className="border p-2 rounded"
                        value={selectedType}
                        onChange={(e) => setSelectedType(e.target.value)}
                    >
                        <option value="">All Types</option>
                        {SENSOR_TYPES.map((type) => (
                            <option key={type} value={type}>{type}</option>
                        ))}
                    </select>
                    <select
                        className="border p-2 rounded"
                        value={selectedNumber}
                        onChange={(e) => setSelectedNumber(e.target.value)}
                    >
                        <option value="">All IDs</option>
                        {["001", "002", "003", "004", "005"].map((num) => (
                            <option key={num} value={num}>{num}</option>
                        ))}
                    </select>
                    <input className="p-2 border rounded" type="text" placeholder="Search sensor or type" value={search}
                           onChange={(e) => setSearch(e.target.value)}/>
                    <DatePicker className="p-2 border rounded" selected={startDate}
                                onChange={(date) => setStartDate(date)} placeholderText="Start Date"/>
                    <DatePicker className="p-2 border rounded" selected={endDate} onChange={(date) => setEndDate(date)}
                                placeholderText="End Date"/>
                    <label className="flex items-center gap-2">
                        <input type="checkbox" checked={showOnlyBlocked}
                               onChange={() => setShowOnlyBlocked(!showOnlyBlocked)}/>
                        Show only blocked
                    </label>
                    <button onClick={downloadCSV}
                            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Download CSV
                    </button>
                </div>
                <div className="flex flex-col lg:flex-row gap-6">
                    <div className="bg-white p-4 shadow rounded-xl w-full lg:w-1/2">
                        <h3 className="text-lg font-semibold mb-2">📈 Live Severity</h3>
                        <Line data={chartData}/>
                    </div>
                    <div className="bg-white p-4 shadow rounded-xl w-full lg:w-1/2">
                        <h3 className="text-lg font-semibold mb-2">📊 Blocked Events Per Sensor Type</h3>
                        <Bar data={barChartData} options={{responsive: true, plugins: {legend: {display: false}}}}/>
                    </div>
                </div>

                <div className="p-4 bg-white shadow rounded-xl max-h-64 overflow-y-auto">
                    <h3 className="text-lg font-semibold mb-2">Live Alerts</h3>
                    <ul className="space-y-2 text-sm">
                        {filteredAlerts.map((alert, idx) => (
                            <li
                                key={idx}
                                className="flex justify-between cursor-pointer hover:bg-gray-100 p-1"
                                onClick={() => {
                                    setModalData(alert);
                                    fetchSHAPExplanation();
                                }}
                            >
                                <span>{alert.time} - {alert.sensor} - {alert.type}</span>
                                <span className="font-bold text-red-500">{alert.severity}</span>
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="bg-white p-4 shadow rounded-xl">
                    <h3 className="text-lg font-semibold mb-2">Audit Trail</h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm table-auto border-collapse">
                            <thead>
                            <tr className="text-left border-b">
                                <th className="p-2">Time</th>
                                <th className="p-2">Sensor</th>
                                <th className="p-2">Attack</th>
                                <th className="p-2">Status</th>
                            </tr>
                            </thead>
                            <tbody>
                            {filteredAuditTrail.map((log, idx) => (
                                <tr key={idx} className="border-b">
                                    <td className="p-2">{log.time}</td>
                                    <td className="p-2">{log.sensor}</td>
                                    <td className="p-2">{log.type}</td>
                                    <td className={`p-2 font-semibold ${log.status === STATUS_BLOCKED ? "text-red-600" : "text-green-600"}`}>
                                        {log.status}
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {modalData && (
                    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
                        <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-xl">
                            <h3 className="text-lg font-bold mb-4">🔍 Alert Metadata</h3>
                            <pre className="text-xs bg-gray-100 p-3 rounded overflow-x-auto">
                {JSON.stringify(modalData, null, 2)}
              </pre>
                            {shapExplanation && (
                                <div className="mt-4">
                                    <h4 className="font-semibold">🧠 SHAP Explanation</h4>
                                    <ul className="text-xs mt-2 space-y-1">
                                        {shapExplanation.features.map((f, i) => (
                                            <li key={i}>{f.feature}: <strong>{f.contribution}</strong></li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                            <div className="text-right mt-4">
                                <button onClick={() => setModalData(null)}
                                        className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">Close
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
</Layout>
)
    ;
};

export default SensorSecurityDashboard;
