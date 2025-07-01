import React, { useEffect, useState } from "react";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

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

    // Count Injected and Detected per attack_type
    const counts = logs.reduce((acc, log) => {
        const type = log.attack_type || "Normal";
        const isBlocked =
            log.blocked === true ||
            (log.severity && log.severity.toLowerCase().includes("high")) ||
            (log.message && log.message.toLowerCase().includes("blocked"));

        if (!acc[type]) {
            acc[type] = { injected: 0, detected: 0 };
        }

        acc[type].injected += 1;
        if (isBlocked) acc[type].detected += 1;

        return acc;
    }, {});

    const labels = Object.keys(counts);
    const injectedData = labels.map(type => counts[type].injected);
    const detectedData = labels.map(type => counts[type].detected);

    const chartData = {
        labels,
        datasets: [
            {
                label: "Attacks Injected",
                data: injectedData,
                backgroundColor: "orange"
            },
            {
                label: "Detected",
                data: detectedData,
                backgroundColor: "green"
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: "top"
            },
            title: {
                display: true,
                text: "Detected Threats per Attack Type in IoE Simulation"
            }
        },
        scales: {
            x: {
                ticks: {
                    maxRotation: 45,
                    minRotation: 45
                }
            },
            y: {
                title: {
                    display: true,
                    text: "Number of Events"
                },
                beginAtZero: true
            }
        }
    };

    return (
        <div className="dark bg-gray-900 text-white p-6 rounded-lg shadow-lg">
            <h2 className="text-2xl font-bold mb-4">📊 Threat Analytics</h2>
            {logs.length === 0 ? (
                <p className="text-gray-400 italic">Loading analytics data...</p>
            ) : (
                <Bar data={chartData} options={chartOptions} />
            )}
        </div>
    );
};

export default Analytics;
