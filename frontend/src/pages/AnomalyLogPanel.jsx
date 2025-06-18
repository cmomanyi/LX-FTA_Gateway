import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";

const AnomalyLogPanel = () => {
    const [logs, setLogs] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");

    useEffect(() => {
        fetch("https://api.lx-gateway.tech/log/anomalies")
            .then(res => res.json())
            .then(setLogs)
            .catch(console.error);
    }, []);

    const downloadCSV = () => {
        const headers = ["timestamp", "sensor_type", "sensor_id", "metric", "value"];
        const csvRows = [
            headers.join(","),
            ...logs.map(log =>
                headers.map(h => JSON.stringify(log[h] || "")).join(",")
            ),
        ];
        const blob = new Blob([csvRows.join("\n")], { type: "text/csv" });
        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = url;
        link.download = "anomaly_logs.csv";
        link.click();
    };

    const filtered = logs.filter(log =>
        Object.values(log).some(val =>
            String(val).toLowerCase().includes(searchTerm.toLowerCase())
        )
    );

    return (
        <Layout>
        <div className="p-4 border rounded shadow mt-6 bg-white">
            <h3 className="text-lg font-semibold mb-2">Anomaly Logs</h3>

            <div className="flex gap-2 mb-2">
                <input
                    type="text"
                    placeholder="Search logs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="p-2 border rounded w-full"
                />
                <button onClick={downloadCSV} className="px-3 py-2 bg-blue-500 text-white rounded">
                    Export CSV
                </button>
            </div>

            <div className="overflow-x-auto max-h-64 overflow-y-scroll border rounded">
                <table className="table-auto w-full text-sm">
                    <thead className="bg-gray-100 sticky top-0">
                    <tr>
                        <th className="p-2">Timestamp</th>
                        <th className="p-2">Sensor</th>
                        <th className="p-2">ID</th>
                        <th className="p-2">Metric</th>
                        <th className="p-2">Value</th>
                    </tr>
                    </thead>
                    <tbody>
                    {filtered.map((log, idx) => (
                        <tr key={idx} className="border-t">
                            <td className="p-2">{log.timestamp}</td>
                            <td className="p-2">{log.sensor_type}</td>
                            <td className="p-2">{log.sensor_id}</td>
                            <td className="p-2">{log.metric}</td>
                            <td className="p-2">{log.value}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
        </Layout>
    );
};

export default AnomalyLogPanel;
