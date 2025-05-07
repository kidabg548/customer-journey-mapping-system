import requests
import json

def test_prediction_api():
    url = "http://localhost:8000/api/predict"
    
    # Sample events
    data = {
        "events": [
            {
                "eventName": "page_view",
                "timestamp": "2024-03-20T10:00:00",
                "metadata": {"page": "homepage"}
            },
            {
                "eventName": "product_view",
                "timestamp": "2024-03-20T10:05:00",
                "metadata": {"product_id": "123"}
            },
            {
                "eventName": "add_to_cart",
                "timestamp": "2024-03-20T10:10:00",
                "metadata": {"product_id": "123"}
            }
        ]
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        result = response.json()
        print("\nPrediction Results:")
        print(f"Predicted Stage: {result['stage']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print("\nStage Probabilities:")
        for stage, prob in result['probabilities'].items():
            print(f"{stage}: {prob:.2%}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding response: {e}")

if __name__ == "__main__":
    test_prediction_api() 