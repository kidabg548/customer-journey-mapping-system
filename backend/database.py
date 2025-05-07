from pymongo import MongoClient
from datetime import datetime
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['customer_journey']

# Collections
events_collection = db['events']
predictions_collection = db['predictions']
analytics_collection = db['analytics']

def check_database_state():
    """Check the state of the database collections."""
    try:
        events_count = events_collection.count_documents({})
        predictions_count = predictions_collection.count_documents({})
        print(f"Database state - Events: {events_count}, Predictions: {predictions_count}")
        
        # Check a sample prediction document
        sample_prediction = predictions_collection.find_one()
        if sample_prediction:
            print(f"Sample prediction structure: {sample_prediction}")
        else:
            print("No predictions found in database")
    except Exception as e:
        print(f"Error checking database state: {str(e)}")
        raise

def store_event(event: Dict[str, Any]) -> str:
    """Store a customer event in the database."""
    # Ensure required fields are present
    required_fields = ['eventName', 'timestamp', 'metadata', 'customer_id', 'user_email']
    for field in required_fields:
        if field not in event:
            raise ValueError(f"Missing required field: {field}")

    # Convert timestamp to datetime if it's a string
    if isinstance(event['timestamp'], str):
        event['timestamp'] = datetime.fromisoformat(event['timestamp'])
    
    # Add created_at timestamp
    event['created_at'] = datetime.utcnow()
    
    # Store the event
    result = events_collection.insert_one(event)
    return str(result.inserted_id)

def store_prediction(customer_id: str, events: List[Dict[str, Any]], prediction: Dict[str, Any]) -> str:
    """Store a journey stage prediction."""
    prediction_doc = {
        'customer_id': customer_id,
        'events': events,
        'prediction': prediction,
        'timestamp': datetime.utcnow()
    }
    result = predictions_collection.insert_one(prediction_doc)
    return str(result.inserted_id)

def get_customer_events(customer_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve events for a specific customer."""
    return list(events_collection.find(
        {'customer_id': customer_id},
        {'_id': 0}
    ).sort('timestamp', -1).limit(limit))

def get_customer_predictions(customer_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve predictions for a specific customer."""
    return list(predictions_collection.find(
        {'customer_id': customer_id},
        {'_id': 0}
    ).sort('timestamp', -1).limit(limit))

def get_stage_distribution() -> Dict[str, Dict[str, Any]]:
    """Get distribution of customers across journey stages."""
    pipeline = [
        {
            '$group': {
                '_id': '$prediction.stage',
                'count': {'$sum': 1},
                'avgConfidence': {'$avg': '$prediction.confidence'}
            }
        }
    ]
    
    results = list(predictions_collection.aggregate(pipeline))
    return {doc['_id']: {'count': doc['count'], 'avgConfidence': doc['avgConfidence']} for doc in results}

def get_stage_transitions() -> List[Dict[str, Any]]:
    """Get stage transition patterns."""
    pipeline = [
        {
            '$sort': {'customer_id': 1, 'timestamp': 1}
        },
        {
            '$group': {
                '_id': '$customer_id',
                'stages': {'$push': '$prediction.stage'}
            }
        },
        {
            '$project': {
                'transitions': {
                    '$reduce': {
                        'input': {'$slice': ['$stages', 1, {'$subtract': [{'$size': '$stages'}, 1]}]},
                        'initialValue': [],
                        'in': {
                            '$concatArrays': [
                                '$$value',
                                [{
                                    'from': {'$arrayElemAt': ['$stages', {'$indexOfArray': ['$stages', '$$this']}]},
                                    'to': {'$arrayElemAt': ['$stages', {'$add': [{'$indexOfArray': ['$stages', '$$this']}, 1]}]}
                                }]
                            ]
                        }
                    }
                }
            }
        }
    ]
    
    return list(predictions_collection.aggregate(pipeline))

def get_time_in_stages() -> Dict[str, float]:
    """Get average time spent in each stage."""
    pipeline = [
        {
            '$sort': {'customer_id': 1, 'timestamp': 1}
        },
        {
            '$group': {
                '_id': '$customer_id',
                'stages': {'$push': {'stage': '$prediction.stage', 'timestamp': '$timestamp'}}
            }
        },
        {
            '$project': {
                'stage_times': {
                    '$reduce': {
                        'input': {'$slice': ['$stages', 1, {'$subtract': [{'$size': '$stages'}, 1]}]},
                        'initialValue': [],
                        'in': {
                            '$concatArrays': [
                                '$$value',
                                [{
                                    'stage': '$$this.stage',
                                    'duration': {
                                        '$divide': [
                                            {'$subtract': [
                                                {'$arrayElemAt': ['$stages.timestamp', {'$add': [{'$indexOfArray': ['$stages', '$$this']}, 1]}]},
                                                '$$this.timestamp'
                                            ]},
                                            3600000  # Convert to hours
                                        ]
                                    }
                                }]
                            ]
                        }
                    }
                }
            }
        },
        {
            '$unwind': '$stage_times'
        },
        {
            '$group': {
                '_id': '$stage_times.stage',
                'avgTime': {'$avg': '$stage_times.duration'}
            }
        }
    ]
    
    results = list(predictions_collection.aggregate(pipeline))
    return {doc['_id']: doc['avgTime'] for doc in results}

def insert_sample_data():
    """Insert sample data for testing."""
    try:
        # Sample predictions data
        sample_predictions = [
            {
                'customer_id': 'cust_001',
                'prediction': {
                    'stage': 'Awareness',
                    'confidence': 0.85
                },
                'timestamp': datetime.utcnow()
            },
            {
                'customer_id': 'cust_002',
                'prediction': {
                    'stage': 'Consideration',
                    'confidence': 0.75
                },
                'timestamp': datetime.utcnow()
            },
            {
                'customer_id': 'cust_003',
                'prediction': {
                    'stage': 'Decision',
                    'confidence': 0.90
                },
                'timestamp': datetime.utcnow()
            },
            {
                'customer_id': 'cust_004',
                'prediction': {
                    'stage': 'Awareness',
                    'confidence': 0.80
                },
                'timestamp': datetime.utcnow()
            },
            {
                'customer_id': 'cust_005',
                'prediction': {
                    'stage': 'Consideration',
                    'confidence': 0.70
                },
                'timestamp': datetime.utcnow()
            }
        ]
        
        # Insert sample predictions
        predictions_collection.insert_many(sample_predictions)
        print("Sample data inserted successfully!")
        
    except Exception as e:
        print(f"Error inserting sample data: {str(e)}")
        raise

# Add this to the top of the file after the collections are defined
check_database_state()

# Add this after check_database_state()
insert_sample_data() 