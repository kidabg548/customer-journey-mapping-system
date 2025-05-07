const cron = require('node-cron');
const Event = require('../database/models/Event');
const { mapToStage } = require('../controllers/analyzeController'); // Reuse this logic

// Simulated action sender
function triggerAction(userId, stage) {
  console.log(`[AI ACTION] User ${userId} is in stage "${stage}"`);

  // Simulated responses (replace with email logic later)
  switch (stage) {
    case 'Awareness':
      console.log(`→ Send welcome email to ${userId}`);
      break;
    case 'Consideration':
      console.log(`→ Send FAQ/helpful links to ${userId}`);
      break;
    case 'Intent':
      console.log(`→ Offer discount to ${userId}`);
      break;
    case 'Purchase':
      console.log(`→ Send thank-you email to ${userId}`);
      break;
  }
}

// Run every 1 minute (adjust as needed)
const startJourneyAutomation = () => {
  cron.schedule('* * * * *', async () => {
    console.log('[AI Automation] Checking user stages...');
    const users = await Event.distinct('userId');

    for (const userId of users) {
      const events = await Event.find({ userId });
      const stage = mapToStage(events);

      triggerAction(userId, stage);
    }
  });
};

module.exports = startJourneyAutomation;
