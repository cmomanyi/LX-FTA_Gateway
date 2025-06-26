// // // Logs.jsx
// // import React, { useEffect, useState } from "react";
// //
// // const Logs = () => {
// //     const [logs, setLogs] = useState([]);
// //     const [searchTerm, setSearchTerm] = useState("");
// //
// //     useEffect(() => {
// //         const fetchLogs = async () => {
// //             try {
// //                 const res = await fetch("https://api.lx-gateway.tech/api/logs");
// //                 const data = await res.json();
// //                 setLogs(data.logs || []);
// //             } catch (error) {
// //                 console.error("Failed to fetch logs", error);
// //             }
// //         };
// //
// //         fetchLogs();
// //         const interval = setInterval(fetchLogs, 10000); // Auto-refresh every 10s
// //         return () => clearInterval(interval);
// //     }, []);
// //
// //     const filteredLogs = logs.filter(log =>
// //         log.sensor_id?.toLowerCase().includes(searchTerm.toLowerCase())
// //     );
// //
// //     return (
// //         <div>
// //             <h2 className="text-2xl font-bold mb-4">📜 Live Audit Trail</h2>
// //
// //             <input
// //                 type="text"
// //                 placeholder="Search by sensor ID..."
// //                 className="border p-2 mb-4 w-full"
// //                 value={searchTerm}
// //                 onChange={e => setSearchTerm(e.target.value)}
// //             />
// //
// //             <div className="overflow-x-auto">
// //                 <table className="min-w-full text-sm border">
// //                     <thead className="bg-gray-100">
// //                     <tr>
// //                         <th className="px-4 py-2 border">Time</th>
// //                         <th className="px-4 py-2 border">Sensor ID</th>
// //                         <th className="px-4 py-2 border">Type</th>
// //                         <th className="px-4 py-2 border">Message</th>
// //                         <th className="px-4 py-2 border">Severity</th>
// //                         <th className="px-4 py-2 border">Status</th>
// //                     </tr>
// //                     </thead>
// //                     <tbody>
// //                     {filteredLogs.map((log, index) => (
// //                         <tr key={index} className="hover:bg-gray-50">
// //                             <td className="px-4 py-2 border">
// //                                 {new Date(log.timestamp).toLocaleString()}
// //                             </td>
// //                             <td className="px-4 py-2 border">{log.sensor_id}</td>
// //                             <td className="px-4 py-2 border">{log.attack_type || "Normal"}</td>
// //                             <td className="px-4 py-2 border">{log.message || "-"}</td>
// //                             <td className="px-4 py-2 border text-red-600">{log.severity || "Low"}</td>
// //                             {/*<td className="px-4 py-2 border">*/}
// //                             {/*    {log.status === "blocked" ? "🔒 Blocked" : "✅ Accepted"}*/}
// //                             {/*</td>*/}
// //                             <td className={`py-2 px-4 border-b font-semibold ${log.severity === 'High' ? 'text-red-600' : 'text-green-600'}`}>
// //                                 {log.severity === 'High' ? '🚫 Blocked' : '✅ Allowed'}
// //                             </td>
// //                         </tr>
// //                     ))}
// //                     </tbody>
// //                 </table>
// //             </div>
// //         </div>
// //     );
// // };
// //
// // export default Logs;
//
// import React, { useEffect, useState } from "react";
//
// const Logs = () => {
//     const [logs, setLogs] = useState([]);
//     const [searchTerm, setSearchTerm] = useState("");
//     const [searchDate, setSearchDate] = useState("");
//
//     useEffect(() => {
//         const fetchLogs = async () => {
//             try {
//                 const res = await fetch("https://api.lx-gateway.tech/api/logs");
//                 const data = await res.json();
//                 setLogs(data.logs || []);
//             } catch (error) {
//                 console.error("Failed to fetch logs", error);
//             }
//         };
//
//         fetchLogs();
//         const interval = setInterval(fetchLogs, 10000); // Auto-refresh every 10s
//         return () => clearInterval(interval);
//     }, []);
//
//     const matchesSearch = (log) => {
//         const dateMatch = searchDate
//             ? new Date(log.timestamp).toISOString().startsWith(searchDate)
//             : true;
//         const idMatch = log.sensor_id?.toLowerCase().includes(searchTerm.toLowerCase());
//         return idMatch && dateMatch;
//     };
//
//     const filteredLogs = logs.filter(matchesSearch);
//
//     const exportToCSV = () => {
//         const headers = ["Time", "Sensor ID", "Type", "Message", "Severity", "Status"];
//         const rows = filteredLogs.map(log => [
//             new Date(log.timestamp).toLocaleString(),
//             log.sensor_id,
//             log.attack_type || "Normal",
//             log.message || "-",
//             log.severity || "Low",
//             log.severity === "High" ? "Blocked" : "Allowed"
//         ]);
//
//         const csvContent = [headers, ...rows]
//             .map(row => row.map(value => `"${value}"`).join(","))
//             .join("\n");
//
//         const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
//         const url = URL.createObjectURL(blob);
//         const link = document.createElement("a");
//         link.href = url;
//         link.download = "sensor_logs.csv";
//         link.click();
//     };
//
//     return (
//         <div>
//             <h2 className="text-2xl font-bold mb-4">📜 Live Audit Trail</h2>
//
//             <div className="flex flex-col md:flex-row gap-4 mb-4">
//                 <input
//                     type="text"
//                     placeholder="Search by sensor ID..."
//                     className="border p-2 w-full md:w-1/3"
//                     value={searchTerm}
//                     onChange={e => setSearchTerm(e.target.value)}
//                 />
//                 <input
//                     type="date"
//                     className="border p-2 w-full md:w-1/4"
//                     value={searchDate}
//                     onChange={e => setSearchDate(e.target.value)}
//                 />
//                 <button
//                     onClick={exportToCSV}
//                     className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
//                 >
//                     ⬇️ Export CSV
//                 </button>
//             </div>
//
//             <div className="overflow-x-auto">
//                 <table className="min-w-full text-sm border">
//                     <thead className="bg-gray-100">
//                     <tr>
//                         <th className="px-4 py-2 border">Time</th>
//                         <th className="px-4 py-2 border">Sensor ID</th>
//                         <th className="px-4 py-2 border">Type</th>
//                         <th className="px-4 py-2 border">Message</th>
//                         <th className="px-4 py-2 border">Severity</th>
//                         <th className="px-4 py-2 border">Status</th>
//                     </tr>
//                     </thead>
//                     <tbody>
//                     {filteredLogs.map((log, index) => (
//                         <tr key={index} className="hover:bg-gray-50">
//                             <td className="px-4 py-2 border">
//                                 {new Date(log.timestamp).toLocaleString()}
//                             </td>
//                             <td className="px-4 py-2 border">{log.sensor_id}</td>
//                             <td className="px-4 py-2 border">{log.attack_type || "Normal"}</td>
//                             <td className="px-4 py-2 border">{log.message || "-"}</td>
//                             <td className="px-4 py-2 border text-red-600">{log.severity || "Low"}</td>
//                             <td className={`py-2 px-4 border font-semibold ${log.severity === 'High' ? 'text-red-600' : 'text-green-600'}`}>
//                                 {log.severity === 'High' ? '🚫 Blocked' : '✅ Allowed'}
//                             </td>
//                         </tr>
//                     ))}
//                     </tbody>
//                 </table>
//             </div>
//         </div>
//     );
// };
//
// // export default Logs;
// import React, { useEffect, useState } from "react";
// import { saveAs } from "file-saver";
//
// const Logs = () => {
//     const [logs, setLogs] = useState([]);
//     const [searchTerm, setSearchTerm] = useState("");
//     const [searchDate, setSearchDate] = useState("");
//     const [searchType, setSearchType] = useState("");
//     const [isCollapsed, setIsCollapsed] = useState(false);
//
//     useEffect(() => {
//         const fetchLogs = async () => {
//             try {
//                 const res = await fetch("https://api.lx-gateway.tech/api/logs");
//                 const data = await res.json();
//                 setLogs(data.logs || []);
//             } catch (error) {
//                 console.error("Failed to fetch logs", error);
//             }
//         };
//
//         fetchLogs();
//         const interval = setInterval(fetchLogs, 10000);
//         return () => clearInterval(interval);
//     }, []);
//
//     const filteredLogs = logs.filter(log => {
//         const matchesID = log.sensor_id?.toLowerCase().includes(searchTerm.toLowerCase());
//         const matchesType = log.attack_type?.toLowerCase().includes(searchType.toLowerCase());
//         const matchesDate = searchDate ? new Date(log.timestamp).toLocaleDateString() === searchDate : true;
//         return matchesID && matchesType && matchesDate;
//     });
//
//     const exportCSV = () => {
//         const header = ["Time", "Sensor ID", "Type", "Message", "Severity", "Status"];
//         const rows = filteredLogs.map(log => [
//             new Date(log.timestamp).toLocaleString(),
//             log.sensor_id,
//             log.attack_type || "Normal",
//             log.message || "-",
//             log.severity || "Low",
//             log.severity === "High" ? "🚫 Blocked" : "✅ Allowed"
//         ]);
//
//         const csvContent = [header, ...rows].map(r => r.join(",")).join("\n");
//         const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8" });
//         saveAs(blob, "sensor_logs.csv");
//     };
//
//     return (
//         <div className="dark bg-gray-900 text-white p-4 min-h-screen">
//             <div className="flex justify-between items-center mb-4">
//                 <h2 className="text-2xl font-bold">📜 Live Audit Trail</h2>
//                 <button onClick={exportCSV} className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-white">⬇️ Export CSV</button>
//             </div>
//
//             <div className="grid grid-cols-3 gap-2 mb-4">
//                 <input
//                     type="text"
//                     placeholder="Search by sensor ID..."
//                     className="p-2 border border-gray-600 bg-gray-800 rounded"
//                     value={searchTerm}
//                     onChange={e => setSearchTerm(e.target.value)}
//                 />
//                 <input
//                     type="date"
//                     className="p-2 border border-gray-600 bg-gray-800 rounded"
//                     onChange={e => setSearchDate(e.target.value)}
//                 />
//                 <input
//                     type="text"
//                     placeholder="Filter by type (e.g. spoofing)"
//                     className="p-2 border border-gray-600 bg-gray-800 rounded"
//                     value={searchType}
//                     onChange={e => setSearchType(e.target.value)}
//                 />
//             </div>
//
//             <button
//                 onClick={() => setIsCollapsed(!isCollapsed)}
//                 className="mb-4 text-sm underline text-blue-400"
//             >
//                 {isCollapsed ? "▶️ Show Logs" : "🔽 Collapse Logs"}
//             </button>
//
//             {!isCollapsed && (
//                 <div className="overflow-x-auto">
//                     <table className="min-w-full text-sm border border-gray-700">
//                         <thead className="bg-gray-800">
//                         <tr>
//                             <th className="px-4 py-2 border border-gray-700">Time</th>
//                             <th className="px-4 py-2 border border-gray-700">Sensor ID</th>
//                             <th className="px-4 py-2 border border-gray-700">Type</th>
//                             <th className="px-4 py-2 border border-gray-700">Message</th>
//                             <th className="px-4 py-2 border border-gray-700">Severity</th>
//                             <th className="px-4 py-2 border border-gray-700">Status</th>
//                         </tr>
//                         </thead>
//                         <tbody>
//                         {filteredLogs.map((log, index) => (
//                             <tr key={index} className="hover:bg-gray-800">
//                                 <td className="px-4 py-2 border border-gray-700">{new Date(log.timestamp).toLocaleString()}</td>
//                                 <td className="px-4 py-2 border border-gray-700">{log.sensor_id}</td>
//                                 <td className="px-4 py-2 border border-gray-700">{log.attack_type || "Normal"}</td>
//                                 <td className="px-4 py-2 border border-gray-700">{log.message || "-"}</td>
//                                 <td className="px-4 py-2 border border-gray-700 text-red-400">{log.severity || "Low"}</td>
//                                 <td className={`px-4 py-2 border border-gray-700 font-semibold ${log.severity === 'High' ? 'text-red-500' : 'text-green-400'}`}>
//                                     {log.severity === 'High' ? '🚫 Blocked' : '✅ Allowed'}
//                                 </td>
//                             </tr>
//                         ))}
//                         </tbody>
//                     </table>
//                 </div>
//             )}
//         </div>
//     );
// };
//
// export default Logs;

import React, { useEffect, useState } from "react";
import { saveAs } from "file-saver";

const Logs = () => {
    const [logs, setLogs] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [searchDate, setSearchDate] = useState("");
    const [searchType, setSearchType] = useState("");
    const [isCollapsed, setIsCollapsed] = useState(false);

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
        const interval = setInterval(fetchLogs, 10000);
        return () => clearInterval(interval);
    }, []);

    const filteredLogs = logs.filter(log => {
        const matchesID = log.sensor_id?.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = log.attack_type?.toLowerCase().includes(searchType.toLowerCase());
        const matchesDate = searchDate ? new Date(log.timestamp).toLocaleDateString() === searchDate : true;
        return matchesID && matchesType && matchesDate;
    });

    const exportCSV = () => {
        const header = ["Time", "Sensor ID", "Type", "Message", "Severity", "Status"];
        const rows = filteredLogs.map(log => [
            new Date(log.timestamp).toLocaleString(),
            log.sensor_id,
            log.attack_type || "Normal",
            log.message || "-",
            log.severity || "Low",
            log.severity === "High" ? "🚫 Blocked" : "✅ Allowed"
        ]);

        const csvContent = [header, ...rows].map(r => r.join(",")).join("\n");
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8" });
        saveAs(blob, "sensor_logs.csv");
    };

    return (
        <div className="dark bg-gray-900 text-white p-4 min-h-screen">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">📜 Live Audit Trail</h2>
                <button onClick={exportCSV} className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-white">⬇️ Export CSV</button>
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
                    <table className="min-w-full text-sm border border-gray-700">
                        <thead className="bg-gray-800">
                        <tr>
                            <th className="px-4 py-2 border border-gray-700">Time</th>
                            <th className="px-4 py-2 border border-gray-700">Sensor ID</th>
                            <th className="px-4 py-2 border border-gray-700">Type</th>
                            <th className="px-4 py-2 border border-gray-700">Message</th>
                            <th className="px-4 py-2 border border-gray-700">Severity</th>
                            <th className="px-4 py-2 border border-gray-700">Status</th>
                        </tr>
                        </thead>
                        <tbody>
                        {filteredLogs.map((log, index) => (
                            <tr key={index} className="hover:bg-gray-800">
                                <td className="px-4 py-2 border border-gray-700">{new Date(log.timestamp).toLocaleString()}</td>
                                <td className="px-4 py-2 border border-gray-700">{log.sensor_id}</td>
                                <td className="px-4 py-2 border border-gray-700">{log.attack_type || "Normal"}</td>
                                <td className="px-4 py-2 border border-gray-700">{log.message || "-"}</td>
                                <td className="px-4 py-2 border border-gray-700 text-red-400">{log.severity || "Low"}</td>
                                <td className={`px-4 py-2 border border-gray-700 font-semibold ${log.severity === 'High' ? 'text-red-500' : 'text-green-400'}`}>
                                    {log.severity === 'High' ? '🚫 Blocked' : '✅ Allowed'}
                                </td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default Logs;
