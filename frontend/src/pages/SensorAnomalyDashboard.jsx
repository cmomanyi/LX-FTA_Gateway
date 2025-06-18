import React, { useEffect, useState, useRef } from "react";
import { Radar, Bar } from "react-chartjs-2";
import {
    Chart as ChartJS,
    RadialLinearScale,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Filler,
    Tooltip,
    Legend,
} from "chart.js";
import zoomPlugin from "chartjs-plugin-zoom";
import Layout from "../components/Layout";

ChartJS.register(
    RadialLinearScale,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Filler,
    Tooltip,
    Legend,
    zoomPlugin
);

const SENSOR_BASELINES = {
    soil: {
        temperature: [18, 30],
        moisture: [30, 70],
        ph: [6, 7.5],
        nutrient_level: [0.2, 0.9],
        battery_level: [3.3, 5.0],
    },
    water: {
        flow_rate: [5, 15],
        water_level: [10, 45],
        salinity: [0.2, 0.4],
        ph: [6.5, 8.0],
        turbidity: [1.0, 4.0],
    },
    threat: {
        unauthorized_access: [0, 0],
        jamming: [0, 0],
        tampering: [0, 0],
        spoofing: [0, 0],
        anomaly_score: [0.0, 0.3],
    },
};

const SENSOR_TYPES = Object.keys(SENSOR_BASELINES);

const SensorAnomalyDashboard = () => {
    const [sensorType, setSensorType] = useState("soil");
    const [sensorData, setSensorData] = useState(null);
    const [error, setError] = useState(null);
    const [chartType, setChartType] = useState("radar");
    const [logs, setLogs] = useState([]);
    const [searchTerm, setSearchTerm] = useState("");
    const chartRef = useRef(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        const socket = new WebSocket(`ws://api.lx-gateway.tech/ws/${sensorType}?token=${token}`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setSensorData(data);
            setError(null);
        };

        socket.onerror = () => {
            setError("WebSocket connection failed.");
            setSensorData(null);
        };

        return () => socket.close();
    }, [sensorType]);

    // ✅ Detect and log anomalies safely after new sensor data is set
    useEffect(() => {
        if (!sensorData) return;

        Object.entries(SENSOR_BASELINES[sensorType]).forEach(([metric]) => {
            const value = sensorData[metric];
            const [min, max] = SENSOR_BASELINES[sensorType][metric];

            if (value < min || value > max) {
                const anomaly = {
                    timestamp: new Date().toISOString(),
                    sensor_type: sensorType,
                    sensor_id: sensorData.sensor_id || "unknown",
                    metric,
                    value,
                };
                setLogs((prev) => [...prev, anomaly]);

                fetch("https://api.lx-gateway.tech/log/anomaly", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(anomaly),
                });

                // 🚨 Alert on critical anomalies
                if (
                    value > 90 ||
                    (sensorType === "threat" && value > 0) ||
                    ["unauthorized_access", "jamming", "tampering"].includes(metric)
                ) {
                    alert(`🚨 CRITICAL ANOMALY\n${metric.toUpperCase()}: ${value}`);
                }
            }
        });
    }, [sensorData, sensorType]);

    const getChartData = () => {
        const metrics = Object.keys(SENSOR_BASELINES[sensorType]);
        const baseline = metrics.map(
            m => (SENSOR_BASELINES[sensorType][m][0] + SENSOR_BASELINES[sensorType][m][1]) / 2
        );
        const values = metrics.map(m => sensorData?.[m] || 0);

        return {
            labels: metrics,
            datasets: [
                {
                    label: "Baseline",
                    data: baseline,
                    backgroundColor: "rgba(0,0,255,0.1)",
                    borderColor: "blue",
                    borderWidth: 2,
                },
                {
                    label: "Live",
                    data: values,
                    backgroundColor: "rgba(255,165,0,0.1)",
                    borderColor: "orange",
                    borderWidth: 2,
                },
            ],
        };
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: "top" },
            zoom: {
                zoom: {
                    wheel: { enabled: true },
                    pinch: { enabled: true },
                    mode: chartType === "bar" ? "x" : "r",
                },
                pan: {
                    enabled: true,
                    mode: chartType === "bar" ? "x" : "r",
                },
            },
        },
        scales: chartType === "bar"
            ? {
                y: {
                    beginAtZero: true,
                },
                x: {},
            }
            : {
                r: {
                    min: 0,
                    max: 100,
                    beginAtZero: true,
                },
            },
    };

    const handleResetZoom = () => {
        if (chartRef.current?.chart) {
            chartRef.current.chart.resetZoom();
        }
    };

    const handleDownloadImage = () => {
        const chart = chartRef.current?.chart;
        if (!chart) return;

        const link = document.createElement("a");
        link.download = `${sensorType}_chart.png`;
        link.href = chart.toBase64Image();
        link.click();
    };

    const handleExportCSV = () => {
        const headers = ["timestamp", "sensor_type", "sensor_id", "metric", "value"];
        const rows = logs.map(log => headers.map(h => JSON.stringify(log[h] || "")).join(","));
        const blob = new Blob([[headers.join(","), ...rows].join("\n")], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "anomaly_logs.csv";
        link.click();
    };

    const filteredLogs = logs.filter(log =>
        Object.values(log).some(val =>
            String(val).toLowerCase().includes(searchTerm.toLowerCase())
        )
    );

    return (
        <Layout>
        <div className="p-4">
            <h2 className="text-xl font-semibold mb-2">Interactive Sensor Anomaly Dashboard</h2>

            <div className="flex gap-4 mb-4 flex-wrap">
                <select
                    className="p-2 border rounded"
                    value={sensorType}
                    onChange={(e) => setSensorType(e.target.value)}
                >
                    {SENSOR_TYPES.map((type) => (
                        <option key={type} value={type}>
                            {type.charAt(0).toUpperCase() + type.slice(1)}
                        </option>
                    ))}
                </select>

                <button onClick={() => setChartType(chartType === "radar" ? "bar" : "radar")} className="px-3 py-2 bg-gray-100 rounded border">
                    Toggle to {chartType === "radar" ? "Bar" : "Radar"} Chart
                </button>

                <button onClick={handleResetZoom} className="px-3 py-2 bg-gray-100 rounded border">
                    Reset Zoom
                </button>

                <button onClick={handleDownloadImage} className="px-3 py-2 bg-blue-600 text-white rounded border">
                    Export Chart Image
                </button>
            </div>

            {error && <p className="text-red-500">{error}</p>}

            {!sensorData ? (
                <p className="text-gray-600">Waiting for real-time data...</p>
            ) : (
                <>
                    <p className="mb-2">Sensor ID: <strong>{sensorData.sensor_id}</strong></p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-[500px]">
                        {chartType === "radar" ? (
                            <Radar ref={chartRef} data={getChartData()} options={chartOptions} />
                        ) : (
                            <Bar ref={chartRef} data={getChartData()} options={chartOptions} />
                        )}
                        <div className="space-y-2">
                            {Object.entries(SENSOR_BASELINES[sensorType]).map(([metric]) => {
                                const value = sensorData[metric];
                                const [min, max] = SENSOR_BASELINES[sensorType][metric];
                                const anomaly = value < min || value > max;
                                return (
                                    <p key={metric} className={anomaly ? "text-red-600" : "text-green-700"}>
                                        <strong>{metric}</strong>: {value} {anomaly && "⚠️ Anomaly"}
                                    </p>
                                );
                            })}
                        </div>
                    </div>
                </>
            )}

            <div className="mt-8 border-t pt-6">
                <h3 className="text-lg font-semibold mb-2">Anomaly Logs</h3>
                <div className="flex gap-2 mb-2">
                    <input
                        type="text"
                        placeholder="Search logs..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="p-2 border rounded w-full"
                    />
                    <button onClick={handleExportCSV} className="px-3 py-2 bg-green-600 text-white rounded">
                        Export CSV
                    </button>
                </div>
                <div className="overflow-x-auto max-h-64 overflow-y-scroll border rounded">
                    <table className="table-auto w-full text-sm">
                        <thead className="bg-gray-100 sticky top-0">
                        <tr>
                            <th className="p-2">Timestamp</th>
                            <th className="p-2">Sensor</th>
                            <th className="p-2">ID</th>
                            <th className="p-2">Metric</th>
                            <th className="p-2">Value</th>
                        </tr>
                        </thead>
                        <tbody>
                        {filteredLogs.map((log, idx) => (
                            <tr key={idx} className="border-t">
                                <td className="p-2">{log.timestamp}</td>
                                <td className="p-2">{log.sensor_type}</td>
                                <td className="p-2">{log.sensor_id}</td>
                                <td className="p-2">{log.metric}</td>
                                <td className="p-2">{log.value}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        </Layout>
    );
};

export default SensorAnomalyDashboard;
