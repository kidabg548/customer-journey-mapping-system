from datetime import datetime, timedelta
import random
from database import store_event, store_prediction
from ml.pipeline import JourneyStagePredictor
import json

def generate_training_events(n_samples=100):
    """Generate synthetic training events and store them in MongoDB."""
    events = []
    customer_ids = [f"customer_{i:03d}" for i in range(n_samples)]
    
    # Event types and their probabilities for each stage
    awareness_events = ['page_view', 'search', 'filter']
    consideration_events = ['product_view', 'review_view', 'filter', 'search']
    decision_events = ['add_to_cart', 'checkout_start', 'product_view', 'review_view']
    
    # Generate events for each customer
    for customer_id in customer_ids:
        # Randomly assign a stage
        stage = random.choice(['Awareness', 'Consideration', 'Decision'])
        
        # Generate 3-7 events for each customer
        n_events = random.randint(3, 7)
        customer_events = []
        
        # Generate events based on stage
        for i in range(n_events):
            if stage == 'Awareness':
                event_name = random.choice(awareness_events)
            elif stage == 'Consideration':
                event_name = random.choice(consideration_events)
            else:  # Decision
                event_name = random.choice(decision_events)
            
            # Create event
            event = {
                'eventName': event_name,
                'timestamp': (datetime.utcnow() - timedelta(minutes=random.randint(0, 60))).isoformat(),
                'metadata': {
                    'page': random.choice(['homepage', 'product', 'cart', 'checkout']),
                    'source': random.choice(['direct', 'search', 'referral'])
                },
                'customer_id': customer_id,
                'user_email': f"user_{customer_id}@example.com",
                'user_name': f"User {customer_id}"
            }
            
            # Store event in MongoDB
            event_id = store_event(event)
            customer_events.append(event)
            
            print(f"Stored event {i+1}/{n_events} for customer {customer_id}")
        
        # Make prediction for the customer's events
        predictor = JourneyStagePredictor()
        prediction = predictor.predict(customer_events)
        
        # Store prediction
        prediction_id = store_prediction(
            customer_id,
            customer_events,
            prediction
        )
        
        print(f"Stored prediction for customer {customer_id}")
        events.extend(customer_events)
    
    return events

if __name__ == "__main__":
    print("Generating training data...")
    events = generate_training_events(100)
    print(f"Generated and stored {len(events)} events")
    
    # Train the model with the generated data
    print("\nTraining model with generated data...")
    predictor = JourneyStagePredictor()
    predictor.train(events_data=events, use_synthetic=False)
    print("Model training completed!") 