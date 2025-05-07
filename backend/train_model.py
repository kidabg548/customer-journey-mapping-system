from ml.pipeline import JourneyStagePredictor
import os

def main():
    # Create model directory if it doesn't exist
    os.makedirs('ml-model', exist_ok=True)
    
    # Initialize predictor
    predictor = JourneyStagePredictor()
    
    # Train with synthetic data
    print("Training model with synthetic data...")
    predictor.train(use_synthetic=True)
    
    print("Model trained and saved successfully!")
    print("Model saved at: ml-model/journey_model.joblib")

if __name__ == "__main__":
    main()
