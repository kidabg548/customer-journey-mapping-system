const express = require('express');
const router = express.Router();
const { logEvent, getEvents } = require('../controllers/eventController');

// Log an event
router.post('/', logEvent);

// Get all or user-specific events
router.get('/', getEvents);

module.exports = router;
