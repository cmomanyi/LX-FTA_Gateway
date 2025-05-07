// src/components/AdminDashboard.jsx
import React, { useState } from "react";
import { initialUsers } from "../data/mockUsers";
import UserForm from "../components/UserForm";
import UserTable from "../components/UserTable";
import Layout from "../components/Layout";
import { sendAccountCreatedEmail } from "../utils/emailService";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";


const AdminDashboard = () => {
    const [users, setUsers] = useState(initialUsers);

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
    return (
        <Layout>
            <div className="p-6 max-w-4xl mx-auto">
                <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
                <UserForm onAddUser={handleAddUser}/>
                <UserTable users={users} onDelete={handleDeleteUser} onChangeRole={handleChangeRole}/>
                <ToastContainer position="bottom-right" autoClose={3000}/>
            </div>
        </Layout>
    );
};

export default AdminDashboard;
