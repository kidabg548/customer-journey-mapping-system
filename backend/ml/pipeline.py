import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
from typing import List, Dict, Any
import json
import os

class JourneyStagePredictor:
    def __init__(self, model_path: str = 'ml-model/journey_model.joblib'):
        self.model_path = model_path
        self.model = None
        self.label_encoder = LabelEncoder()
        self.event_vocabulary = {}
        self.stages = ['Awareness', 'Consideration', 'Decision', 'Loyalty']
        
    def _extract_features(self, events: List[Dict[str, Any]]) -> np.ndarray:
        """Convert event sequence to feature vector."""
        features = []
        
        # Event frequency features
        event_counts = {}
        for event in events:
            event_name = event['eventName']
            event_counts[event_name] = event_counts.get(event_name, 0) + 1
            
        # Convert to feature vector using vocabulary
        feature_vector = np.zeros(len(self.event_vocabulary))
        for event_name, count in event_counts.items():
            if event_name in self.event_vocabulary:
                idx = self.event_vocabulary[event_name]
                feature_vector[idx] = count
                
        return feature_vector

    def _generate_synthetic_data(self, n_samples: int = 1000) -> tuple:
        """Generate synthetic training data with balanced stage distribution."""
        events = [
            'page_view', 'product_view', 'add_to_cart', 'checkout_start',
            'purchase', 'signup', 'login', 'search', 'filter', 'review_view'
        ]
        
        X = []
        y = []
        
        # Generate equal number of samples for each stage
        samples_per_stage = n_samples // 3  # For Awareness, Consideration, Decision
        
        # Generate Awareness stage samples
        for _ in range(samples_per_stage):
            n_events = np.random.randint(1, 4)
            session_events = []
            
            # Always include page_view for Awareness
            session_events.append({
                'eventName': 'page_view',
                'timestamp': pd.Timestamp.now(),
                'metadata': {'page': np.random.choice(['homepage', 'about', 'features'])}
            })
            
            # Add random early-stage events
            for _ in range(n_events - 1):
                event = {
                    'eventName': np.random.choice(['page_view', 'search', 'filter']),
                    'timestamp': pd.Timestamp.now(),
                    'metadata': {}
                }
                session_events.append(event)
            
            X.append(self._extract_features(session_events))
            y.append('Awareness')
        
        # Generate Consideration stage samples
        for _ in range(samples_per_stage):
            n_events = np.random.randint(3, 6)
            session_events = []
            
            # Always include product_view for Consideration
            session_events.append({
                'eventName': 'product_view',
                'timestamp': pd.Timestamp.now(),
                'metadata': {'product_id': f'prod_{np.random.randint(100, 999)}'}
            })
            
            # Add random consideration-stage events
            for _ in range(n_events - 1):
                event = {
                    'eventName': np.random.choice(['product_view', 'review_view', 'filter', 'search']),
                    'timestamp': pd.Timestamp.now(),
                    'metadata': {}
                }
                session_events.append(event)
            
            X.append(self._extract_features(session_events))
            y.append('Consideration')
        
        # Generate Decision stage samples
        for _ in range(samples_per_stage):
            n_events = np.random.randint(4, 7)
            session_events = []
            
            # Must include add_to_cart or checkout_start for Decision
            session_events.append({
                'eventName': np.random.choice(['add_to_cart', 'checkout_start']),
                'timestamp': pd.Timestamp.now(),
                'metadata': {'product_id': f'prod_{np.random.randint(100, 999)}'}
            })
            
            # Add random decision-stage events
            for _ in range(n_events - 1):
                event = {
                    'eventName': np.random.choice(['add_to_cart', 'checkout_start', 'product_view', 'review_view']),
                    'timestamp': pd.Timestamp.now(),
                    'metadata': {}
                }
                session_events.append(event)
            
            X.append(self._extract_features(session_events))
            y.append('Decision')
        
        # Shuffle the data
        indices = np.random.permutation(len(X))
        return np.array(X)[indices], np.array(y)[indices]

    def train(self, events_data: List[Dict[str, Any]] = None, use_synthetic: bool = False):
        """Train the model using real or synthetic data."""
        # Initialize event vocabulary
        all_events = [
            'page_view', 'product_view', 'add_to_cart', 'checkout_start',
            'purchase', 'signup', 'login', 'search', 'filter', 'review_view'
        ]
        self.event_vocabulary = {event: idx for idx, event in enumerate(all_events)}
        
        if use_synthetic:
            X, y = self._generate_synthetic_data()
        else:
            # Process real data
            X = []
            y = []
            
            # Group events by customer_id
            customer_events = {}
            for event in events_data:
                customer_id = event['customer_id']
                if customer_id not in customer_events:
                    customer_events[customer_id] = []
                customer_events[customer_id].append(event)
            
            # Process each customer's events
            for customer_id, session_events in customer_events.items():
                X.append(self._extract_features(session_events))
                
                # Determine stage based on events
                event_names = [e['eventName'] for e in session_events]
                if 'checkout_start' in event_names or 'add_to_cart' in event_names:
                    stage = 'Decision'
                elif 'product_view' in event_names or 'review_view' in event_names:
                    stage = 'Consideration'
                else:
                    stage = 'Awareness'
                y.append(stage)
            
            X = np.array(X)
            y = np.array(y)

        # Fit label encoder
        self.label_encoder.fit(self.stages)
        y_encoded = self.label_encoder.transform(y)

        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y_encoded)

        # Save model and metadata
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'label_encoder': self.label_encoder,
            'event_vocabulary': self.event_vocabulary
        }, self.model_path)

    def load_model(self):
        """Load the trained model and metadata."""
        if os.path.exists(self.model_path):
            saved_data = joblib.load(self.model_path)
            self.model = saved_data['model']
            self.label_encoder = saved_data['label_encoder']
            self.event_vocabulary = saved_data['event_vocabulary']
            return True
        return False

    def predict(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict journey stage for a sequence of events."""
        if self.model is None:
            if not self.load_model():
                raise ValueError("Model not trained or loaded")

        features = self._extract_features(events)
        prediction = self.model.predict([features])[0]
        probabilities = self.model.predict_proba([features])[0]
        
        stage = self.label_encoder.inverse_transform([prediction])[0]
        confidence = float(probabilities[prediction])
        
        return {
            'stage': stage,
            'confidence': confidence,
            'probabilities': {
                stage: float(prob) for stage, prob in zip(self.stages, probabilities)
            }
        } 