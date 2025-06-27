import React, { useEffect, useState } from "react";
import {
    fetchAllSoilSensors,
    fetchAllAtmosphericSensors,
    fetchAllWaterSensors,
    fetchAllPlantSensors,
    fetchAllThreatSensors,
} from "../components/api";

const SENSOR_CONFIG = {
    soil: {
        fetch: fetchAllSoilSensors,
        label: "Soil",
        fields: ["temperature", "moisture", "ph", "nutrient_level"],
    },
    atmosphere: {
        fetch: fetchAllAtmosphericSensors,
        label: "Atmosphere",
        fields: ["air_temperature", "humidity", "co2", "wind_speed", "rainfall"],
    },
    water: {
        fetch: fetchAllWaterSensors,
        label: "Water",
        fields: ["flow_rate", "water_level", "salinity", "ph", "turbidity"],
    },
    plant: {
        fetch: fetchAllPlantSensors,
        label: "Plant",
        fields: ["leaf_moisture", "chlorophyll_level", "growth_rate", "disease_risk", "stem_diameter"],
    },
    threat: {
        fetch: fetchAllThreatSensors,
        label: "Threat",
        fields: ["unauthorized_access", "jamming_signal", "tampering_attempts", "spoofing_attempts", "anomaly_score"],
    }
};

const SensorAveragesDashboard = () => {
    const [averages, setAverages] = useState({});

    useEffect(() => {
        const fetchAverages = async () => {
            const results = {};
            for (const [type, config] of Object.entries(SENSOR_CONFIG)) {
                const data = await config.fetch();
                const totals = {};
                config.fields.forEach((field) => (totals[field] = 0));

                data.forEach(sensor => {
                    config.fields.forEach(field => {
                        totals[field] += sensor[field] || 0;
                    });
                });

                const count = data.length || 1;
                results[type] = config.fields.map(field => ({
                    name: field,
                    average: (totals[field] / count).toFixed(2)
                }));
            }
            setAverages(results);
        };

        fetchAverages();
        const interval = setInterval(fetchAverages, 10000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold mb-4">📊 Sensor Averages Overview</h2>
            {Object.entries(averages).map(([type, data]) => (
                <div key={type} className="mb-6">
                    <h3 className="text-xl font-semibold mb-2 capitalize">{SENSOR_CONFIG[type].label}</h3>
                    <table className="w-full table-auto border">
                        <thead className="bg-gray-200">
                        <tr>
                            <th className="p-2 text-left">Metric</th>
                            <th className="p-2 text-left">Average</th>
                        </tr>
                        </thead>
                        <tbody>
                        {data.map((item) => (
                            <tr key={item.name} className="border-t">
                                <td className="p-2">{item.name.replace(/_/g, " ")}</td>
                                <td className="p-2">{item.average}</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            ))}
        </div>
    );
};

export default SensorAveragesDashboard;
