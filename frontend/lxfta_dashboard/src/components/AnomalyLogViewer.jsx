import React, { useEffect, useState } from "react";

const AnomalyLogViewer = () => {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await fetch("http://localhost:8000/api/anomalies", {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem("token")}`,
                    },
                });
                const data = await res.json();
                setLogs(data);
            } catch (err) {
                console.error("Failed to fetch anomaly logs:", err);
            }
        };

        fetchLogs();
        const interval = setInterval(fetchLogs, 10000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="overflow-x-auto">
            <table className="w-full table-auto border text-sm">
                <thead className="bg-gray-100">
                <tr>
                    <th className="p-2">Time</th>
                    <th className="p-2">Sensor</th>
                    <th className="p-2">Attack</th>
                    <th className="p-2">Severity</th>
                </tr>
                </thead>
                <tbody>
                {logs.map((log, idx) => (
                    <tr key={idx} className="border-t">
                        <td className="p-2">{log.time}</td>
                        <td className="p-2">{log.sensor}</td>
                        <td className="p-2">{log.type}</td>
                        <td className={`p-2 font-semibold ${log.severity === "High" ? "text-red-600" : "text-yellow-600"}`}>
                            {log.severity}
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
};

export default AnomalyLogViewer;
