import React, { useState, useEffect } from "react";
import axios from "axios";
import Layout from "../components/Layout";

const SENSOR_TYPES = ["soil", "water", "atmospheric", "plant", "threat"];
const SENSOR_IDS = ["1", "2", "3", "4", "5"];

const FirmwareDashboard = () => {
    const [formData, setFormData] = useState({
        sensorType: "soil",
        sensorId: "1",
        firmwareVersion: "",
        issuerId: "Trusted_CA_01",
        deploymentDate: new Date().toISOString().split("T")[0],
        attemptDowngrade: false,
    });

    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadResult, setUploadResult] = useState(null);
    const [firmwareLogs, setFirmwareLogs] = useState([]);
    const [deviceStatus, setDeviceStatus] = useState(null);

    const fullSensorId = `${formData.sensorType}_${formData.sensorId}`;

    useEffect(() => {
        fetchFirmwareLogs();
    }, []);

    useEffect(() => {
        if (!fullSensorId) return;
        axios.get(`https://api.lx-gateway.tech/api/firmware/versions/${fullSensorId}`)
            .then((res) => {
                setDeviceStatus(res.data);
                if (res.data.last) {
                    setFormData((prev) => ({ ...prev, firmwareVersion: res.data.last }));
                }
            })
            .catch(() => setDeviceStatus(null));
    }, [formData.sensorType, formData.sensorId]);

    const fetchFirmwareLogs = async () => {
        try {
            const { data } = await axios.get("https://api.lx-gateway.tech/api/firmware/log");
            setFirmwareLogs(data);
        } catch (err) {
            console.error("Error fetching logs", err);
        }
    };

    const handleUpload = async (e) => {
        e.preventDefault();

        if (!formData.firmwareVersion.trim()) {
            alert("Please enter a valid firmware version.");
            return;
        }

        if (formData.attemptDowngrade && !window.confirm("You are attempting a downgrade. Are you sure?")) return;

        const payload = new FormData();
        payload.append("file", selectedFile);
        payload.append("sensor_id", fullSensorId);
        payload.append("firmwareVersion", formData.firmwareVersion);
        payload.append("issuerId", formData.issuerId);
        payload.append("deploymentDate", formData.deploymentDate);
        payload.append("attemptDowngrade", formData.attemptDowngrade);

        try {
            const { data } = await axios.post("https://api.lx-gateway.tech/firmware/upload", payload);
            setUploadResult(data);
            fetchFirmwareLogs();
        } catch (err) {
            setUploadResult({
                error: err.response?.data?.message || "Upload failed. Please check backend or file signature."
            });
        }
    };

    return (
        <Layout>
            <div className="p-4 max-w-4xl mx-auto">
                <h1 className="text-2xl font-bold mb-4">📦 Firmware Upload Dashboard</h1>

                <form onSubmit={handleUpload} className="bg-white shadow-md rounded px-6 py-4 mb-6">
                    <div className="mb-4">
                        <label className="block text-gray-700">Firmware File</label>
                        <input type="file" onChange={(e) => setSelectedFile(e.target.files[0])} required className="mt-1" />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        {[
                            { label: "Sensor Type", key: "sensorType", options: SENSOR_TYPES },
                            { label: "Sensor ID", key: "sensorId", options: SENSOR_IDS },
                        ].map(({ label, key, options }) => (
                            <div key={key}>
                                <label className="block">{label}</label>
                                <select
                                    value={formData[key]}
                                    onChange={(e) => setFormData({ ...formData, [key]: e.target.value })}
                                    className="w-full p-2 border rounded"
                                >
                                    {options.map((option) => (
                                        <option key={option} value={option}>{option}</option>
                                    ))}
                                </select>
                            </div>
                        ))}

                        {[
                            { label: "Firmware Version", key: "firmwareVersion", placeholder: "e.g. v1.0.0" },
                            { label: "Issuer ID", key: "issuerId" },
                            { label: "Deployment Date", key: "deploymentDate", type: "date" }
                        ].map(({ label, key, placeholder, type = "text" }) => (
                            <div key={key}>
                                <label className="block">{label}</label>
                                <input
                                    type={type}
                                    value={formData[key]}
                                    onChange={(e) => setFormData({ ...formData, [key]: e.target.value })}
                                    className="w-full p-2 border rounded"
                                    placeholder={placeholder || ""}
                                />
                            </div>
                        ))}
                    </div>

                    <div className="mt-4 flex items-center">
                        <input
                            type="checkbox"
                            checked={formData.attemptDowngrade}
                            onChange={(e) => setFormData({ ...formData, attemptDowngrade: e.target.checked })}
                            className="mr-2"
                        />
                        <label>☐ Attempt Downgrade (confirm rollback manually)</label>
                    </div>

                    <button type="submit" className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                        🚀 Simulate Upload
                    </button>
                </form>

                {deviceStatus && (
                    <div className="text-sm mt-4 mb-6 text-gray-700">
                        <p><strong>Current Version:</strong> {deviceStatus.current}</p>
                        <p><strong>Last Version:</strong> {deviceStatus.last}</p>
                        <p><strong>Rollback Protection:</strong> {deviceStatus.rollback_protection ? "Enabled 🔒" : "Disabled ✅"}</p>
                    </div>
                )}

                {uploadResult && (
                    <div className="bg-gray-100 p-4 rounded mb-4 border border-gray-300">
                        <h2 className="font-bold">Result:</h2>
                        <pre className="text-sm text-green-700">
              {JSON.stringify(uploadResult, null, 2)}
            </pre>
                    </div>
                )}

                <h2 className="text-xl font-semibold mt-8 mb-2">📜 Audit Log</h2>
                <div className="overflow-auto max-h-80 border p-4 rounded bg-white shadow">
                    {firmwareLogs.length === 0 ? (
                        <p>No logs yet.</p>
                    ) : (
                        firmwareLogs.map((log, idx) => (
                            <div key={idx} className="mb-3 border-b pb-2 text-sm">
                                <strong>{log.version}</strong> — {log.status} — <span className="text-gray-600">{log.issuer}</span>
                                <div className="text-gray-500 text-xs">{new Date(log.timestamp).toLocaleString()}</div>
                                <details className="text-xs mt-1">
                                    <summary className="cursor-pointer text-blue-600">View details</summary>
                                    <pre>{JSON.stringify(log, null, 2)}</pre>
                                </details>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </Layout>
    );
};

export default FirmwareDashboard;
