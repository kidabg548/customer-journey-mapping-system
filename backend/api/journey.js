const express = require('express');
const router = express.Router();
const { getJourneyStage } = require('../controllers/analyzeController');

router.get('/:userId', getJourneyStage);

module.exports = router;
