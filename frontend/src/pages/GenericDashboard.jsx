// import React, { useEffect, useState } from "react";
// import {
//     fetchAllSoilSensors,
//     fetchAllAtmosphericSensors,
//     fetchAllWaterSensors,
//     fetchAllPlantSensors,
//     fetchAllThreatSensors,
//     fetchSensorAverages,
// } from "../components/api";
// import { Line } from "react-chartjs-2";
// import {
//     Chart as ChartJS,
//     LineElement,
//     CategoryScale,
//     LinearScale,
//     PointElement,
//     Tooltip,
//     Legend,
//     Filler // ✅ Required for fill: true
// } from "chart.js";
// import Layout from "../components/Layout";
//
// ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend, Filler);
//
// const SENSOR_CONFIG = {
//     soil: {
//         fetch: fetchAllSoilSensors,
//         label: "Soil Readings",
//         fields: ["temperature", "moisture", "ph", "nutrient_level"],
//         labels: ["Temperature", "Moisture", "pH", "Nutrients"],
//     },
//     atmosphere: {
//         fetch: fetchAllAtmosphericSensors,
//         label: "Atmospheric Readings",
//         fields: ["air_temperature", "humidity", "co2", "wind_speed", "rainfall"],
//         labels: ["Air Temp", "Humidity", "CO₂", "Wind Speed", "Rainfall"],
//     },
//     water: {
//         fetch: fetchAllWaterSensors,
//         label: "Water Readings",
//         fields: ["flow_rate", "water_level", "salinity", "ph", "turbidity"],
//         labels: ["Flow Rate", "Water Level", "Salinity", "pH", "Turbidity"],
//     },
//     plant: {
//         fetch: fetchAllPlantSensors,
//         label: "Plant Health Metrics",
//         fields: ["leaf_moisture", "chlorophyll_level", "growth_rate", "disease_risk", "stem_diameter"],
//         labels: ["Leaf Moisture", "Chlorophyll", "Growth Rate", "Disease Risk", "Stem Diameter"],
//     },
//     threat: {
//         fetch: fetchAllThreatSensors,
//         label: "Threat Detection",
//         fields: ["unauthorized_access", "jamming_signal", "tampering_attempts", "spoofing_attempts", "anomaly_score"],
//         labels: ["Unauthorized Access", "Jamming", "Tampering", "Spoofing", "Anomaly Score"],
//     }
// };
//
// const GenericDashboard = () => {
//     const [sensorType, setSensorType] = useState("soil");
//     const [sensorIndex, setSensorIndex] = useState(0);
//     const [allSensors, setAllSensors] = useState([]);
//     const [sensorData, setSensorData] = useState(null);
//     const [averages, setAverages] = useState({});
//
//     useEffect(() => {
//         const fetchData = async () => {
//             const config = SENSOR_CONFIG[sensorType];
//             if (!config) return;
//
//             try {
//                 const fullData = await config.fetch();
//                 const avgData = await fetchSensorAverages();
//
//                 const cloned = JSON.parse(JSON.stringify(fullData)); // Deep clone
//                 setAllSensors(cloned);
//                 setAverages(avgData);
//
//                 if (cloned[sensorIndex]) {
//                     setSensorData(cloned[sensorIndex]);
//                     console.log("✅ Updated sensorData:", cloned[sensorIndex]);
//                 }
//             } catch (error) {
//                 console.error("❌ Fetch error:", error);
//             }
//         };
//
//         fetchData();
//         const interval = setInterval(fetchData, 5000);
//         return () => clearInterval(interval);
//     }, [sensorType, sensorIndex]);
//
//     const config = SENSOR_CONFIG[sensorType];
//     const avgData = averages[sensorType];
//
//     const renderChart = () => {
//         if (!sensorData || !config) return <p>Loading...</p>;
//
//         const chartData = config.fields.map((field) => sensorData[field]);
//
//         return (
//             <>
//                 <ul className="mb-4 text-sm bg-white shadow rounded p-4">
//                     {Object.entries(sensorData).map(([key, value]) => (
//                         <li key={key} className="mb-1">
//                             <strong>{key.replace(/_/g, " ")}:</strong> {value}
//                         </li>
//                     ))}
//                 </ul>
//                 <Line
//                     data={{
//                         labels: config.labels,
//                         datasets: [
//                             {
//                                 label: config.label,
//                                 data: chartData,
//                                 backgroundColor: "rgba(153,102,255,0.4)",
//                                 borderColor: "rgba(153,102,255,1)",
//                                 fill: true, // ✅ Now works because Filler plugin is registered
//                                 tension: 0.3,
//                             },
//                         ],
//                     }}
//                     options={{
//                         animation: {
//                             duration: 500
//                         },
//                         scales: {
//                             y: {
//                                 beginAtZero: true,
//                             }
//                         }
//                     }}
//                 />
//             </>
//         );
//     };
//
//     const renderAverages = () => {
//         if (!avgData || !config) return null;
//
//         return (
//             <div className="absolute top-4 right-4 bg-white border shadow-lg rounded p-4 w-64 z-10">
//                 <h2 className="text-md font-semibold mb-2">📊 Avg {sensorType} metrics</h2>
//                 <ul className="text-sm">
//                     {Object.entries(avgData).map(([key, value]) => (
//                         <li key={key} className="mb-1">
//                             <strong>{key.replace(/_/g, " ")}:</strong> {parseFloat(value).toFixed(2)}
//                         </li>
//                     ))}
//                 </ul>
//             </div>
//         );
//     };
//
//     return (
//         <Layout>
//             <div className="relative p-6 font-sans min-h-screen">
//                 {renderAverages()}
//                 <header className="mb-6">
//                     <h1 className="text-3xl font-bold mb-4">🌐 Sensor Network Dashboard</h1>
//
//                     <div className="mb-4">
//                         <label className="mr-2 font-medium">Sensor Type:</label>
//                         <select
//                             value={sensorType}
//                             onChange={(e) => setSensorType(e.target.value)}
//                             className="border px-2 py-1 rounded"
//                         >
//                             {Object.keys(SENSOR_CONFIG).map((type) => (
//                                 <option key={type} value={type}>
//                                     {type.charAt(0).toUpperCase() + type.slice(1)} Sensors
//                                 </option>
//                             ))}
//                         </select>
//                     </div>
//
//                     <div>
//                         <label className="mr-2 font-medium">Select Sensor #:</label>
//                         <select
//                             value={sensorIndex}
//                             onChange={(e) => setSensorIndex(Number(e.target.value))}
//                             className="border px-2 py-1 rounded"
//                         >
//                             {allSensors.map((_, idx) => (
//                                 <option key={idx} value={idx}>
//                                     Sensor {idx + 1}
//                                 </option>
//                             ))}
//                         </select>
//                     </div>
//                 </header>
//
//                 <main>
//                     {renderChart()}
//                 </main>
//             </div>
//         </Layout>
//     );
// };
//
// export default GenericDashboard;
import React, { useEffect, useState } from "react";
import {
    fetchAllSoilSensors,
    fetchAllAtmosphericSensors,
    fetchAllWaterSensors,
    fetchAllPlantSensors,
    fetchAllThreatSensors,
    fetchSensorAverages,
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
    Filler
} from "chart.js";
import Layout from "../components/Layout";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend, Filler);

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

const GenericDashboard = () => {
    const [sensorType, setSensorType] = useState("soil");
    const [sensorIndex, setSensorIndex] = useState(0);
    const [allSensors, setAllSensors] = useState([]);
    const [sensorData, setSensorData] = useState(null);
    const [averages, setAverages] = useState({});
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            const config = SENSOR_CONFIG[sensorType];
            if (!config) return;

            setLoading(true);
            try {
                const [sensorResults, avgResults] = await Promise.all([
                    config.fetch(),
                    fetchSensorAverages()
                ]);

                setAllSensors(sensorResults || []);
                setAverages(avgResults || {});

                if (Array.isArray(sensorResults) && sensorResults[sensorIndex]) {
                    setSensorData(sensorResults[sensorIndex]);
                }
            } catch (error) {
                console.error("❌ Data fetch error:", error);
                setAllSensors([]);
                setSensorData(null);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [sensorType, sensorIndex]);

    const config = SENSOR_CONFIG[sensorType];
    const avgData = averages?.[sensorType];

    const renderChart = () => {
        if (loading) return <p className="text-gray-500">⏳ Loading sensor data...</p>;
        if (!sensorData || !config) return <p>No data available for this sensor.</p>;

        const chartData = config.fields.map((field) => sensorData[field]);

        return (
            <>
                <ul className="mb-4 text-sm bg-white shadow rounded p-4">
                    {Object.entries(sensorData).map(([key, value]) => (
                        <li key={key} className="mb-1">
                            <strong>{key.replace(/_/g, " ")}:</strong> {String(value)}
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
                    options={{
                        responsive: true,
                        animation: { duration: 500 },
                        scales: {
                            y: { beginAtZero: true },
                        },
                    }}
                />
            </>
        );
    };

    const renderAverages = () => {
        if (!avgData || !config) return null;

        return (
            <div className="absolute top-4 right-4 bg-white border shadow-lg rounded p-4 w-64 z-10">
                <h2 className="text-md font-semibold mb-2">📊 Avg {sensorType} metrics</h2>
                <ul className="text-sm">
                    {Object.entries(avgData).map(([key, value]) => (
                        <li key={key} className="mb-1">
                            <strong>{key.replace(/_/g, " ")}:</strong> {parseFloat(value).toFixed(2)}
                        </li>
                    ))}
                </ul>
            </div>
        );
    };

    return (
        <Layout>
            <div className="relative p-6 font-sans min-h-screen">
                {renderAverages()}
                <header className="mb-6">
                    <h1 className="text-3xl font-bold mb-4">🌐 Sensor Network Dashboard</h1>

                    <div className="mb-4">
                        <label className="mr-2 font-medium">Sensor Type:</label>
                        <select
                            value={sensorType}
                            onChange={(e) => {
                                setSensorType(e.target.value);
                                setSensorIndex(0); // Reset sensor index on change
                            }}
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
                            disabled={!Array.isArray(allSensors) || allSensors.length === 0}
                        >
                            {Array.isArray(allSensors) &&
                                allSensors.map((_, idx) => (
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

export default GenericDashboard;
