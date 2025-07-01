import React, { useEffect, useState } from "react";
import { saveAs } from "file-saver";

const isLogBlocked = (log) => {
    return (
        log.blocked === true ||
        (typeof log.severity === "string" && log.severity.toLowerCase().includes("high")) ||
        (typeof log.message === "string" && log.message.toLowerCase().includes("blocked"))
    );
};

const Logs = () => {
    const [logs, setLogs] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [searchDate, setSearchDate] = useState("");
    const [searchType, setSearchType] = useState("");
    const [isCollapsed, setIsCollapsed] = useState(false);
    const [loading, setLoading] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const logsPerPage = 10;

    const fetchLogs = async () => {
        try {
            setLoading(true);
            const res = await fetch("https://api.lx-gateway.tech/api/logs");
            const data = await res.json();
            setLogs(data.logs || []);
        } catch (error) {
            console.error("Failed to fetch logs", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 10000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        setCurrentPage(1);
    }, [searchTerm, searchDate, searchType]);

    const handleResetLogs = async () => {
        const confirmed = window.confirm("Are you sure you want to delete all logs?");
        if (!confirmed) return;

        try {
            const res = await fetch("https://api.lx-gateway.tech/api/logs", {
                method: "DELETE"
            });

            if (res.ok) {
                alert("✅ All logs have been deleted.");
                await fetchLogs();
            } else {
                alert("❌ Failed to delete logs.");
            }
        } catch (error) {
            console.error("Error deleting logs:", error);
            alert("❌ Error deleting logs.");
        }
    };

    const filteredLogs = logs.filter(log => {
        const matchesID = log.sensor_id?.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = log.attack_type?.toLowerCase().includes(searchType.toLowerCase());
        const matchesDate = searchDate ? new Date(log.timestamp).toLocaleDateString() === searchDate : true;
        return matchesID && matchesType && matchesDate;
    });

    const indexOfLastLog = currentPage * logsPerPage;
    const indexOfFirstLog = indexOfLastLog - logsPerPage;
    const currentLogs = filteredLogs.slice(indexOfFirstLog, indexOfLastLog);
    const totalPages = Math.ceil(filteredLogs.length / logsPerPage);

    const exportCSV = () => {
        const header = ["#", "Time", "Sensor ID", "Type", "Message", "Severity", "Status"];
        const rows = filteredLogs.map((log, index) => [
            index + 1,
            new Date(log.timestamp).toLocaleString(),
            log.sensor_id,
            log.attack_type || "Normal",
            log.message || "-",
            log.severity || "Low",
            isLogBlocked(log) ? "🚫 Blocked" : "✅ Allowed"
        ]);

        const csvContent = [header, ...rows].map(r => r.join(",")).join("\n");
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8" });
        saveAs(blob, "sensor_logs.csv");
    };

    return (
        <div className="dark bg-gray-900 text-white p-4 min-h-screen">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">📜 Live Audit Trail</h2>
                <div className="space-x-2">
                    <button onClick={exportCSV} className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded">
                        ⬇️ Export CSV
                    </button>
                    <button onClick={handleResetLogs} className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded">
                        🗑️ Reset Logs
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-2 mb-4">
                <input
                    type="text"
                    placeholder="Search by sensor ID..."
                    className="p-2 border border-gray-600 bg-gray-800 rounded"
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                />
                <input
                    type="date"
                    className="p-2 border border-gray-600 bg-gray-800 rounded"
                    onChange={e => setSearchDate(e.target.value)}
                />
                <input
                    type="text"
                    placeholder="Filter by type (e.g. spoofing)"
                    className="p-2 border border-gray-600 bg-gray-800 rounded"
                    value={searchType}
                    onChange={e => setSearchType(e.target.value)}
                />
            </div>

            <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="mb-4 text-sm underline text-blue-400"
            >
                {isCollapsed ? "▶️ Show Logs" : "🔽 Collapse Logs"}
            </button>

            {!isCollapsed && (
                <div className="overflow-x-auto">
                    {loading ? (
                        <p className="text-gray-400">Loading logs...</p>
                    ) : (
                        <>
                            <table className="min-w-full text-sm border border-gray-700">
                                <thead className="bg-gray-800">
                                <tr>
                                    <th className="px-4 py-2 border border-gray-700">#</th>
                                    <th className="px-4 py-2 border border-gray-700">Time</th>
                                    <th className="px-4 py-2 border border-gray-700">Sensor ID</th>
                                    <th className="px-4 py-2 border border-gray-700">Type</th>
                                    <th className="px-4 py-2 border border-gray-700">Message</th>
                                    <th className="px-4 py-2 border border-gray-700">Severity</th>
                                    <th className="px-4 py-2 border border-gray-700">Status</th>
                                </tr>
                                </thead>
                                <tbody>
                                {currentLogs.map((log, index) => {
                                    const rowNumber = indexOfFirstLog + index + 1;
                                    return (
                                        <tr key={index} className="hover:bg-gray-800">
                                            <td className="px-4 py-2 border border-gray-700 text-gray-400 font-semibold">{rowNumber}</td>
                                            <td className="px-4 py-2 border border-gray-700">{new Date(log.timestamp).toLocaleString()}</td>
                                            <td className="px-4 py-2 border border-gray-700">{log.sensor_id}</td>
                                            <td className="px-4 py-2 border border-gray-700">{log.attack_type || "Normal"}</td>
                                            <td className="px-4 py-2 border border-gray-700">{log.message || "-"}</td>
                                            <td className="px-4 py-2 border border-gray-700 text-red-400">{log.severity || "Low"}</td>
                                            <td className={`px-4 py-2 border border-gray-700 font-semibold ${isLogBlocked(log) ? 'text-red-500' : 'text-green-400'}`}>
                                                {isLogBlocked(log) ? '🚫 Blocked' : '✅ Allowed'}
                                            </td>
                                        </tr>
                                    );
                                })}
                                </tbody>
                            </table>

                            {totalPages > 1 && (
                                <div className="flex justify-center space-x-2 mt-4">
                                    <button
                                        onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                                        disabled={currentPage === 1}
                                        className="px-3 py-1 bg-gray-700 text-white rounded disabled:opacity-50"
                                    >
                                        ◀ Prev
                                    </button>
                                    <span className="text-sm text-gray-300 pt-1">Page {currentPage} of {totalPages}</span>
                                    <button
                                        onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                                        disabled={currentPage === totalPages}
                                        className="px-3 py-1 bg-gray-700 text-white rounded disabled:opacity-50"
                                    >
                                        Next ▶
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

export default Logs;
