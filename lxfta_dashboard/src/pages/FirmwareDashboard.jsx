import React, { useState, useEffect } from "react";
import axios from "axios";
import Layout from "../components/Layout";

const FirmwareDashboard = () => {
    const [formData, setFormData] = useState({
        firmwareVersion: "v3.0.5",
        issuerId: "Trusted_CA_01",
        targetDevice: "soil_sensor_alpha",
        deploymentDate: new Date().toISOString().split("T")[0],
        attemptDowngrade: false,
    });
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadResult, setUploadResult] = useState(null);
    const [firmwareLogs, setFirmwareLogs] = useState([]);

    useEffect(() => {
        fetchFirmwareLogs();
    }, []);

    const fetchFirmwareLogs = async () => {
        try {
            const response = await axios.get("http://localhost:8000/api/firmware/log");
            setFirmwareLogs(response.data);
        } catch (error) {
            console.error("Error fetching logs", error);
        }
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        const payload = new FormData();
        payload.append("file", selectedFile);
        Object.entries(formData).forEach(([key, value]) => {
            payload.append(key, value);
        });

        try {
            const response = await axios.post("http://localhost:8000/api/firmware/upload", payload);
            setUploadResult(response.data);
            fetchFirmwareLogs();
        } catch (error) {
            setUploadResult({ error: "Upload failed. Check the backend." });
        }
    };

    return (
        <Layout>
            <div className="p-4 max-w-4xl mx-auto">
                <h1 className="text-2xl font-bold mb-4">📦 Firmware Upload Simulator</h1>

                <form
                    onSubmit={handleUpload}
                    className="bg-white shadow-md rounded px-6 py-4 mb-6"
                >
                    <div className="mb-4">
                        <label className="block text-gray-700">Firmware File</label>
                        <input
                            type="file"
                            onChange={(e) => setSelectedFile(e.target.files[0])}
                            className="mt-1"
                            required
                        />
                        <a
                            href="http://localhost:8000/api/sample-firmware"
                            download
                            className="inline-block mb-4 text-blue-600 underline hover:text-blue-800"
                        >
                            📥 Download Sample Firmware File
                        </a>

                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block">Firmware Version</label>
                            <input
                                type="text"
                                value={formData.firmwareVersion}
                                onChange={(e) =>
                                    setFormData({ ...formData, firmwareVersion: e.target.value })
                                }
                                className="w-full p-2 border rounded"
                            />
                        </div>

                        <div>
                            <label className="block">Issuer ID</label>
                            <input
                                type="text"
                                value={formData.issuerId}
                                onChange={(e) =>
                                    setFormData({ ...formData, issuerId: e.target.value })
                                }
                                className="w-full p-2 border rounded"
                            />
                        </div>

                        <div>
                            <label className="block">Target Device</label>
                            <input
                                type="text"
                                value={formData.targetDevice}
                                onChange={(e) =>
                                    setFormData({ ...formData, targetDevice: e.target.value })
                                }
                                className="w-full p-2 border rounded"
                            />
                        </div>

                        <div>
                            <label className="block">Deployment Date</label>
                            <input
                                type="date"
                                value={formData.deploymentDate}
                                onChange={(e) =>
                                    setFormData({ ...formData, deploymentDate: e.target.value })
                                }
                                className="w-full p-2 border rounded"
                            />
                        </div>
                    </div>

                    <div className="mt-4 flex items-center">
                        <input
                            type="checkbox"
                            checked={formData.attemptDowngrade}
                            onChange={(e) =>
                                setFormData({ ...formData, attemptDowngrade: e.target.checked })
                            }
                            className="mr-2"
                        />
                        <label>☐ Attempt Downgrade (simulate rollback lock)</label>
                    </div>

                    <button
                        type="submit"
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                        Simulate Upload
                    </button>
                </form>

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
                            <div
                                key={idx}
                                className="mb-3 border-b pb-2 text-sm"
                            >
                <span
                    className={`inline-block w-2 h-2 rounded-full mr-2 ${
                        log.status === "Verified" ? "bg-green-500" : "bg-red-500"
                    }`}
                ></span>
                                <strong>{log.version}</strong> — {log.status} —{" "}
                                <span className="text-gray-600">{log.issuer}</span>
                                <div className="text-gray-500 text-xs">
                                    {new Date(log.timestamp).toLocaleString()}
                                </div>
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
