import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Recommendations from './Recommendations';

const CustomerJourney = () => {
    const { customerId } = useParams();
    const [events, setEvents] = useState([]);
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch events
                const eventsResponse = await fetch(`http://localhost:8000/api/customers/${customerId}/events`);
                const eventsData = await eventsResponse.json();
                setEvents(eventsData.data.events);

                // Fetch predictions
                const predictionsResponse = await fetch(`http://localhost:8000/api/customers/${customerId}/predictions`);
                const predictionsData = await predictionsResponse.json();
                setPredictions(predictionsData.data.predictions);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [customerId]);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="container mx-auto px-4">
                    <div className="flex justify-center items-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="container mx-auto px-4">
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <div className="flex items-center space-x-2 text-red-600">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <p>Error: {error}</p>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!customerId) return <div>No customer ID provided</div>;
    if (!events?.length && !predictions?.length) return <div>No data available for this customer</div>;

    const latestPrediction = predictions[0] || null;

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="container mx-auto px-4">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Customer Journey</h1>
                    <p className="text-gray-600 mt-2">Customer ID: {customerId}</p>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column - Current Stage and Recommendations */}
                    <div className="lg:col-span-2 space-y-8">
                        {/* Current Stage */}
                        {latestPrediction && (
                            <div className="bg-white rounded-lg shadow p-6">
                                <h2 className="text-xl font-semibold mb-4">Current Stage</h2>
                                <div className="flex items-center space-x-4">
                                    <div className={`px-4 py-2 rounded-full ${
                                        latestPrediction.prediction.stage === 'Awareness' ? 'bg-blue-100 text-blue-800' :
                                        latestPrediction.prediction.stage === 'Consideration' ? 'bg-yellow-100 text-yellow-800' :
                                        latestPrediction.prediction.stage === 'Decision' ? 'bg-green-100 text-green-800' :
                                        'bg-purple-100 text-purple-800'
                                    }`}>
                                        {latestPrediction.prediction.stage}
                                    </div>
                                    <div className="text-gray-600">
                                        Confidence: {(latestPrediction.prediction.confidence * 100).toFixed(1)}%
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Recommendations */}
                        {latestPrediction && (
                            <Recommendations
                                customerId={customerId}
                                stage={latestPrediction.prediction.stage}
                                confidence={latestPrediction.prediction.confidence}
                                events={events.slice(0, 5)}
                            />
                        )}
                    </div>

                    {/* Right Column - Events and Predictions */}
                    <div className="space-y-8">
                        {/* Events Timeline */}
                        <div className="bg-white rounded-lg shadow p-6">
                            <h2 className="text-xl font-semibold mb-4">Recent Events</h2>
                            <div className="space-y-4">
                                {events.slice(0, 5).map((event, index) => (
                                    <div key={index} className="border-l-4 border-blue-500 pl-4">
                                        <p className="font-semibold text-gray-900">{event.eventName}</p>
                                        <p className="text-sm text-gray-600">
                                            {new Date(event.timestamp).toLocaleString()}
                                        </p>
                                        {event.metadata && (
                                            <div className="mt-2 text-sm text-gray-500">
                                                <pre className="whitespace-pre-wrap">
                                                    {JSON.stringify(event.metadata, null, 2)}
                                                </pre>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Predictions History */}
                        <div className="bg-white rounded-lg shadow p-6">
                            <h2 className="text-xl font-semibold mb-4">Stage History</h2>
                            <div className="space-y-4">
                                {predictions.map((prediction, index) => (
                                    <div key={index} className="border-l-4 border-gray-200 pl-4">
                                        <div className="flex items-center justify-between">
                                            <span className={`px-3 py-1 rounded-full text-sm ${
                                                prediction.prediction.stage === 'Awareness' ? 'bg-blue-100 text-blue-800' :
                                                prediction.prediction.stage === 'Consideration' ? 'bg-yellow-100 text-yellow-800' :
                                                prediction.prediction.stage === 'Decision' ? 'bg-green-100 text-green-800' :
                                                'bg-purple-100 text-purple-800'
                                            }`}>
                                                {prediction.prediction.stage}
                                            </span>
                                            <span className="text-sm text-gray-600">
                                                {(prediction.prediction.confidence * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-500 mt-1">
                                            {new Date(prediction.timestamp).toLocaleString()}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CustomerJourney; 