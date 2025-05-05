const Event = require('../database/eventModel');

// POST /api/events
exports.logEvent = async (req, res) => {
  try {
    const { userId, eventType, metadata } = req.body;

    if (!userId || !eventType) {
      return res.status(400).json({ message: 'userId and eventType are required' });
    }

    const newEvent = new Event({ userId, eventType, metadata });
    await newEvent.save();

    res.status(201).json({ message: 'Event logged successfully', event: newEvent });
  } catch (error) {
    res.status(500).json({ message: 'Failed to log event', error });
  }
};

// GET /api/events?userId=123
exports.getEvents = async (req, res) => {
  try {
    const { userId } = req.query;
    const query = userId ? { userId } : {};

    const events = await Event.find(query).sort({ timestamp: -1 });
    res.status(200).json(events);
  } catch (error) {
    res.status(500).json({ message: 'Failed to fetch events', error });
  }
};
