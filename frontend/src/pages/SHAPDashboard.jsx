// SHAPDashboard.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

const SHAPDashboard = () => {
    const [shapData, setShapData] = useState(null);
    const [expanded, setExpanded] = useState(true);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchShap = async () => {
            setLoading(true);
            try {
                const res = await axios.get("https://api.lx-gateway.tech/api/shap/latest");
                setShapData(res.data);
            } catch (error) {
                console.error("Failed to fetch SHAP explanation", error);
            }
            setLoading(false);
        };
        fetchShap();
    }, []);

    const handleDownloadImage = () => {
        if (shapData?.image) {
            const link = document.createElement("a");
            link.href = `data:image/png;base64,${shapData.image}`;
            link.download = `shap-explanation-${shapData.attack_type}.png`;
            link.click();
        }
    };

    return (
        <div className="p-6 text-gray-800 dark:bg-gray-900 dark:text-gray-100">
            <h1 className="text-3xl font-bold mb-6 cursor-pointer" onClick={() => setExpanded(!expanded)}>
                {expanded ? "🔍 SHAP Insights Dashboard (Click to Collapse)" : "🔍 SHAP Insights Dashboard (Click to Expand)"}
            </h1>

            {expanded && (
                <>
                    <p className="mb-4 text-md">
                        The <strong>XAI/SHAP Panel</strong> provides explainable AI (XAI) feedback whenever an attack leads to access denial or anomaly detection. It leverages <strong>SHAP</strong> values to visually break down which input features (e.g., sensor ID, frequency, temperature, firmware version) most influenced the model’s decision.
                    </p>

                    <p className="mb-4 text-md">
                        For example, in a <em>Sensor Hijack</em> case, the <code>sensor_id</code> may be the top contributor. In <em>ML Evasion</em>, drift in values like temperature or pH might stand out. These SHAP visuals support forensic analysis and responsible AI audits.
                    </p>

                    <h2 className="text-xl font-semibold mt-6 mb-2">📌 Live SHAP Insights</h2>
                    <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded mb-4 text-sm">
                        {loading ? (
                            <p>Loading SHAP explanation...</p>
                        ) : shapData ? (
                            <>
                                <p className="mb-2 font-medium">Detected Attack: {shapData.attack_type}</p>
                                <ul className="list-disc list-inside">
                                    {Object.entries(shapData.contributions).map(([feature, value]) => (
                                        <li key={feature}>
                                            {feature} ➝ <span className="text-red-600 dark:text-red-400 font-semibold">{value > 0 ? `+${value}` : value}</span>
                                        </li>
                                    ))}
                                </ul>
                                <p className="mt-2">⛔ Total contribution ➝ <strong>{shapData.total_score}</strong> ➝ Access Blocked</p>
                                {shapData.image && (
                                    <>
                                        <img src={`data:image/png;base64,${shapData.image}`} alt="SHAP Plot" className="mt-4 rounded shadow" />
                                        <button
                                            onClick={handleDownloadImage}
                                            className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                                        >
                                            ⬇️ Download SHAP Plot
                                        </button>
                                    </>
                                )}
                            </>
                        ) : (
                            <p>No SHAP insights available yet.</p>
                        )}
                    </div>

                    <h2 className="text-xl font-semibold mt-6 mb-2">🎯 What This Panel Shows</h2>
                    <ul className="list-disc list-inside pl-4 mt-2">
                        <li>🔍 Why was access blocked?</li>
                        <li>🔑 What features triggered anomaly?</li>
                        <li>🛠️ How can we tune policies better?</li>
                    </ul>

                    <h2 className="text-xl font-semibold mt-6 mb-2">🔗 Resources</h2>
                    <a
                        href="https://chatgpt.com/canvas/shared/68226f1b2458819190c4242451219908"
                        className="text-blue-600 dark:text-blue-400 underline"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        👉 View Full SHAP Implementation Guide
                    </a>
                </>
            )}
        </div>
    );
};

export default SHAPDashboard;
