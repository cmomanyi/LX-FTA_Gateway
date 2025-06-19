import React, { useEffect, useState } from "react";
import Layout from "../components/Layout";

const SENSOR_TYPES = ["soil", "water", "threat"];

const SensorDashboardWebSocket = () => {
    const [sensorType, setSensorType] = useState("soil");
    const [sensorData, setSensorData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        const socket = new WebSocket(`ws://api.lx-gateway.tech/ws/${sensorType}?token=${token}`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setSensorData(data);
        };

        socket.onerror = () => {
            setError("WebSocket connection failed.");
        };

        return () => socket.close();
    }, [sensorType]);

    // ... render dropdown
    return (
        <Layout>
        <div className="p-4">
            <select
                className="mb-4 p-2 border rounded"
                value={sensorType}
                onChange={(e) => setSensorType(e.target.value)}
            >
                {SENSOR_TYPES.map((type) => (
                    <option key={type} value={type}>
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                    </option>
                ))}
            </select>
            {/* ... chart and anomaly logic */}
        </div>
        </Layout>
    );
};



export default SensorDashboardWebSocket;
