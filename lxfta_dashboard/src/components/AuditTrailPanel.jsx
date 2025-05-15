import React, { useState } from "react";

const mockData = [
    { time: "10:03:21", sensor: "plant-1202", attack: "firmware injection", status: "breached" },
    { time: "10:05:10", sensor: "threat-2101", attack: "replay", status: "breached" },
];

const AuditTrailPanel = () => {
    const [search, setSearch] = useState("");

    const filtered = mockData.filter(entry =>
        entry.sensor.includes(search) || entry.attack.includes(search)
    );

    return (
        <div className="mt-6 bg-white p-4 shadow rounded-xl">
            <h3 className="text-lg font-semibold mb-2">Audit Trail</h3>
            <input
                type="text"
                className="w-full p-2 mb-3 border rounded"
                placeholder="Search by sensor or attack"
                value={search}
                onChange={e => setSearch(e.target.value)}
            />
            <table className="w-full text-sm">
                <thead>
                <tr className="text-left border-b">
                    <th>Time</th>
                    <th>Sensor</th>
                    <th>Attack</th>
                    <th>Status</th>
                </tr>
                </thead>
                <tbody>
                {filtered.map((log, idx) => (
                    <tr key={idx} className="border-b">
                        <td>{log.time}</td>
                        <td>{log.sensor}</td>
                        <td>{log.attack}</td>
                        <td className={log.status === "breached" ? "text-red-500" : "text-green-500"}>
                            {log.status}
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
};

export default AuditTrailPanel;
