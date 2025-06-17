import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Layout from "../components/Layout";

const Dashboard = () => {
    const [user, setUser] = useState(null);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUser = async () => {
            const token = localStorage.getItem('token');
            if (!token) return navigate('/login');

            try {
                const response = await axios.get('https://api.lx-gateway.tech/protected', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setUser(response.data);
            } catch {
                setError('Session expired. Redirecting to login...');
                localStorage.removeItem('token');
                setTimeout(() => navigate('/'), 1500);
            }
        };
        fetchUser();
    }, [navigate]);

    return (
        <Layout>
        <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-r from-green-100 to-blue-200">
            <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md text-center">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">LX-FTA Sensor Dashboard</h2>

                {user ? (
                    <>
                        <p className="text-gray-600 mb-2">
                            <span className="font-semibold">Username:</span> {user.username}
                        </p>
                        <p className="text-gray-600 mb-4">
                            <span className="font-semibold">Role:</span> {user.role}
                        </p>
                        <button
                            onClick={() => {
                                localStorage.removeItem('token');
                                navigate('/');
                            }}
                            className="mt-4 bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded transition"
                        >
                            Logout
                        </button>
                    </>
                ) : (
                    <p className="text-blue-600 font-medium">{error || 'Loading user data...'}</p>
                )}
            </div>
        </div>
        </Layout>
    );
};

export default Dashboard;
