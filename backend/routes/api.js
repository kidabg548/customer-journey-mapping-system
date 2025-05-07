const express = require('express');
const router = express.Router();
const { predict_journey_stage } = require('../predict');
const Event = require('../database/models/Event');
const rateLimit = require('express-rate-limit');

// Rate limiting middleware
const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});

// Middleware to validate API key
const validateApiKey = (req, res, next) => {
    const apiKey = req.headers['x-api-key'];
    if (!apiKey || apiKey !== process.env.API_KEY) {
        return res.status(401).json({ error: 'Invalid API key' });
    }
    next();
};

// Track user event
router.post('/track', validateApiKey, apiLimiter, async (req, res) => {
    try {
        const { sessionId, eventName, metadata } = req.body;

        if (!sessionId || !eventName) {
            return res.status(400).json({
                success: false,
                error: 'sessionId and eventName are required'
            });
        }

        // Create event
        const event = new Event({
            sessionId,
            eventName,
            metadata,
            timestamp: new Date()
        });

        await event.save();

        // Get prediction for the session
        const prediction = await predict_journey_stage(sessionId);

        // Update event with prediction
        await Event.findByIdAndUpdate(event._id, {
            journeyStage: prediction.stage,
            confidence: prediction.confidence
        });

        res.status(201).json({
            success: true,
            data: {
                event: event.toObject(),
                prediction
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get journey stage for a session
router.get('/journey/:sessionId', validateApiKey, apiLimiter, async (req, res) => {
    try {
        const { sessionId } = req.params;
        const prediction = await predict_journey_stage(sessionId);
        
        res.json({
            success: true,
            data: prediction
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Get analytics for a date range
router.get('/analytics', validateApiKey, apiLimiter, async (req, res) => {
    try {
        const { startDate, endDate } = req.query;
        
        const query = {};
        if (startDate && endDate) {
            query.timestamp = {
                $gte: new Date(startDate),
                $lte: new Date(endDate)
            };
        }

        const analytics = await Event.aggregate([
            { $match: query },
            {
                $group: {
                    _id: '$journeyStage',
                    count: { $sum: 1 },
                    avgConfidence: { $avg: '$confidence' }
                }
            }
        ]);

        res.json({
            success: true,
            data: analytics
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

module.exports = router; 