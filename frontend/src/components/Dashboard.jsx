import React, { useState, useEffect } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import axios from 'axios';
import './Dashboard.css';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

const API_BASE_URL = 'http://localhost:8000/api';

const Dashboard = () => {
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchAnalytics();
    }, []);

    const fetchAnalytics = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/analytics`);
            if (response.data.success) {
                setAnalytics(response.data.data);
            } else {
                setError('Failed to fetch analytics data');
            }
            setLoading(false);
        } catch (err) {
            setError('Failed to fetch analytics data');
            setLoading(false);
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!analytics || !Array.isArray(analytics)) return <div>No data available</div>;

    const stageDistributionData = {
        labels: analytics.map(item => item.stage),
        datasets: [
            {
                label: 'Number of Customers',
                data: analytics.map(item => item.count),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                ],
            },
        ],
    };

    return (
        <div className="dashboard">
            <h1 className="dashboard-title">Customer Journey Analytics</h1>
            
            <div className="grid">
                {/* Stage Distribution */}
                <div className="card">
                    <h2 className="card-title">Customer Distribution by Stage</h2>
                    <div className="chart-container">
                        <Pie data={stageDistributionData} options={{ maintainAspectRatio: false }} />
                    </div>
                </div>

                {/* Stage Details */}
                <div className="card">
                    <h2 className="card-title">Stage Details</h2>
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Stage</th>
                                    <th>Count</th>
                                    <th>Avg Confidence</th>
                                </tr>
                            </thead>
                            <tbody>
                                {analytics.map((item, index) => (
                                    <tr key={index}>
                                        <td>{item.stage}</td>
                                        <td>{item.count}</td>
                                        <td>{(item.avgConfidence * 100).toFixed(1)}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard; 