import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import Layout from "../components/Layout";
import UserForm from "../components/UserForm";
import UserTable from "../components/UserTable";
import AnomalyLogViewer from "../components/AnomalyLogViewer";
import PolicyEditor from "../components/PolicyEditor";
import FirmwareSimulator from "../components/FirmwareSimulator";
import { initialUsers } from "../data/mockUsers";
import { sendAccountCreatedEmail } from "../utils/emailService";

const AdminDashboard = () => {
    const [activeTab, setActiveTab] = useState("users");
    const [users, setUsers] = useState(initialUsers);
    const [isAuthorized, setIsAuthorized] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem("token");
        const role = localStorage.getItem("role");

        if (!token || role !== "admin") {
            toast.error("Access denied: Admins only");
            setIsAuthorized(false);
            setTimeout(() => navigate("/unauthorized"), 1500);
        } else {
            setIsAuthorized(true);
        }
    }, [navigate]);

    const handleAddUser = async (user) => {
        const newUser = { ...user, id: Date.now() };
        setUsers((prev) => [...prev, newUser]);
        toast.success(`User ${user.name} added successfully`);

        try {
            await sendAccountCreatedEmail(newUser);
            toast.info(`Email notification sent to ${user.email}`);
        } catch (err) {
            toast.error("Failed to send email");
            console.error(err);
        }
    };

    const handleDeleteUser = (id) => {
        const deletedUser = users.find((u) => u.id === id);
        setUsers((prev) => prev.filter((u) => u.id !== id));
        toast.warn(`User ${deletedUser.name} deleted`);
    };

    const handleChangeRole = (id, newRole) => {
        setUsers((prev) =>
            prev.map((u) => (u.id === id ? { ...u, role: newRole } : u))
        );
        const changedUser = users.find((u) => u.id === id);
        toast.info(`${changedUser.name}'s role changed to ${newRole}`);
    };

    const renderContent = () => {
        switch (activeTab) {
            case "users":
                return (
                    <>
                        <UserForm onAddUser={handleAddUser} />
                        <UserTable
                            users={users}
                            onDelete={handleDeleteUser}
                            onChangeRole={handleChangeRole}
                        />
                    </>
                );
            case "anomalies":
                return (
                    <section className="bg-white p-4 rounded shadow">
                        <h2 className="text-xl font-semibold mb-2">📋 Anomaly Detection Logs</h2>
                        <AnomalyLogViewer />
                    </section>
                );
            case "policy":
                return (
                    <section className="bg-white p-4 rounded shadow">
                        <h2 className="text-xl font-semibold mb-2">🛡️ Policy-as-Code Editor</h2>
                        <PolicyEditor />
                    </section>
                );
            case "firmware":
                return (
                    <section className="bg-white p-4 rounded shadow">
                        <h2 className="text-xl font-semibold mb-2">📦 OTA Firmware Simulation</h2>
                        <FirmwareSimulator />
                    </section>
                );
            default:
                return null;
        }
    };

    if (isAuthorized === null) {
        return (
            <Layout>
                <div className="p-6 text-center text-gray-600">Checking permissions...</div>
                <ToastContainer position="bottom-right" autoClose={3000} />
            </Layout>
        );
    }

    if (!isAuthorized) {
        return (
            <Layout>
                <div className="p-6 text-center text-red-600 font-bold">Access Denied</div>
                <ToastContainer position="bottom-right" autoClose={3000} />
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="flex min-h-screen">
                {/* Sidebar */}
                <aside className="w-64 bg-gray-100 border-r p-4 space-y-4">
                    <h2 className="text-xl font-bold mb-4">🛠️ Admin Panel</h2>
                    <nav className="flex flex-col gap-2">
                        <button onClick={() => setActiveTab("users")} className={`p-2 rounded ${activeTab === "users" ? "bg-blue-500 text-white" : "hover:bg-blue-100"}`}>
                            👤 Manage Users
                        </button>
                        <button onClick={() => setActiveTab("anomalies")} className={`p-2 rounded ${activeTab === "anomalies" ? "bg-blue-500 text-white" : "hover:bg-blue-100"}`}>
                            📊 Anomaly Detection
                        </button>
                        <button onClick={() => setActiveTab("policy")} className={`p-2 rounded ${activeTab === "policy" ? "bg-blue-500 text-white" : "hover:bg-blue-100"}`}>
                            🛡️ Policy Editor
                        </button>
                        <button onClick={() => setActiveTab("firmware")} className={`p-2 rounded ${activeTab === "firmware" ? "bg-blue-500 text-white" : "hover:bg-blue-100"}`}>
                            📦 Firmware Simulator
                        </button>
                    </nav>
                </aside>

                {/* Main content area */}
                <main className="flex-1 p-6 space-y-6">
                    <h1 className="text-3xl font-bold mb-4">Admin Dashboard</h1>
                    {renderContent()}
                </main>
            </div>

            <ToastContainer position="bottom-right" autoClose={3000} />
        </Layout>
    );
};

export default AdminDashboard;
