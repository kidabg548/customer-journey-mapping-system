const mongoose = require('mongoose');

const eventSchema = new mongoose.Schema({
  userId: { type: String, required: true },
  eventType: { type: String, required: true }, // e.g., 'page_view', 'button_click'
  metadata: { type: Object }, // optional data like page, button ID, etc.
  timestamp: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Event', eventSchema);
