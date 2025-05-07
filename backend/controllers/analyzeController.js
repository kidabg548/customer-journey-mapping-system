const Event = require('../database/models/Event');

// Map events to journey stages
function mapToStage(events) {
  const eventTypes = events.map(e => e.eventType);

  if (eventTypes.includes('purchase')) return 'Purchase';
  if (eventTypes.includes('add_to_cart') || eventTypes.includes('cta_click')) return 'Intent';
  if (eventTypes.includes('product_view')) return 'Consideration';
  if (eventTypes.includes('page_view')) return 'Awareness';

  return 'Unknown';
}

// GET /api/journey/:userId
exports.getJourneyStage = async (req, res) => {
  try {
    const { userId } = req.params;
    const events = await Event.find({ userId });

    const stage = mapToStage(events);

    res.status(200).json({ userId, stage });
  } catch (error) {
    res.status(500).json({ message: 'Failed to analyze journey', error });
  }
};
