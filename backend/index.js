require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const eventRoutes = require('./routes/eventRoutes');
const startJourneyAutomation = require('./jobs/actionJob');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.send('AI Customer Journey Mapping API is running.');
});

// Routes
app.use('/api/v1', eventRoutes);

// Start automation
startJourneyAutomation();

const PORT = process.env.PORT || 5000;

// MongoDB connection options
const mongoOptions = {
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
  family: 4 // Use IPv4, skip trying IPv6
};

// MongoDB connection with retry logic
const connectWithRetry = async () => {
  const MONGODB_URI = process.env.MONGO_URI;
  
  if (!MONGODB_URI) {
    console.error('❌ MONGO_URI is not defined in environment variables');
    process.exit(1);
  }

  try {
    await mongoose.connect(MONGODB_URI, mongoOptions);
    console.log('✅ Connected to MongoDB');
    
    // Start the server only after successful database connection
    app.listen(PORT, () => {
      console.log(`🚀 Server running on http://localhost:${PORT}`);
    });
  } catch (err) {
    console.error('❌ MongoDB connection error:', err.message);
    console.log('🔄 Retrying connection in 5 seconds...');
    setTimeout(connectWithRetry, 5000);
  }
};

// Initial connection attempt
connectWithRetry();
