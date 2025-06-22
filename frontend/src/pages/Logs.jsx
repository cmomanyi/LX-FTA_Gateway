// Logs.jsx
import React, { useEffect, useState } from "react";

const Logs = () => {
    const [logs, setLogs] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await fetch("https://api.lx-gateway.tech/api/logs");
                const data = await res.json();
                setLogs(data.logs || []);
            } catch (error) {
                console.error("Failed to fetch logs", error);
            }
        };

        fetchLogs();
        const interval = setInterval(fetchLogs, 10000); // Auto-refresh every 10s
        return () => clearInterval(interval);
    }, []);

    const filteredLogs = logs.filter(log =>
        log.sensor_id?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4">📜 Live Audit Trail</h2>

            <input
                type="text"
                placeholder="Search by sensor ID..."
                className="border p-2 mb-4 w-full"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
            />

            <div className="overflow-x-auto">
                <table className="min-w-full text-sm border">
                    <thead className="bg-gray-100">
                    <tr>
                        <th className="px-4 py-2 border">Time</th>
                        <th className="px-4 py-2 border">Sensor ID</th>
                        <th className="px-4 py-2 border">Type</th>
                        <th className="px-4 py-2 border">Message</th>
                        <th className="px-4 py-2 border">Severity</th>
                        <th className="px-4 py-2 border">Status</th>
                    </tr>
                    </thead>
                    <tbody>
                    {filteredLogs.map((log, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                            <td className="px-4 py-2 border">
                                {new Date(log.timestamp).toLocaleString()}
                            </td>
                            <td className="px-4 py-2 border">{log.sensor_id}</td>
                            <td className="px-4 py-2 border">{log.attack_type || "Normal"}</td>
                            <td className="px-4 py-2 border">{log.message || "-"}</td>
                            <td className="px-4 py-2 border text-red-600">{log.severity || "Low"}</td>
                            <td className="px-4 py-2 border">
                                {log.status === "blocked" ? "🔒 Blocked" : "✅ Accepted"}
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Logs;
