const mongoose = require('mongoose');

const eventSchema = new mongoose.Schema({
    sessionId: {
        type: String,
        required: true,
        index: true
    },
    eventName: {
        type: String,
        required: true
    },
    timestamp: {
        type: Date,
        required: true,
        default: Date.now
    },
    metadata: {
        type: Map,
        of: mongoose.Schema.Types.Mixed,
        default: {}
    },
    journeyStage: {
        type: String,
        enum: ['Awareness', 'Consideration', 'Decision', 'Unknown'],
        default: 'Unknown'
    },
    confidence: {
        type: Number,
        default: 0
    }
}, {
    timestamps: true
});

// Index for efficient querying
eventSchema.index({ sessionId: 1, timestamp: 1 });

module.exports = mongoose.model('Event', eventSchema); 