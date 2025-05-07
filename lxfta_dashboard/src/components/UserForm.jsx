// src/components/UserForm.jsx
import React, { useState } from "react";

const roles = ["Admin", "User", "Moderator"];

const UserForm = ({ onAddUser }) => {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [role, setRole] = useState("User");

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!name || !email) return;
        onAddUser({ name, email, role });
        setName("");
        setEmail("");
        setRole("User");
    };

    return (
        <form onSubmit={handleSubmit} className="mb-4 space-y-2">
            <input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} className="p-2 border w-full" />
            <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="p-2 border w-full" />
            <select value={role} onChange={(e) => setRole(e.target.value)} className="p-2 border w-full">
                {roles.map((r) => (
                    <option key={r}>{r}</option>
                ))}
            </select>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Add User</button>
        </form>
    );
};

export default UserForm;
