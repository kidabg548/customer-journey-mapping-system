const Event = require('../database/models/Event');
const { spawn } = require('child_process');
const path = require('path');

class EventController {
    constructor() {
        // Bind methods to ensure 'this' context is preserved
        this.createEvent = this.createEvent.bind(this);
        this.getSessionEvents = this.getSessionEvents.bind(this);
        this.getAnalytics = this.getAnalytics.bind(this);
        this.getRecentEvents = this.getRecentEvents.bind(this);
        this.triggerPrediction = this.triggerPrediction.bind(this);
    }

    // Create a new event
    async createEvent(req, res) {
        try {
            const { sessionId, eventName, metadata } = req.body;
            
            const event = new Event({
                sessionId,
                eventName,
                metadata
            });

            await event.save();

            // Wait for prediction and update event
            const prediction = await this.triggerPrediction(sessionId);
            if (prediction && prediction.stage) {
                await Event.findOneAndUpdate(
                    { sessionId },
                    { journeyStage: prediction.stage, confidence: prediction.confidence },
                    { sort: { timestamp: -1 } }
                );
            }

            res.status(201).json({
                success: true,
                data: { ...event.toObject(), prediction }
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                error: error.message
            });
        }
    }

    // Get events for a session
    async getSessionEvents(req, res) {
        try {
            const { sessionId } = req.params;
            const events = await Event.find({ sessionId })
                .sort({ timestamp: 1 });

            res.status(200).json({
                success: true,
                data: events
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                error: error.message
            });
        }
    }

    // Trigger prediction for a session
    async triggerPrediction(sessionId) {
        return new Promise((resolve, reject) => {
            try {
                const pythonProcess = spawn('python', [
                    path.join(__dirname, '../predict.py'),
                    sessionId
                ]);
                let result = '';
                let error = '';
                pythonProcess.stdout.on('data', (data) => { result += data.toString(); });
                pythonProcess.stderr.on('data', (data) => { error += data.toString(); });
                pythonProcess.on('close', () => {
                    if (error) {
                        console.error(`Prediction error: ${error}`);
                        resolve({ stage: 'Unknown', confidence: 0.0, error });
                    } else {
                        try {
                            resolve(JSON.parse(result));
                        } catch (e) {
                            resolve({ stage: 'Unknown', confidence: 0.0, error: 'Invalid JSON from Python' });
                        }
                    }
                });
            } catch (err) {
                console.error('Prediction error:', err);
                resolve({ stage: 'Unknown', confidence: 0.0, error: err.message });
            }
        });
    }

    // Get recent events
    async getRecentEvents(req, res) {
        try {
            const events = await Event.find()
                .sort({ timestamp: -1 })
                .limit(10);

            res.status(200).json({
                success: true,
                data: events
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                error: error.message
            });
        }
    }

    // Get analytics data
    async getAnalytics(req, res) {
        try {
            const analytics = await Event.aggregate([
                {
                    $group: {
                        _id: '$journeyStage',
                        count: { $sum: 1 },
                        avgConfidence: { $avg: '$confidence' }
                    }
                }
            ]);

            res.status(200).json({
                success: true,
                data: analytics
            });
        } catch (error) {
            res.status(400).json({
                success: false,
                error: error.message
            });
        }
    }
}

module.exports = new EventController();
