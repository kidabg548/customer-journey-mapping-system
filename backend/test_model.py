from ml.pipeline import JourneyStagePredictor

def test_prediction():
    # Initialize predictor
    predictor = JourneyStagePredictor()
    
    # Sample events for a customer session
    sample_events = [
        {
            'eventName': 'page_view',
            'timestamp': '2024-03-20T10:00:00',
            'metadata': {'page': 'homepage'}
        },
        {
            'eventName': 'product_view',
            'timestamp': '2024-03-20T10:05:00',
            'metadata': {'product_id': '123'}
        },
        {
            'eventName': 'add_to_cart',
            'timestamp': '2024-03-20T10:10:00',
            'metadata': {'product_id': '123'}
        }
    ]
    
    # Make prediction
    prediction = predictor.predict(sample_events)
    
    print("\nPrediction Results:")
    print(f"Predicted Stage: {prediction['stage']}")
    print(f"Confidence: {prediction['confidence']:.2%}")
    print("\nStage Probabilities:")
    for stage, prob in prediction['probabilities'].items():
        print(f"{stage}: {prob:.2%}")

if __name__ == "__main__":
    test_prediction() 