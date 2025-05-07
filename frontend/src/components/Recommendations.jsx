import React, { useState, useEffect } from 'react';

const Recommendations = ({ customerId, stage, confidence, events }) => {
    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchRecommendations = async () => {
            if (!customerId || !stage) return;
            
            setLoading(true);
            setError(null);
            
            try {
                const response = await fetch('http://localhost:8000/api/recommendations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        customer_id: customerId,
                        stage,
                        confidence,
                        events
                    }),
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to fetch recommendations');
                }

                setRecommendations(data.data.recommendations);
            } catch (err) {
                console.error('Recommendation error:', err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchRecommendations();
    }, [customerId, stage, confidence, events]);

    if (loading) {
        return (
            <div className="p-6 bg-white rounded-lg shadow">
                <h2 className="text-2xl font-bold mb-4">Business Recommendations</h2>
                <div className="flex flex-col items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
                    <p className="text-gray-600">Analyzing customer journey...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 bg-red-50 rounded-lg shadow">
                <h2 className="text-2xl font-bold mb-4 text-red-700">Business Recommendations</h2>
                <div className="flex items-center space-x-2 text-red-600">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                        <p className="font-semibold">Error Loading Recommendations</p>
                        <p className="text-sm mt-1">{error}</p>
                    </div>
                </div>
            </div>
        );
    }

    if (!recommendations) {
        return null;
    }

    return (
        <div className="p-6 bg-white rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-4">Business Recommendations</h2>
            <div className="prose max-w-none">
                {recommendations.split('\n').map((line, index) => {
                    // Check if line is a section header
                    if (line.match(/^\d+\./)) {
                        return (
                            <h3 key={index} className="text-lg font-semibold mt-4 mb-2 text-blue-600">
                                {line}
                            </h3>
                        );
                    }
                    // Regular paragraph
                    return (
                        <p key={index} className="mb-2 text-gray-700">
                            {line}
                        </p>
                    );
                })}
            </div>
        </div>
    );
};

export default Recommendations; 