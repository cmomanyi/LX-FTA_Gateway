import React, { useEffect, useState, useRef } from "react";
import Layout from "../components/Layout";

const SENSOR_TYPES = ["soil", "water", "threat"];

const SensorDashboardWebSocket = () => {
    const [sensorType, setSensorType] = useState("soil");
    const [sensorData, setSensorData] = useState(null);
    const [error, setError] = useState(null);
    const wsRef = useRef(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        const wsUrl = `wss://api.lx-gateway.tech/ws/${sensorType}?token=${token}`;
        const socket = new WebSocket(wsUrl);
        wsRef.current = socket;

        socket.onopen = () => {
            console.log(`[WebSocket] Connected to ${wsUrl}`);
            setError(null);
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setSensorData(data);
            } catch (err) {
                console.error("Failed to parse WebSocket message:", err);
            }
        };

        socket.onerror = () => {
            setError("⚠️ WebSocket connection failed.");
        };

        socket.onclose = () => {
            console.log(`[WebSocket] Disconnected from ${wsUrl}`);
        };

        return () => {
            socket.close();
        };
    }, [sensorType]);

    return (
        <Layout>
            <div className="p-6 max-w-3xl mx-auto">
                <h2 className="text-xl font-bold mb-4">📡 Live Sensor Data</h2>

                <label className="block font-medium mb-1">Select Sensor Type</label>
                <select
                    className="mb-6 p-2 border border-gray-300 rounded w-full"
                    value={sensorType}
                    onChange={(e) => setSensorType(e.target.value)}
                >
                    {SENSOR_TYPES.map((type) => (
                        <option key={type} value={type}>
                            {type.charAt(0).toUpperCase() + type.slice(1)}
                        </option>
                    ))}
                </select>

                {error && (
                    <div className="text-red-600 font-semibold mb-4">
                        {error}
                    </div>
                )}

                {sensorData ? (
                    <div className="bg-gray-100 p-4 rounded shadow border text-sm">
                        <h3 className="font-semibold mb-2">Latest Sensor Data</h3>
                        <pre>{JSON.stringify(sensorData, null, 2)}</pre>
                    </div>
                ) : (
                    <p className="text-gray-600">Waiting for sensor data...</p>
                )}
            </div>
        </Layout>
    );
};

export default SensorDashboardWebSocket;
