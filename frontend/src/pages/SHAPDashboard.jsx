// import React, { useState } from "react";
// import axios from "axios";
//
// const SENSOR_FIELDS = {
//     soil: {
//         model: "SoilData",
//         fields: ["temperature", "moisture", "ph", "nutrient_level", "battery_level"]
//     },
//     atmosphere: {
//         model: "AtmosphericData",
//         fields: ["air_temperature", "humidity", "co2", "wind_speed", "rainfall", "battery_level"]
//     },
//     water: {
//         model: "WaterData",
//         fields: ["flow_rate", "water_level", "salinity", "ph", "turbidity", "battery_level"]
//     },
//     plant: {
//         model: "PlantData",
//         fields: ["leaf_moisture", "chlorophyll_level", "growth_rate", "disease_risk", "stem_diameter", "battery_level"]
//     },
//     threat: {
//         model: "ThreatData",
//         fields: ["unauthorized_access", "jamming_signal", "tampering_attempts", "spoofing_attempts", "anomaly_score", "battery_level"]
//     }
// };
//
// const ShapDashboard = () => {
//     const [sensorType, setSensorType] = useState("soil");
//     const [inputValues, setInputValues] = useState({});
//     const [response, setResponse] = useState(null);
//
//     const handleChange = (field, value) => {
//         setInputValues(prev => ({ ...prev, [field]: value }));
//     };
//
//     const handleSubmit = async () => {
//         try {
//             const res = await axios.post(`http://localhost:8000/api/shap/explain?sensor_type=${sensorType}`, inputValues);
//             setResponse(res.data);
//         } catch (err) {
//             console.error(err);
//             alert("Failed to fetch SHAP explanation. Check console for details.");
//         }
//     };
//
//     const fields = SENSOR_FIELDS[sensorType].fields;
//
//     return (
//         <div className="p-6">
//             <h2 className="text-xl font-bold mb-4">🔍 SHAP Model Explanation</h2>
//
//             <label className="font-medium">Sensor Type:</label>
//             <select
//                 className="border rounded px-2 py-1 mb-4 block"
//                 value={sensorType}
//                 onChange={(e) => {
//                     setSensorType(e.target.value);
//                     setInputValues({}); // Reset fields on sensor change
//                     setResponse(null);
//                 }}
//             >
//                 {Object.keys(SENSOR_FIELDS).map(type => (
//                     <option key={type} value={type}>{type}</option>
//                 ))}
//             </select>
//
//             {fields.map(field => (
//                 <div key={field} className="mb-2">
//                     <label className="block text-sm font-semibold">{field.replace(/_/g, ' ')}:</label>
//                     <input
//                         type="number"
//                         value={inputValues[field] || ""}
//                         onChange={(e) => handleChange(field, parseFloat(e.target.value))}
//                         className="border px-2 py-1 rounded w-full"
//                     />
//                 </div>
//             ))}
//
//             <button
//                 onClick={handleSubmit}
//                 className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
//             >
//                 Get SHAP Explanation
//             </button>
//
//             {response && (
//                 <div className="mt-6 bg-white p-4 shadow rounded">
//                     <h3 className="text-md font-semibold">Prediction: {response.prediction}</h3>
//                     <p className="text-sm">Base Value: {response.base_value}</p>
//                     <ul className="text-sm mt-2">
//                         {response.features.map((f, idx) => (
//                             <li key={idx}>
//                                 <strong>{f.feature}:</strong> {f.contribution}
//                             </li>
//                         ))}
//                     </ul>
//                 </div>
//             )}
//         </div>
//     );
// };
//
// export default ShapDashboard;
// ShapDashboard.jsx
import React, { useState } from "react";
import axios from "axios";

const SENSOR_TYPES = ["soil", "atmospheric", "water", "plant", "threat"];

const DUMMY_DATA = {
    soil: {
        sensor_id: "soil-1001",
        temperature: 24.3,
        moisture: 55.0,
        ph: 6.5,
        nutrient_level: 3.2,
        battery_level: 4.1,
        status: "active"
    },
    atmosphere: {
        sensor_id: "atm-2002",
        air_temperature: 29.4,
        humidity: 60,
        co2: 420,
        wind_speed: 5,
        rainfall: 15,
        battery_level: 3.7,
        status: "active"
    },
    water: {
        sensor_id: "water-3003",
        flow_rate: 3,
        water_level: 150,
        salinity: 2.5,
        ph: 7.0,
        turbidity: 5,
        battery_level: 4,
        status: "active"
    },
    plant: {
        sensor_id: "plant-4004",
        leaf_moisture: 60,
        chlorophyll_level: 3.1,
        growth_rate: 2.0,
        disease_risk: 0.3,
        stem_diameter: 1.2,
        battery_level: 4,
        status: "healthy"
    },
    threat: {
        sensor_id: "threat-5005",
        unauthorized_access: 1,
        jamming_signal: 0,
        tampering_attempts: 0,
        spoofing_attempts: 1,
        anomaly_score: 0.7,
        battery_level: 4,
        status: "alerting"
    }
};

const ShapDashboard = () => {
    const [sensorType, setSensorType] = useState("soil");
    const [explanation, setExplanation] = useState(null);
    const [forceImage, setForceImage] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleExplain = async () => {
        setLoading(true);
        try {
            const response = await axios.post(
                `https://api.lx-gateway.tech/api/shap/explain?sensor_type=${sensorType}`,
                DUMMY_DATA[sensorType]
            );
            setExplanation(response.data);
        } catch (error) {
            console.error("Explain error:", error);
        }
        setLoading(false);
    };

    const handleForcePlot = async () => {
        setLoading(true);
        try {
            const response = await axios.post(
                `https://api.lx-gateway.tech/api/shap/force-plot?sensor_type=${sensorType}`,
                DUMMY_DATA[sensorType]
            );
            setForceImage(response.data.image_base64);
        } catch (error) {
            console.error("Force plot error:", error);
        }
        setLoading(false);
    };

    return (
        <div className="p-6 font-sans min-h-screen bg-gray-100">
            <h1 className="text-2xl font-bold mb-4">SHAP Explanation Dashboard</h1>

            <label className="mr-2 font-medium">Sensor Type:</label>
            <select
                className="border px-2 py-1 rounded mb-4"
                value={sensorType}
                onChange={(e) => setSensorType(e.target.value)}
            >
                {SENSOR_TYPES.map((type) => (
                    <option key={type} value={type}>
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                    </option>
                ))}
            </select>

            <div className="space-x-4 mb-6">
                <button
                    onClick={handleExplain}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                    Explain
                </button>
                <button
                    onClick={handleForcePlot}
                    className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
                >
                    Show Force Plot
                </button>
            </div>

            {loading && <p className="text-sm text-gray-600">Loading...</p>}

            {explanation && (
                <div className="bg-white rounded shadow p-4 mb-6">
                    <h2 className="text-lg font-semibold mb-2">Prediction: {explanation.prediction}</h2>
                    <p className="text-sm text-gray-500 mb-4">Base value: {explanation.base_value}</p>
                    <ul className="text-sm">
                        {explanation.features.map((f) => (
                            <li key={f.feature}>
                                <strong>{f.feature}</strong>: {f.contribution}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {forceImage && (
                <div className="bg-white rounded shadow p-4">
                    <h2 className="text-lg font-semibold mb-2">SHAP Force Plot</h2>
                    <img
                        src={`data:image/png;base64,${forceImage}`}
                        alt="SHAP force plot"
                        className="w-full max-w-3xl"
                    />
                </div>
            )}
        </div>
    );
};

export default ShapDashboard;

