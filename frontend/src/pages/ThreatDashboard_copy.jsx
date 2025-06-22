// import React, { useEffect, useState } from "react";
// import Layout from "../components/Layout";
// import Sidebar from "../components/Sidebar";
// import { saveAs } from "file-saver";
// import { Bar, Line } from "react-chartjs-2";
// import DatePicker from "react-datepicker";
// import "react-datepicker/dist/react-datepicker.css";
// import {
//     Chart as ChartJS,
//     CategoryScale,
//     LinearScale,
//     BarElement,
//     LineElement,
//     PointElement,
//     Title,
//     Tooltip,
//     Legend
// } from "chart.js";
//
// ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);
//
// const ATTACK_TYPES = {
//     spoofing: {
//         endpoint: "/api/validate",
//         payload: (sensorId, valid = true) => ({
//             sensor_id: sensorId,
//             payload: "testPayload",
//             ecc_signature: valid
//                 ? window.btoa(sensorId + "testPayload")
//                 : "invalid_signature"
//         })
//     },
//     replay: {
//         endpoint: "/api/replay-protect",
//         payload: (sensorId) => ({
//             sensor_id: sensorId,
//             timestamp: new Date().toISOString(),
//             nonce: `${sensorId}-${Date.now()}`
//         })
//     },
//     firmware: {
//         endpoint: "/api/detect/firmware_injection",
//         payload: (sensorId) => ({
//             sensor_id: sensorId,
//             firmware_version: "1.0.3",
//             firmware_signature: "invalid_signature"
//         })
//     },
//     ddos: {
//         endpoint: "/sensor/threat/ddos",
//         payload: (sensorId) => ({ sensor_id: sensorId, threshold: 10 })
//     },
//     ml: {
//         endpoint: "/api/drift-detect",
//         payload: (sensorId) => ({ sensor_id: sensorId, values: Array(10).fill(Math.random() * 100) })
//     }
// };
//
// const ThreatDashboard = () => {
//     const [sensorTypes, setSensorTypes] = useState([]);
//     const [sensorIds, setSensorIds] = useState([]);
//     const [selectedType, setSelectedType] = useState("threat");
//     const [selectedSensorId, setSelectedSensorId] = useState("");
//     const [selectedAttack, setSelectedAttack] = useState("spoofing");
//     const [response, setResponse] = useState(null);
//     const [samplePayload, setSamplePayload] = useState("");
//     const [activeTab, setActiveTab] = useState("dashboard");
//     const [anomalies, setAnomalies] = useState([]);
//     const [wsStatus, setWsStatus] = useState("Disconnected");
//     const [startDate, setStartDate] = useState(null);
//     const [endDate, setEndDate] = useState(null);
//     const [severityFilter, setSeverityFilter] = useState("");
//     const [searchQuery, setSearchQuery] = useState("");
//
//     useEffect(() => {
//         fetch("https://api.lx-gateway.tech/api/sensor-types")
//             .then(res => res.json())
//             .then(data => {
//                 setSensorTypes(data.sensor_types);
//                 filterSensorIds(data.sensor_ids, selectedType);
//             });
//     }, []);
//
//     useEffect(() => {
//         fetch("https://api.lx-gateway.tech/api/sensor-types")
//             .then(res => res.json())
//             .then(data => {
//                 filterSensorIds(data.sensor_ids, selectedType);
//             });
//     }, [selectedType]);
//
//     useEffect(() => {
//         const ws = new WebSocket("wss://api.lx-gateway.tech/ws/alerts");
//         ws.onopen = () => setWsStatus("Connected");
//         ws.onclose = () => setWsStatus("Disconnected");
//         ws.onerror = () => setWsStatus("Error");
//         ws.onmessage = (event) => {
//             const newAlert = JSON.parse(event.data);
//             setAnomalies((prev) => [newAlert, ...prev]);
//         };
//         return () => ws.close();
//     }, []);
//
//     useEffect(() => {
//         const config = ATTACK_TYPES[selectedAttack];
//         if (config && selectedSensorId) {
//             const body = config.payload(selectedSensorId);
//             setSamplePayload(JSON.stringify(body, null, 2));
//         }
//     }, [selectedAttack, selectedSensorId]);
//
//     const filterSensorIds = (allIds, type) => {
//         const filtered = allIds.filter(id => id.startsWith(type));
//         setSensorIds(filtered);
//         setSelectedSensorId(filtered[0] || "");
//     };
//
//     const simulateAttack = async () => {
//         try {
//             const body = JSON.parse(samplePayload);
//             const res = await fetch(`https://api.lx-gateway.tech${ATTACK_TYPES[selectedAttack].endpoint}`, {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify(body)
//             });
//             const data = await res.json();
//             setResponse(data);
//             setAnomalies((prev) => [data, ...prev]);
//         } catch (err) {
//             console.error("Attack simulation failed", err);
//             alert("Failed to simulate attack");
//         }
//     };
//
//     const resetPayload = () => {
//         const config = ATTACK_TYPES[selectedAttack];
//         if (config && selectedSensorId) {
//             const defaultPayload = config.payload(selectedSensorId);
//             setSamplePayload(JSON.stringify(defaultPayload, null, 2));
//         }
//     };
//
//     const exportLogs = () => {
//         const blob = new Blob([JSON.stringify(anomalies, null, 2)], {
//             type: "application/json",
//         });
//         saveAs(blob, "anomaly_logs.json");
//     };
//
//     const filteredAnomalies = anomalies.filter((log) => {
//         const logDate = new Date(log.timestamp);
//         const severityMatch = severityFilter ? log.severity === severityFilter : true;
//         const startMatch = startDate ? logDate >= startDate : true;
//         const endMatch = endDate ? logDate <= endDate : true;
//         const searchMatch = searchQuery
//             ? Object.values(log).some((value) =>
//                 typeof value === "string" && value.toLowerCase().includes(searchQuery.toLowerCase())
//             )
//             : true;
//         return severityMatch && startMatch && endMatch && searchMatch;
//     });
//
//     const getAnalyticsData = () => {
//         const counts = filteredAnomalies.reduce((acc, log) => {
//             const type = log.attack_type || "Normal";
//             acc[type] = (acc[type] || 0) + 1;
//             return acc;
//         }, {});
//         return {
//             labels: Object.keys(counts),
//             datasets: [
//                 {
//                     label: "Attack Frequency",
//                     data: Object.values(counts),
//                     backgroundColor: "#dc2626"
//                 }
//             ]
//         };
//     };
//
//     const getLineChartData = () => {
//         const dataMap = {};
//         filteredAnomalies.forEach((log) => {
//             const date = new Date(log.timestamp).toLocaleDateString();
//             dataMap[date] = (dataMap[date] || 0) + 1;
//         });
//         return {
//             labels: Object.keys(dataMap),
//             datasets: [
//                 {
//                     label: "Alerts Over Time",
//                     data: Object.values(dataMap),
//                     borderColor: "#2563eb",
//                     backgroundColor: "rgba(37, 99, 235, 0.3)"
//                 }
//             ]
//         };
//     };
//
//     return (
//         <Layout>
//             <div className="flex">
//                 <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
//                 <div className="flex-1 p-6 bg-white min-h-screen">
//                     {activeTab === "dashboard" && (
//                         <>
//                             <h1 className="text-2xl font-semibold mb-4">🛡️ Threat Simulation</h1>
//                             <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
//                                 <div>
//                                     <label className="block mb-1">Sensor Type</label>
//                                     <select className="border p-2 w-full" value={selectedType} onChange={e => setSelectedType(e.target.value)}>
//                                         {sensorTypes.map(type => (
//                                             <option key={type} value={type}>{type}</option>
//                                         ))}
//                                     </select>
//                                 </div>
//                                 <div>
//                                     <label className="block mb-1">Sensor ID</label>
//                                     <select className="border p-2 w-full" value={selectedSensorId} onChange={e => setSelectedSensorId(e.target.value)}>
//                                         {sensorIds.map(id => (
//                                             <option key={id} value={id}>{id}</option>
//                                         ))}
//                                     </select>
//                                 </div>
//                                 <div>
//                                     <label className="block mb-1">Attack Type</label>
//                                     <select className="border p-2 w-full" value={selectedAttack} onChange={e => setSelectedAttack(e.target.value)}>
//                                         {Object.keys(ATTACK_TYPES).map(type => (
//                                             <option key={type} value={type}>{type}</option>
//                                         ))}
//                                     </select>
//                                 </div>
//                             </div>
//
//                             <label className="block mb-1 font-semibold">Attack Payload</label>
//                             <textarea
//                                 className="w-full border p-2 h-48 font-mono"
//                                 value={samplePayload}
//                                 onChange={e => setSamplePayload(e.target.value)}
//                             />
//                             <div className="flex gap-4 mt-2">
//                                 <button onClick={simulateAttack} className="bg-red-600 text-white px-4 py-2 rounded">🚀 Simulate Attack</button>
//                                 <button onClick={resetPayload} className="bg-gray-300 px-4 py-2 rounded">♻️ Reset Payload</button>
//                             </div>
//
//                             <div className="mt-6">
//                                 <span className="text-sm text-gray-600">
//                                     WebSocket Status: <strong className={wsStatus === "Connected" ? "text-green-600" : "text-red-500"}>{wsStatus}</strong>
//                                 </span>
//                                 {response && (
//                                     <pre className="bg-gray-100 mt-4 p-4 rounded text-sm text-gray-800 whitespace-pre-wrap">
//                                         {JSON.stringify(response, null, 2)}
//                                     </pre>
//                                 )}
//                             </div>
//                         </>
//                     )}
//
//                     {activeTab === "logs" && (
//                         <>
//                             <h1 className="text-2xl font-semibold mb-4">🧾 Audit Logs</h1>
//                             <div className="mb-4 flex flex-wrap gap-4">
//                                 <DatePicker selected={startDate} onChange={date => setStartDate(date)} placeholderText="Start Date" className="border p-2" />
//                                 <DatePicker selected={endDate} onChange={date => setEndDate(date)} placeholderText="End Date" className="border p-2" />
//                                 <select value={severityFilter} onChange={e => setSeverityFilter(e.target.value)} className="border p-2">
//                                     <option value="">All Severities</option>
//                                     <option value="Low">Low</option>
//                                     <option value="Medium">Medium</option>
//                                     <option value="High">High</option>
//                                 </select>
//                                 <input type="text" value={searchQuery} onChange={e => setSearchQuery(e.target.value)} placeholder="Search logs..." className="border p-2 flex-1" />
//                                 <button onClick={exportLogs} className="px-4 py-2 bg-green-600 text-white rounded">📤 Export</button>
//                             </div>
//
//                             <div className="overflow-x-auto bg-white shadow-md rounded">
//                                 <table className="min-w-full text-sm text-left">
//                                     <thead className="bg-gray-100 border-b">
//                                     <tr>
//                                         <th className="px-4 py-2">Time</th>
//                                         <th className="px-4 py-2">Sensor</th>
//                                         <th className="px-4 py-2">Attack</th>
//                                         <th className="px-4 py-2">Message</th>
//                                         <th className="px-4 py-2">Severity</th>
//                                         <th className="px-4 py-2">Status</th>
//                                     </tr>
//                                     </thead>
//                                     <tbody>
//                                     {filteredAnomalies.map((log, index) => (
//                                         <tr key={index} className="border-b hover:bg-gray-50">
//                                             <td className="px-4 py-2">{new Date(log.timestamp).toLocaleString()}</td>
//                                             <td className="px-4 py-2">{log.sensor_id}</td>
//                                             <td className="px-4 py-2">{log.attack_type || "Normal"}</td>
//                                             <td className="px-4 py-2">{log.message || "No anomaly"}</td>
//                                             <td className="px-4 py-2 text-red-600">{log.severity || "Low"}</td>
//                                             <td className="px-4 py-2">{log.status || "Accepted"}</td>
//                                         </tr>
//                                     ))}
//                                     </tbody>
//                                 </table>
//                             </div>
//                         </>
//                     )}
//
//                     {activeTab === "analytics" && (
//                         <>
//                             <h1 className="text-2xl font-semibold mb-4">📈 Threat Analytics</h1>
//                             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//                                 <div className="bg-white p-4 rounded shadow">
//                                     <Line data={getLineChartData()} />
//                                 </div>
//                                 <div className="bg-white p-4 rounded shadow">
//                                     <Bar data={getAnalyticsData()} />
//                                 </div>
//                             </div>
//                         </>
//                     )}
//                 </div>
//             </div>
//         </Layout>
//     );
// };
//
// export default ThreatDashboard;
