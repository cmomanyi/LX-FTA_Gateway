import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const res = await fetch("http://localhost:8000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            const data = await res.json();

            if (!res.ok) {
                toast.error(data.detail || "Login failed");
                setLoading(false);
                return;
            }

            // Save token and decode role (extracted from backend's known users for simplicity)
            localStorage.setItem("token", data.access_token);

            // Manual role assignment based on username (can be improved with jwt-decode)
            let role = "guest";
            if (username === "admin") role = "admin";
            else if (username === "analyst") role = "analyst";
            else if (username === "sensor") role = "sensor";

            localStorage.setItem("role", role);

            toast.success("Login successful");

            // Redirect based on role
            if (role === "admin") {
                navigate("/admin");
            } else {
                navigate("/dashboard"); // or another route
            }
        } catch (err) {
            toast.error("Network error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="bg-white p-8 rounded shadow-lg w-full max-w-sm space-y-4">
                <h2 className="text-xl font-bold text-center">Admin Login</h2>

                <form onSubmit={handleLogin} className="space-y-4">
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Username"
                        className="w-full p-2 border rounded"
                        required
                    />
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Password"
                        className="w-full p-2 border rounded"
                        required
                    />
                    <button
                        type="submit"
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white p-2 rounded"
                        disabled={loading}
                    >
                        {loading ? "Logging in..." : "Login"}
                    </button>
                </form>
                <ToastContainer position="bottom-right" autoClose={3000} />
            </div>
        </div>
    );
};

export default Login;
