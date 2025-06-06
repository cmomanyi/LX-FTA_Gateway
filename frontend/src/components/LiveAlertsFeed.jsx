import React, { useEffect, useState } from "react";

const LiveAlertsFeed = () => {
    const [alerts, setAlerts] = useState([]);

    useEffect(() => {
        const interval = setInterval(() => {
            const sampleAlert = {
                time: new Date().toLocaleTimeString(),
                type: "spoofing",
                sensor: "soil-1023",
                severity: "high",
            };
            setAlerts(prev => [sampleAlert, ...prev].slice(0, 20));
        }, 4000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="mt-6 p-4 bg-white shadow rounded-xl max-h-64 overflow-y-auto">
            <h3 className="text-lg font-semibold mb-2">Live Alerts</h3>
            <ul className="space-y-2 text-sm">
                {alerts.map((alert, idx) => (
                    <li key={idx} className="flex justify-between">
                        <span>{alert.time} - {alert.sensor} - {alert.type}</span>
                        <span className="font-bold text-red-500">{alert.severity}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default LiveAlertsFeed;
