// import React, { useState, useEffect } from "react";
// import axios from "axios";
// import Layout from "../components/Layout";
//
// const SENSOR_TYPES = ["soil", "water", "atmospheric", "plant", "threat"];
// const SENSOR_IDS = ["1", "2", "3", "4", "5"];
//
// const FirmwareDashboard = () => {
//     const [formData, setFormData] = useState({
//         sensorType: "soil",
//         sensorId: "1",
//         firmwareVersion: "",
//         issuerId: "Trusted_CA_01",
//         deploymentDate: new Date().toISOString().split("T")[0],
//         attemptDowngrade: false,
//     });
//
//     const [selectedFile, setSelectedFile] = useState(null);
//     const [uploadResult, setUploadResult] = useState(null);
//     const [firmwareLogs, setFirmwareLogs] = useState([]);
//     const [deviceStatus, setDeviceStatus] = useState(null);
//
//     const fullSensorId = `${formData.sensorType}_${formData.sensorId}`;
//
//     useEffect(() => {
//         fetchFirmwareLogs();
//     }, []);
//
//     useEffect(() => {
//         if (fullSensorId) {
//             axios
//                 .get(`http://localhost:8000/api/firmware/versions/${fullSensorId}`)
//                 .then((res) => {
//                     setDeviceStatus(res.data);
//                     if (res.data.last) {
//                         setFormData((prev) => ({
//                             ...prev,
//                             firmwareVersion: res.data.last
//                         }));
//                     }
//                 })
//                 .catch(() => setDeviceStatus(null));
//         }
//     }, [formData.sensorType, formData.sensorId]);
//
//     const fetchFirmwareLogs = async () => {
//         try {
//             const response = await axios.get("http://localhost:8000/api/firmware/log");
//             setFirmwareLogs(response.data);
//         } catch (error) {
//             console.error("Error fetching logs", error);
//         }
//     };
//
//     const handleUpload = async (e) => {
//         e.preventDefault();
//
//         if (!formData.firmwareVersion.trim()) {
//             alert("Please enter a valid firmware version.");
//             return;
//         }
//
//         if (formData.attemptDowngrade) {
//             const confirmed = window.confirm("You are attempting a downgrade. Are you sure?");
//             if (!confirmed) return;
//         }
//
//         const payload = new FormData();
//         payload.append("file", selectedFile);
//         payload.append("sensor_id", fullSensorId);
//         payload.append("firmwareVersion", formData.firmwareVersion);
//         payload.append("issuerId", formData.issuerId);
//         payload.append("deploymentDate", formData.deploymentDate);
//         payload.append("attemptDowngrade", formData.attemptDowngrade.toString());
//
//         try {
//             const response = await axios.post("http://localhost:8000/api/firmware/upload", payload);
//             setUploadResult(response.data);
//             fetchFirmwareLogs();
//         } catch (error) {
//             setUploadResult({
//                 error: error.response?.data?.message || "Upload failed. Please check backend or file signature."
//             });
//         }
//     };
//
//     return (
//         <Layout>
//             <div className="p-4 max-w-4xl mx-auto">
//                 <h1 className="text-2xl font-bold mb-4">📦 Firmware Upload Dashboard</h1>
//
//                 <form onSubmit={handleUpload} className="bg-white shadow-md rounded px-6 py-4 mb-6">
//                     <div className="mb-4">
//                         <label className="block text-gray-700">Firmware File</label>
//                         <input
//                             type="file"
//                             onChange={(e) => setSelectedFile(e.target.files[0])}
//                             className="mt-1"
//                             required
//                         />
//                     </div>
//
//                     <div className="grid grid-cols-2 gap-4">
//                         <div>
//                             <label className="block">Sensor Type</label>
//                             <select
//                                 value={formData.sensorType}
//                                 onChange={(e) => setFormData({ ...formData, sensorType: e.target.value })}
//                                 className="w-full p-2 border rounded"
//                             >
//                                 {SENSOR_TYPES.map((type) => (
//                                     <option key={type} value={type}>{type}</option>
//                                 ))}
//                             </select>
//                         </div>
//
//                         <div>
//                             <label className="block">Sensor ID</label>
//                             <select
//                                 value={formData.sensorId}
//                                 onChange={(e) => setFormData({ ...formData, sensorId: e.target.value })}
//                                 className="w-full p-2 border rounded"
//                             >
//                                 {SENSOR_IDS.map((id) => (
//                                     <option key={id} value={id}>{id}</option>
//                                 ))}
//                             </select>
//                         </div>
//
//                         <div>
//                             <label className="block">Firmware Version</label>
//                             <input
//                                 type="text"
//                                 value={formData.firmwareVersion}
//                                 onChange={(e) => setFormData({ ...formData, firmwareVersion: e.target.value })}
//                                 className="w-full p-2 border rounded"
//                                 placeholder="e.g. v1.0.0"
//                             />
//                         </div>
//
//                         <div>
//                             <label className="block">Issuer ID</label>
//                             <input
//                                 type="text"
//                                 value={formData.issuerId}
//                                 onChange={(e) => setFormData({ ...formData, issuerId: e.target.value })}
//                                 className="w-full p-2 border rounded"
//                             />
//                         </div>
//
//                         <div>
//                             <label className="block">Deployment Date</label>
//                             <input
//                                 type="date"
//                                 value={formData.deploymentDate}
//                                 onChange={(e) => setFormData({ ...formData, deploymentDate: e.target.value })}
//                                 className="w-full p-2 border rounded"
//                             />
//                         </div>
//                     </div>
//
//                     <div className="mt-4 flex items-center">
//                         <input
//                             type="checkbox"
//                             checked={formData.attemptDowngrade}
//                             onChange={(e) => setFormData({ ...formData, attemptDowngrade: e.target.checked })}
//                             className="mr-2"
//                         />
//                         <label>☐ Attempt Downgrade (confirm rollback manually)</label>
//                     </div>
//
//                     <button type="submit" className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
//                         🚀 Simulate Upload
//                     </button>
//                 </form>
//
//                 {deviceStatus && (
//                     <div className="text-sm mt-4 mb-6 text-gray-700">
//                         <p><strong>Current Version:</strong> {deviceStatus.current}</p>
//                         <p><strong>Last Version:</strong> {deviceStatus.last}</p>
//                         <p><strong>Rollback Protection:</strong> {deviceStatus.rollback_protection ? "Enabled 🔒" : "Disabled ✅"}</p>
//                     </div>
//                 )}
//
//                 {uploadResult && (
//                     <div className="bg-gray-100 p-4 rounded mb-4 border border-gray-300">
//                         <h2 className="font-bold">Result:</h2>
//                         <pre className="text-sm text-green-700">
//               {JSON.stringify(uploadResult, null, 2)}
//             </pre>
//                     </div>
//                 )}
//
//                 <h2 className="text-xl font-semibold mt-8 mb-2">📜 Audit Log</h2>
//                 <div className="overflow-auto max-h-80 border p-4 rounded bg-white shadow">
//                     {firmwareLogs.length === 0 ? (
//                         <p>No logs yet.</p>
//                     ) : (
//                         firmwareLogs.map((log, idx) => (
//                             <div key={idx} className="mb-3 border-b pb-2 text-sm">
//                                 <strong>{log.version}</strong> — {log.status} —{" "}
//                                 <span className="text-gray-600">{log.issuer}</span>
//                                 <div className="text-gray-500 text-xs">
//                                     {new Date(log.timestamp).toLocaleString()}
//                                 </div>
//                                 <details className="text-xs mt-1">
//                                     <summary className="cursor-pointer text-blue-600">View details</summary>
//                                     <pre>{JSON.stringify(log, null, 2)}</pre>
//                                 </details>
//                             </div>
//                         ))
//                     )}
//                 </div>
//             </div>
//         </Layout>
//     );
// };
//
// export default FirmwareDashboard;
