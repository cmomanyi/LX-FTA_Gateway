import React from "react";
import { Link, useNavigate } from "react-router-dom";

const Layout = ({ children }) => {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem("token");
        navigate("/");
    };

    const downloadLogs = () => {
        const logs = localStorage.getItem("sensor_logs");
        if (!logs) return;
        const blob = new Blob([logs], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "sensor_logs.json";
        a.click();
    };

    return (
        <>
            <nav style={{ background: "#222", padding: "10px", color: "#fff", display: "flex", justifyContent: "space-between" }}>
                <div>
                    <Link to="/genericdashboard" style={{ color: "#fff", marginRight: "15px", textDecoration: "none" }}>Dashboard</Link>
                    {/*<Link to="/dashboard" style={{ color: "#fff", marginRight: "15px", textDecoration: "none" }}>Welcome</Link>*/}
                    {/*<Link to="/websocketdashboard" style={{ color: "#fff", marginRight: "15px", textDecoration: "none" }}>Improved Dashboard</Link>*/}
                    <Link to="/viewanomalies" style={{ color: "#fff", marginRight: "15px", textDecoration: "none" }}>Anomaly Detection Dashboard</Link>
                    <Link to="/attacksimulate" style={{ color: "#fff", marginRight: "15px", textDecoration: "none" }}>Attack Dashboard</Link>
                    <Link to="/securitydashboard" style={{ color: "#fff", marginRight: "15px", textDecoration: "none" }}>Security Dashboard</Link>
                    <Link to="/firmwaredashboard" style={{ color: "#fff", marginRight: "15px", textDecoration: "none" }}>Firmware Dashboard</Link>
                    {/*<Link to="/attacksimulationdashboard" style={{ color: "#fff", marginRight: "15px", textDecoration: "none" }}>Attack Simulation Dashboard</Link>*/}
                    <Link to="/Shapdashboard" style={{ color: "#fff", marginRight: "15px", textDecoration: "none" }}>Shap Dashboard</Link>

                    {/*<Link to="/attackV2" style={{ color: "#fff", marginRight: "15px", textDecoration: "none" }}>attackV2</Link>*/}


                     <Link to="/admin" style={{ color: "#fff", marginRight: "15px", textDecoration: "none" }}>Admin</Link>
                </div>
                <div>
                    <button onClick={downloadLogs} style={{ marginRight: "10px" }}>Download Logs</button>
                    <button onClick={handleLogout}>Logout</button>
                </div>
            </nav>
            <main style={{ padding: "20px" }}>{children}</main>
        </>
    );
};

export default Layout;