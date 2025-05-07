import sys
import json
from ml.pipeline import JourneyStagePredictor

def predict_journey_stage(session_id: str) -> dict:
    """Predict journey stage for a session."""
    try:
        # Initialize predictor
        predictor = JourneyStagePredictor()
        
        # Load model
        if not predictor.load_model():
            return {
                'stage': 'Unknown',
                'confidence': 0.0,
                'error': 'Model not found'
            }
        
        # Get session events from MongoDB
        from pymongo import MongoClient
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/customer-journey')
        DB_NAME = os.getenv('MONGODB_DB', 'customer-journey')
        
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        # Get events for the session
        events = list(db.events.find({'sessionId': session_id}).sort('timestamp', 1))
        
        if not events:
            return {
                'stage': 'Unknown',
                'confidence': 0.0,
                'error': 'No events found for session'
            }
        
        # Convert events to the format expected by the predictor
        formatted_events = [
            {
                'eventName': event['eventName'],
                'timestamp': event['timestamp'],
                'metadata': event.get('metadata', {})
            }
            for event in events
        ]
        
        # Make prediction
        prediction = predictor.predict(formatted_events)
        
        return prediction
        
    except Exception as e:
        return {
            'stage': 'Unknown',
            'confidence': 0.0,
            'error': str(e)
        }

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(json.dumps({
            'stage': 'Unknown',
            'confidence': 0.0,
            'error': 'Session ID required'
        }))
        sys.exit(1)
    
    session_id = sys.argv[1]
    result = predict_journey_stage(session_id)
    print(json.dumps(result))
