import React from "react";

const sensorStatuses = {
    soil: "secure",
    water: "breached",
    plant: "secure",
    threat: "breached",
};

const StatusOverview = () => {
    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(sensorStatuses).map(([type, status]) => (
                <div key={type} className="flex items-center space-x-3 p-4 rounded-xl shadow bg-white">
                    <div
                        className={`w-4 h-4 rounded-full ${
                            status === "secure" ? "bg-green-500" : "bg-red-500"
                        }`}
                    />
                    <span className="capitalize">{type}</span>
                </div>
            ))}
        </div>
    );
};

export default StatusOverview;
