// src/components/UserTable.jsx
import React from "react";

const roles = ["Admin", "User", "Moderator"];

const UserTable = ({ users, onDelete, onChangeRole }) => {
    return (
        <table className="w-full border table-fixed">
            <thead>
            <tr className="bg-gray-200">
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Actions</th>
            </tr>
            </thead>
            <tbody>
            {users.map((user) => (
                <tr key={user.id} className="border-t">
                    <td>{user.name}</td>
                    <td>{user.email}</td>
                    <td>
                        <select
                            value={user.role}
                            onChange={(e) => onChangeRole(user.id, e.target.value)}
                            className="p-1 border"
                        >
                            {roles.map((r) => (
                                <option key={r}>{r}</option>
                            ))}
                        </select>
                    </td>
                    <td>
                        <button onClick={() => onDelete(user.id)} className="text-red-600">Delete</button>
                    </td>
                </tr>
            ))}
            </tbody>
        </table>
    );
};

export default UserTable;
