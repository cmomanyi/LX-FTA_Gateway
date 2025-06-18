import React, { useState } from "react";
import { toast } from "react-toastify";

const FirmwareSimulator = () => {
    const [file, setFile] = useState(null);
    const [tamper, setTamper] = useState(false);

    const handleUpload = async () => {
        if (!file) {
            toast.warn("Please select a firmware file");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("simulate_tamper", tamper);

        try {
            const res = await fetch("https://api.lx-gateway.tech/api/firmware/update", {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("token")}`,
                },
                body: formData,
            });

            const data = await res.json();
            if (res.ok) {
                toast.success(`Update status: ${data.status}`);
            } else {
                toast.error(`Rejected: ${data.reason}`);
            }
        } catch (err) {
            toast.error(`Upload failed: ${err.message}`);
        }
    };

    return (
        <div className="space-y-4">
            <input
                type="file"
                accept=".bin,.hex"
                onChange={(e) => setFile(e.target.files[0])}
                className="block"
            />
            <label className="flex items-center gap-2">
                <input
                    type="checkbox"
                    checked={tamper}
                    onChange={() => setTamper(!tamper)}
                />
                Simulate tampered firmware
            </label>
            <button onClick={handleUpload} className="px-4 py-2 bg-indigo-600 text-white rounded">
                🚀 Simulate Upload
            </button>
        </div>
    );
};

export default FirmwareSimulator;
