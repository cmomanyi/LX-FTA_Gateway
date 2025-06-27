import React, { useEffect, useState } from "react";
import {
    fetchAllSoilSensors,
    fetchAllAtmosphericSensors,
    fetchAllWaterSensors,
    fetchAllPlantSensors,
    fetchAllThreatSensors,
} from "../components/api";
import { Line } from "react-chartjs-2";
import {
    Chart as ChartJS,
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement,
    Tooltip,
    Legend,
} from "chart.js";
import Layout from "../components/Layout";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

const SENSOR_CONFIG = {
    soil: {
        fetch: fetchAllSoilSensors,
        label: "Soil Readings",
        fields: ["temperature", "moisture", "ph", "nutrient_level"],
        labels: ["Temperature", "Moisture", "pH", "Nutrients"],
    },
    atmosphere: {
        fetch: fetchAllAtmosphericSensors,
        label: "Atmospheric Readings",
        fields: ["air_temperature", "humidity", "co2", "wind_speed", "rainfall"],
        labels: ["Air Temp", "Humidity", "CO₂", "Wind Speed", "Rainfall"],
    },
    water: {
        fetch: fetchAllWaterSensors,
        label: "Water Readings",
        fields: ["flow_rate", "water_level", "salinity", "ph", "turbidity"],
        labels: ["Flow Rate", "Water Level", "Salinity", "pH", "Turbidity"],
    },
    plant: {
        fetch: fetchAllPlantSensors,
        label: "Plant Health Metrics",
        fields: ["leaf_moisture", "chlorophyll_level", "growth_rate", "disease_risk", "stem_diameter"],
        labels: ["Leaf Moisture", "Chlorophyll", "Growth Rate", "Disease Risk", "Stem Diameter"],
    },
    threat: {
        fetch: fetchAllThreatSensors,
        label: "Threat Detection",
        fields: ["unauthorized_access", "jamming_signal", "tampering_attempts", "spoofing_attempts", "anomaly_score"],
        labels: ["Unauthorized Access", "Jamming", "Tampering", "Spoofing", "Anomaly Score"],
    }
};

const GenericSimulationSensor = () => {
    const [sensorType, setSensorType] = useState("soil");
    const [sensorIndex, setSensorIndex] = useState(0);
    const [allSensors, setAllSensors] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            const config = SENSOR_CONFIG[sensorType];
            if (config) {
                const data = await config.fetch();
                setAllSensors(data);
                setSensorIndex(0);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 10000);
        return () => clearInterval(interval);
    }, [sensorType]);

    const sensorData = allSensors[sensorIndex];
    const config = SENSOR_CONFIG[sensorType];

    const renderChart = () => {
        if (!sensorData || !config) return <p>Loading...</p>;

        const chartData = config.fields.map((field) => sensorData[field]);

        return (
            <>
                <ul className="mb-4 text-sm bg-white shadow rounded p-4">
                    {Object.entries(sensorData).map(([key, value]) => (
                        <li key={key} className="mb-1">
                            <strong>{key.replace(/_/g, " ")}:</strong> {value}
                        </li>
                    ))}
                </ul>
                <Line
                    data={{
                        labels: config.labels,
                        datasets: [
                            {
                                label: config.label,
                                data: chartData,
                                backgroundColor: "rgba(153,102,255,0.4)",
                                borderColor: "rgba(153,102,255,1)",
                                fill: true,
                                tension: 0.3,
                            },
                        ],
                    }}
                />
            </>
        );
    };

    return (
        <Layout>
            <div className="p-6 font-sans">
                <header className="mb-6">
                    <h1 className="text-3xl font-bold mb-4">🌐 Sensor Network Dashboard</h1>

                    <div className="mb-4">
                        <label className="mr-2 font-medium">Sensor Type:</label>
                        <select
                            value={sensorType}
                            onChange={(e) => setSensorType(e.target.value)}
                            className="border px-2 py-1 rounded"
                        >
                            {Object.keys(SENSOR_CONFIG).map((type) => (
                                <option key={type} value={type}>
                                    {type.charAt(0).toUpperCase() + type.slice(1)} Sensors
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="mr-2 font-medium">Select Sensor #:</label>
                        <select
                            value={sensorIndex}
                            onChange={(e) => setSensorIndex(Number(e.target.value))}
                            className="border px-2 py-1 rounded"
                        >
                            {allSensors.map((_, idx) => (
                                <option key={idx} value={idx}>
                                    Sensor {idx + 1}
                                </option>
                            ))}
                        </select>
                    </div>
                </header>

                <main>{renderChart()}</main>
            </div>
        </Layout>
    );
};

export default GenericSimulationSensor;