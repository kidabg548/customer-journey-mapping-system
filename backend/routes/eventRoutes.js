const express = require('express');
const router = express.Router();
const eventController = require('../controllers/eventController');

// Create a new event
router.post('/events', eventController.createEvent);

// Get events for a specific session
router.get('/events/session/:sessionId', eventController.getSessionEvents);

// Get analytics data
router.get('/analytics', eventController.getAnalytics);

// Get recent events
router.get('/events/recent', eventController.getRecentEvents);

module.exports = router; 