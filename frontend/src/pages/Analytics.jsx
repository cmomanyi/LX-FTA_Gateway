// Analytics.jsx
import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const Analytics = () => {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await fetch("https://api.lx-gateway.tech/api/logs");
                const data = await res.json();
                setLogs(data.logs || []);
            } catch (error) {
                console.error("Analytics fetch error", error);
            }
        };

        fetchLogs();
        const interval = setInterval(fetchLogs, 15000);
        return () => clearInterval(interval);
    }, []);

    const groupedBySensor = logs.reduce((acc, log) => {
        const sensor = log.sensor_id || "unknown";
        acc[sensor] = (acc[sensor] || 0) + 1;
        return acc;
    }, {});

    const chartData = {
        labels: Object.keys(groupedBySensor),
        datasets: [
            {
                label: "Alerts by Sensor",
                data: Object.values(groupedBySensor),
                fill: false,
                borderColor: "rgb(75, 192, 192)",
                tension: 0.2
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: { position: "top" },
            title: { display: true, text: "Sensor Activity Overview" }
        }
    };

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4">📈 Threat Analytics</h2>
            {logs.length === 0 ? (
                <p className="text-gray-500 italic">Loading analytics data...</p>
            ) : (
                <Line data={chartData} options={chartOptions} />
            )}
        </div>
    );
};

export default Analytics;
