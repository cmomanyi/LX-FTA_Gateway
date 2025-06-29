// // ShapDashboard.jsx
// import React, { useState } from "react";
// import axios from "axios";
//
// const SENSOR_TYPES = ["soil", "atmosphere", "water", "plant", "threat"];
//
// const DUMMY_DATA = {
//     soil: {
//         sensor_id: "soil-1001",
//         temperature: 24.3,
//         moisture: 55.0,
//         ph: 6.5,
//         nutrient_level: 3.2,
//         battery_level: 4.1,
//         status: "active"
//     },
//     atmosphere: {
//         sensor_id: "atm-2002",
//         air_temperature: 29.4,
//         humidity: 60,
//         co2: 420,
//         wind_speed: 5,
//         rainfall: 15,
//         battery_level: 3.7,
//         status: "active"
//     },
//     water: {
//         sensor_id: "water-3003",
//         flow_rate: 3,
//         water_level: 150,
//         salinity: 2.5,
//         ph: 7.0,
//         turbidity: 5,
//         battery_level: 4,
//         status: "active"
//     },
//     plant: {
//         sensor_id: "plant-4004",
//         leaf_moisture: 60,
//         chlorophyll_level: 3.1,
//         growth_rate: 2.0,
//         disease_risk: 0.3,
//         stem_diameter: 1.2,
//         battery_level: 4,
//         status: "healthy"
//     },
//     threat: {
//         sensor_id: "threat-5005",
//         unauthorized_access: 1,
//         jamming_signal: 0,
//         tampering_attempts: 0,
//         spoofing_attempts: 1,
//         anomaly_score: 0.7,
//         battery_level: 4,
//         status: "alerting"
//     }
// };
//
// const ATTACK_CUES = {
//     spoofing: "ECC signature mismatch indicates possible data tampering.",
//     replay: "Reused nonce or old timestamp detected, indicating replay attack.",
//     ddos: "High request frequency from the same sensor suggests flooding.",
//     firmware: "Invalid firmware signature implies unauthorized update attempt.",
//     ml_evasion: "Sensor readings significantly differ from expected patterns.",
//     sensor_hijack: "Sensor stream was manipulated or intercepted.",
//     api_abuse: "API endpoints accessed in unauthorized or excessive patterns.",
//     tamper_breach: "Physical access interference detected on the sensor.",
//     side_channel: "Unusual timing or behavior implying covert data leakage."
// };
//
// const ShapDashboard = () => {
//     const [sensorType, setSensorType] = useState("soil");
//     const [explanation, setExplanation] = useState(null);
//     const [forceImage, setForceImage] = useState(null);
//     const [loading, setLoading] = useState(false);
//
//     const handleExplain = async () => {
//         setLoading(true);
//         try {
//             const response = await axios.post(
//                 `https://api.lx-gateway.tech/api/shap/explain?sensor_type=${sensorType}`,
//                 DUMMY_DATA[sensorType]
//             );
//             setExplanation(response.data);
//         } catch (error) {
//             console.error("Explain error:", error);
//         }
//         setLoading(false);
//     };
//
//     const handleForcePlot = async () => {
//         setLoading(true);
//         try {
//             const response = await axios.post(
//                 `https://api.lx-gateway.tech/api/shap/force-plot?sensor_type=${sensorType}`,
//                 DUMMY_DATA[sensorType]
//             );
//             setForceImage(response.data.image_base64);
//         } catch (error) {
//             console.error("Force plot error:", error);
//         }
//         setLoading(false);
//     };
//
//     return (
//         <div className="p-6 font-sans min-h-screen bg-gray-100">
//             <h1 className="text-2xl font-bold mb-4">SHAP Explanation Dashboard</h1>
//
//             <label className="mr-2 font-medium">Sensor Type:</label>
//             <select
//                 className="border px-2 py-1 rounded mb-4"
//                 value={sensorType}
//                 onChange={(e) => setSensorType(e.target.value)}
//             >
//                 {SENSOR_TYPES.map((type) => (
//                     <option key={type} value={type}>
//                         {type.charAt(0).toUpperCase() + type.slice(1)}
//                     </option>
//                 ))}
//             </select>
//
//             <div className="space-x-4 mb-6">
//                 <button
//                     onClick={handleExplain}
//                     className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
//                 >
//                     Explain
//                 </button>
//                 <button
//                     onClick={handleForcePlot}
//                     className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
//                 >
//                     Show Force Plot
//                 </button>
//             </div>
//
//             {loading && <p className="text-sm text-gray-600">Loading...</p>}
//
//             {explanation && (
//                 <div className="bg-white rounded shadow p-4 mb-6">
//                     <h2 className="text-lg font-semibold mb-2">
//                         Prediction: <span className={explanation.prediction === "1" ? "text-red-600" : "text-green-600"}>{explanation.prediction === "1" ? "⚠️ Attack Blocked" : "✅ Allowed"}</span>
//                     </h2>
//                     <p className="text-sm text-gray-500 mb-2">Base value: {explanation.base_value}</p>
//                     <ul className="text-sm mb-2">
//                         {explanation.features.map((f) => (
//                             <li key={f.feature} className="mb-1">
//                                 <span className="font-semibold text-blue-700">{f.feature}</span>: <span className={f.contribution > 0 ? "text-red-600" : "text-green-600"}>{f.contribution.toFixed(4)}</span>
//                             </li>
//                         ))}
//                     </ul>
//                     {ATTACK_CUES[explanation.attack_type] && (
//                         <div className="text-sm text-gray-700 border-t pt-3 mt-2">
//                             <strong>Explanation:</strong> {ATTACK_CUES[explanation.attack_type]}
//                         </div>
//                     )}
//                 </div>
//             )}
//
//             {forceImage && (
//                 <div className="bg-white rounded shadow p-4">
//                     <h2 className="text-lg font-semibold mb-2">SHAP Force Plot</h2>
//                     <img
//                         src={`data:image/png;base64,${forceImage}`}
//                         alt="SHAP force plot"
//                         className="w-full max-w-3xl"
//                     />
//                 </div>
//             )}
//         </div>
//     );
// };
//
// export default ShapDashboard;

// ShapDashboard.jsx
// ShapDashboard.jsx
// import React, { useState, useEffect } from "react";
// import axios from "axios";
//
// const ATTACK_CUES = {
//     spoofing: "ECC signature mismatch indicates possible data tampering.",
//     replay: "Reused nonce or old timestamp detected, indicating replay attack.",
//     ddos: "High request frequency from the same sensor suggests flooding.",
//     firmware: "Invalid firmware signature implies unauthorized update attempt.",
//     ml_evasion: "Sensor readings significantly differ from expected patterns.",
//     sensor_hijack: "Sensor stream was manipulated or intercepted.",
//     api_abuse: "API endpoints accessed in unauthorized or excessive patterns.",
//     tamper_breach: "Physical access interference detected on the sensor.",
//     side_channel: "Unusual timing or behavior implying covert data leakage."
// };
//
// const ShapDashboard = () => {
//     const [sensorType, setSensorType] = useState("soil");
//     const [sensorTypes, setSensorTypes] = useState([]);
//     const [dummyData, setDummyData] = useState({});
//     const [explanation, setExplanation] = useState(null);
//     const [forceImage, setForceImage] = useState(null);
//     const [loading, setLoading] = useState(false);
//
//     useEffect(() => {
//         const fetchSensorTypes = async () => {
//             try {
//                 const response = await axios.get("https://api.lx-gateway.tech/api/sensor-types");
//                 setSensorTypes(response.data.types || []);
//             } catch (error) {
//                 console.error("Error fetching sensor types:", error);
//             }
//         };
//
//         fetchSensorTypes();
//     }, []);
//
//     const fetchDummyData = async (type) => {
//         try {
//             const response = await axios.get(`https://api.lx-gateway.tech/api/dummy-data/${type}`);
//             return response.data;
//         } catch (error) {
//             console.error("Failed to fetch dummy data:", error);
//             return {};
//         }
//     };
//
//     const handleExplain = async () => {
//         setLoading(true);
//         const data = await fetchDummyData(sensorType);
//         setDummyData((prev) => ({ ...prev, [sensorType]: data }));
//
//         try {
//             const response = await axios.post(
//                 `https://api.lx-gateway.tech/api/shap/explain?sensor_type=${sensorType}`,
//                 data
//             );
//             setExplanation(response.data);
//         } catch (error) {
//             console.error("Explain error:", error);
//         }
//         setLoading(false);
//     };
//
//     const handleForcePlot = async () => {
//         setLoading(true);
//         const data = await fetchDummyData(sensorType);
//         setDummyData((prev) => ({ ...prev, [sensorType]: data }));
//
//         try {
//             const response = await axios.post(
//                 `https://api.lx-gateway.tech/api/shap/force-plot?sensor_type=${sensorType}`,
//                 data
//             );
//             setForceImage(response.data.image_base64);
//         } catch (error) {
//             console.error("Force plot error:", error);
//         }
//         setLoading(false);
//     };
//
//     return (
//         <div className="p-6 font-sans min-h-screen bg-gray-100">
//             <h1 className="text-2xl font-bold mb-4">SHAP Explanation Dashboard</h1>
//
//             <label className="mr-2 font-medium">Sensor Type:</label>
//             <select
//                 className="border px-2 py-1 rounded mb-4"
//                 value={sensorType}
//                 onChange={(e) => setSensorType(e.target.value)}
//             >
//                 {sensorTypes.map((type) => (
//                     <option key={type} value={type}>
//                         {type.charAt(0).toUpperCase() + type.slice(1)}
//                     </option>
//                 ))}
//             </select>
//
//             <div className="space-x-4 mb-6">
//                 <button
//                     onClick={handleExplain}
//                     className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
//                 >
//                     Explain
//                 </button>
//                 <button
//                     onClick={handleForcePlot}
//                     className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
//                 >
//                     Show Force Plot
//                 </button>
//             </div>
//
//             {dummyData[sensorType] && (
//                 <div className="bg-white rounded shadow p-4 mb-6">
//                     <h2 className="text-md font-semibold mb-2 text-gray-700">Dummy Input Preview:</h2>
//                     <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto">
//                         {JSON.stringify(dummyData[sensorType], null, 2)}
//                     </pre>
//                 </div>
//             )}
//
//             {loading && <p className="text-sm text-gray-600">Loading...</p>}
//
//             {explanation && (
//                 <div className="bg-white rounded shadow p-4 mb-6">
//                     <h2 className="text-lg font-semibold mb-2">
//                         Prediction: <span className={explanation.prediction === "1" ? "text-red-600" : "text-green-600"}>{explanation.prediction === "1" ? "⚠️ Attack Blocked" : "✅ Allowed"}</span>
//                     </h2>
//                     <p className="text-sm text-gray-500 mb-2">Base value: {explanation.base_value}</p>
//                     <ul className="text-sm mb-2">
//                         {explanation.features.map((f) => (
//                             <li key={f.feature} className="mb-1">
//                                 <span className="font-semibold text-blue-700">{f.feature}</span>: <span className={f.contribution > 0 ? "text-red-600" : "text-green-600"}>{f.contribution.toFixed(4)}</span>
//                             </li>
//                         ))}
//                     </ul>
//                     {ATTACK_CUES[explanation.attack_type] && (
//                         <div className="text-sm text-gray-700 border-t pt-3 mt-2">
//                             <strong>Explanation:</strong> {ATTACK_CUES[explanation.attack_type]}
//                         </div>
//                     )}
//                 </div>
//             )}
//
//             {forceImage && (
//                 <div className="bg-white rounded shadow p-4">
//                     <h2 className="text-lg font-semibold mb-2">SHAP Force Plot</h2>
//                     <img
//                         src={`data:image/png;base64,${forceImage}`}
//                         alt="SHAP force plot"
//                         className="w-full max-w-3xl"
//                     />
//                 </div>
//             )}
//         </div>
//     );
// };
//
// export default ShapDashboard;


// ShapDashboard.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";

const ATTACK_CUES = {
    spoofing: "ECC signature mismatch indicates possible data tampering.",
    replay: "Reused nonce or old timestamp detected, indicating replay attack.",
    ddos: "High request frequency from the same sensor suggests flooding.",
    firmware: "Invalid firmware signature implies unauthorized update attempt.",
    ml_evasion: "Sensor readings significantly differ from expected patterns.",
    sensor_hijack: "Sensor stream was manipulated or intercepted.",
    api_abuse: "API endpoints accessed in unauthorized or excessive patterns.",
    tamper_breach: "Physical access interference detected on the sensor.",
    side_channel: "Unusual timing or behavior implying covert data leakage."
};

const ShapDashboard = () => {
    const [sensorType, setSensorType] = useState("soil");
    const [sensorTypes, setSensorTypes] = useState([]);
    const [dummyData, setDummyData] = useState({});
    const [explanation, setExplanation] = useState(null);
    const [forceImage, setForceImage] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchSensorTypes = async () => {
            try {
                const response = await axios.get("https://api.lx-gateway.tech/api/sensor-types");
                setSensorTypes(response.data.types || []);
                if (!response.data.types.includes(sensorType)) {
                    setSensorType(response.data.types[0]);
                }
            } catch (error) {
                console.error("Error fetching sensor types:", error);
            }
        };

        fetchSensorTypes();
    }, []);

    const fetchDummyData = async (type) => {
        try {
            const response = await axios.get(`https://api.lx-gateway.tech/api/dummy-data/${type}`);
            return response.data;
        } catch (error) {
            console.error("Failed to fetch dummy data:", error);
            return {};
        }
    };

    const handleExplain = async () => {
        setLoading(true);
        const data = await fetchDummyData(sensorType);
        setDummyData((prev) => ({ ...prev, [sensorType]: data }));

        try {
            const response = await axios.post(
                `https://api.lx-gateway.tech/api/shap/explain?sensor_type=${sensorType}`,
                data
            );
            setExplanation(response.data);
        } catch (error) {
            console.error("Explain error:", error);
        }
        setLoading(false);
    };

    const handleForcePlot = async () => {
        setLoading(true);
        const data = await fetchDummyData(sensorType);
        setDummyData((prev) => ({ ...prev, [sensorType]: data }));

        try {
            const response = await axios.post(
                `https://api.lx-gateway.tech/api/shap/force-plot?sensor_type=${sensorType}`,
                data
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
                {sensorTypes.map((type) => (
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

            {dummyData[sensorType] && (
                <div className="bg-white rounded shadow p-4 mb-6">
                    <h2 className="text-md font-semibold mb-2 text-gray-700">Dummy Input Preview:</h2>
                    <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                        {JSON.stringify(dummyData[sensorType], null, 2)}
                    </pre>
                </div>
            )}

            {loading && <p className="text-sm text-gray-600">Loading...</p>}

            {explanation && (
                <div className="bg-white rounded shadow p-4 mb-6">
                    <h2 className="text-lg font-semibold mb-2">
                        Prediction: <span className={explanation.prediction === "1" ? "text-red-600" : "text-green-600"}>{explanation.prediction === "1" ? "⚠️ Attack Blocked" : "✅ Allowed"}</span>
                    </h2>
                    <p className="text-sm text-gray-500 mb-2">Base value: {explanation.base_value}</p>
                    <ul className="text-sm mb-2">
                        {explanation.features.map((f) => (
                            <li key={f.feature} className="mb-1">
                                <span className="font-semibold text-blue-700">{f.feature}</span>: <span className={f.contribution > 0 ? "text-red-600" : "text-green-600"}>{f.contribution.toFixed(4)}</span>
                            </li>
                        ))}
                    </ul>
                    {ATTACK_CUES[explanation.attack_type] && (
                        <div className="text-sm text-gray-700 border-t pt-3 mt-2">
                            <strong>Explanation:</strong> {ATTACK_CUES[explanation.attack_type]}
                        </div>
                    )}
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
