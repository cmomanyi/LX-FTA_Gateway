import React, { useState } from "react";
import { toast } from "react-toastify";

const PolicyEditor = () => {
    const [policy, setPolicy] = useState("{\n  \"rules\": []\n}");

    const handleAction = async (endpoint, label) => {
        try {
            const res = await fetch(`http://localhost:8000/api/policy/${endpoint}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("token")}`,
                },
                body: JSON.stringify({ policy: JSON.parse(policy) }),
            });

            const data = await res.json();
            if (res.ok) {
                toast.success(`${label} succeeded: ${data.message || "Success"}`);
            } else {
                toast.error(`${label} failed: ${data.error || "Unknown error"}`);
            }
        } catch (err) {
            toast.error(`${label} failed: ${err.message}`);
        }
    };

    return (
        <div>
            <textarea
                className="w-full h-64 border p-2 font-mono text-sm rounded"
                value={policy}
                onChange={(e) => setPolicy(e.target.value)}
            />

            <div className="flex gap-4 mt-4">
                <button onClick={() => handleAction("validate", "Validation")} className="px-4 py-2 bg-blue-500 text-white rounded">
                    ✅ Validate
                </button>
                <button onClick={() => handleAction("simulate", "Simulation")} className="px-4 py-2 bg-yellow-500 text-white rounded">
                    ⚙️ Simulate
                </button>
                <button onClick={() => handleAction("deploy", "Deployment")} className="px-4 py-2 bg-green-600 text-white rounded">
                    🚀 Deploy
                </button>
            </div>
        </div>
    );
};

export default PolicyEditor;
