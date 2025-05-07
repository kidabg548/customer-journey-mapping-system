import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI')
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set")

DB_NAME = os.getenv('MONGODB_DB', 'customer-journey')
COLLECTION_NAME = 'events'  # Explicitly set collection name

# Sample event types and their corresponding journey stages
EVENT_TYPES = {
    'page_view': 'Awareness',
    'product_view': 'Consideration',
    'add_to_cart': 'Intent',
    'purchase': 'Purchase'
}

# Sample metadata for different event types
METADATA_TEMPLATES = {
    'page_view': {
        'pageType': ['home', 'category', 'product', 'about'],
        'referrer': ['google', 'direct', 'social', 'email']
    },
    'product_view': {
        'productId': lambda: f'PROD{random.randint(1000, 9999)}',
        'category': ['electronics', 'clothing', 'books', 'home']
    },
    'add_to_cart': {
        'productId': lambda: f'PROD{random.randint(1000, 9999)}',
        'quantity': lambda: random.randint(1, 5),
        'price': lambda: round(random.uniform(10.0, 200.0), 2)
    },
    'purchase': {
        'orderId': lambda: f'ORD{random.randint(10000, 99999)}',
        'totalAmount': lambda: round(random.uniform(50.0, 500.0), 2),
        'paymentMethod': ['credit_card', 'paypal', 'bank_transfer']
    }
}

def generate_metadata(event_type):
    """Generate random metadata for an event type"""
    template = METADATA_TEMPLATES.get(event_type, {})
    metadata = {}
    
    for key, value in template.items():
        if callable(value):
            metadata[key] = value()
        elif isinstance(value, list):
            metadata[key] = random.choice(value)
        else:
            metadata[key] = value
    
    return metadata

def create_sample_session(num_events=5):
    """Create a sample session with multiple events"""
    session_id = f'SESS{random.randint(10000, 99999)}'
    events = []
    base_time = datetime.now() - timedelta(days=random.randint(0, 30))
    
    # Generate a sequence of events
    event_sequence = random.sample(list(EVENT_TYPES.keys()), min(num_events, len(EVENT_TYPES)))
    
    for i, event_type in enumerate(event_sequence):
        timestamp = base_time + timedelta(minutes=i * random.randint(5, 30))
        event = {
            'sessionId': session_id,
            'eventName': event_type,
            'timestamp': timestamp,
            'metadata': generate_metadata(event_type),
            'journeyStage': EVENT_TYPES[event_type],
            'confidence': round(random.uniform(0.7, 1.0), 2)
        }
        events.append(event)
    
    return events

def add_training_data(num_sessions=100):
    """Add training data to the database"""
    try:
        # Connect to MongoDB
        print("Connecting to MongoDB...")
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        events_collection = db[COLLECTION_NAME]
        
        # Verify connection and list all collections
        print(f"Connected to database: {DB_NAME}")
        print(f"Available collections: {db.list_collection_names()}")
        print(f"Using collection: {COLLECTION_NAME}")
        
        # Generate and insert sample sessions
        total_events = 0
        for i in range(num_sessions):
            session_events = create_sample_session()
            try:
                result = events_collection.insert_many(session_events)
                total_events += len(session_events)
                print(f"Session {i+1}/{num_sessions}: Inserted {len(session_events)} events for session {session_events[0]['sessionId']}")
            except Exception as insert_error:
                print(f"Error inserting session {i+1}: {str(insert_error)}")
                continue
        
        # Verify data was inserted
        count = events_collection.count_documents({})
        print(f"\nVerification:")
        print(f"Total documents in collection: {count}")
        print(f"Expected documents: {total_events}")
        
        if count > 0:
            # Show a sample document
            sample = events_collection.find_one()
            print("\nSample document structure:")
            print(f"Keys: {list(sample.keys())}")
            print("\nSample document content:")
            for key, value in sample.items():
                if key != '_id':  # Skip MongoDB's internal _id field
                    print(f"{key}: {value}")
        
        print(f"\nSuccessfully added {total_events} events from {num_sessions} sessions")
        
    except Exception as e:
        print(f"Error adding training data: {str(e)}")
    finally:
        client.close()

if __name__ == '__main__':
    # Add 100 sample sessions to the database
    add_training_data(100) 