from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from ml.pipeline import JourneyStagePredictor
from database import (
    store_event, store_prediction, get_customer_events,
    get_customer_predictions, get_stage_distribution,
    get_stage_transitions, get_time_in_stages
)
from datetime import datetime
import json
from automation import AutomationService
import logging
import sys

# Configure logging to print to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True  # Force the configuration
)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add console handler if not already added
if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Print initial log to verify logging is working
logger.info("Starting FastAPI application...")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
predictor = JourneyStagePredictor()
automation_service = AutomationService()

class Event(BaseModel):
    eventName: str
    timestamp: str
    metadata: Dict[str, Any]
    customer_id: str
    user_email: EmailStr
    user_name: Optional[str] = None

class PredictionRequest(BaseModel):
    events: List[Event]

class AnalyticsResponse(BaseModel):
    success: bool = True
    data: List[Dict[str, Any]]

@app.post("/api/events")
async def create_event(event: Event):
    """Store a new customer event and make prediction."""
    try:
        print(f"\n=== Creating event for customer {event.customer_id} ===")  # Direct print
        logger.info(f"Creating event for customer {event.customer_id}")
        
        # Store the event
        event_id = store_event(event.model_dump())  # Using model_dump instead of dict
        print(f"Event stored with ID: {event_id}")  # Direct print
        logger.info(f"Event stored with ID: {event_id}")
        
        # Get all events for this customer
        customer_events = get_customer_events(event.customer_id)
        print(f"Retrieved {len(customer_events)} events for customer")  # Direct print
        logger.info(f"Retrieved {len(customer_events)} events for customer")
        
        # Make prediction using all customer events
        prediction = predictor.predict(customer_events)
        print(f"Prediction made: {prediction}")  # Direct print
        logger.info(f"Prediction made: {prediction}")
        
        # Store the prediction
        prediction_id = store_prediction(
            event.customer_id,
            customer_events,
            prediction
        )
        print(f"Prediction stored with ID: {prediction_id}")  # Direct print
        logger.info(f"Prediction stored with ID: {prediction_id}")

        # Always trigger automation with the user's email
        print(f"Triggering automation for {event.user_email}")  # Direct print
        logger.info(f"Triggering automation for {event.user_email}")
        automation_result = automation_service.trigger_stage_automation(
            customer_id=event.customer_id,
            stage=prediction['stage'],
            customer_email=event.user_email,
            customer_name=event.user_name
        )
        print(f"Automation result: {automation_result}")  # Direct print
        logger.info(f"Automation result: {automation_result}")
        
        return {
            "success": True,
            "data": {
                "event_id": event_id,
                "prediction": prediction,
                "prediction_id": prediction_id,
                "automation": automation_result
            }
        }
    except Exception as e:
        print(f"Error in create_event: {str(e)}")  # Direct print
        logger.error(f"Error in create_event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/trigger")
async def trigger_automation(customer_id: str, stage: str, customer_email: str, customer_name: Optional[str] = None):
    """Manually trigger automation for a customer."""
    try:
        result = automation_service.trigger_stage_automation(
            customer_id=customer_id,
            stage=stage,
            customer_email=customer_email,
            customer_name=customer_name
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict")
async def predict_journey_stage(request: PredictionRequest):
    """Predict journey stage and store the prediction."""
    try:
        # Convert Pydantic model to list of dicts
        events = [event.dict() for event in request.events]
        
        # Make prediction
        prediction = predictor.predict(events)
        
        # Store prediction if we have a customer_id
        if events and 'customer_id' in events[0]:
            prediction_id = store_prediction(
                events[0]['customer_id'],
                events,
                prediction
            )
            prediction['prediction_id'] = prediction_id
        
        return {"success": True, "data": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}/events")
async def get_events(customer_id: str, limit: int = 100):
    """Get events for a specific customer."""
    try:
        events = get_customer_events(customer_id, limit)
        return {"success": True, "data": {"events": events}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}/predictions")
async def get_predictions(customer_id: str, limit: int = 100):
    """Get predictions for a specific customer."""
    try:
        predictions = get_customer_predictions(customer_id, limit)
        return {"success": True, "data": {"predictions": predictions}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """Get journey analytics."""
    try:
        # Get stage distribution
        stage_distribution = get_stage_distribution()
        print(f"Stage distribution: {stage_distribution}")  # Debug log
        
        # Transform the data to match the frontend's expected format
        analytics_data = [
            {
                "stage": stage,
                "count": data['count'],
                "avgConfidence": data['avgConfidence']
            }
            for stage, data in stage_distribution.items()
        ]
        print(f"Analytics data: {analytics_data}")  # Debug log
        
        return {"success": True, "data": analytics_data}
    except Exception as e:
        print(f"Error in get_analytics: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test/events")
async def add_test_events():
    """Add test events for a customer."""
    try:
        # Sample events for testing
        test_events = [
            {
                "eventName": "page_view",
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "page": "homepage",
                    "source": "direct"
                },
                "customer_id": "test_customer_001"
            },
            {
                "eventName": "product_view",
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "product_id": "prod_123",
                    "category": "electronics"
                },
                "customer_id": "test_customer_001"
            },
            {
                "eventName": "add_to_cart",
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "product_id": "prod_123",
                    "quantity": 1
                },
                "customer_id": "test_customer_001"
            }
        ]
        
        # Store events
        event_ids = []
        for event in test_events:
            event_id = store_event(event)
            event_ids.append(event_id)
            
        # Make prediction
        prediction = predictor.predict(test_events)
        
        # Store prediction
        prediction_id = store_prediction(
            test_events[0]['customer_id'],
            test_events,
            prediction
        )
        
        return {
            "success": True,
            "data": {
                "event_ids": event_ids,
                "prediction": prediction,
                "prediction_id": prediction_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test/predict")
async def test_prediction():
    """Test prediction with a single event."""
    try:
        # Test event
        test_event = {
            "eventName": "product_view",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "product_id": "prod_789",
                "category": "electronics"
            },
            "customer_id": "test_customer_002"
        }
        
        # Make prediction
        prediction = predictor.predict([test_event])
        
        return {
            "success": True,
            "data": {
                "event": test_event,
                "prediction": prediction
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai-insights")
async def get_ai_insights():
    """Get AI-powered insights about customer journey analytics."""
    try:
        # Get all necessary data
        stage_distribution = get_stage_distribution()
        stage_transitions = get_stage_transitions()
        time_in_stages = get_time_in_stages()

        # Prepare data for AI analysis
        analysis_data = {
            "stage_distribution": stage_distribution,
            "stage_transitions": stage_transitions,
            "time_in_stages": time_in_stages
        }

        # Generate insights using Gemini
        prompt = f"""
        As an AI analytics expert, analyze this customer journey data and provide comprehensive insights:

        Stage Distribution:
        {json.dumps(stage_distribution, indent=2)}

        Stage Transitions:
        {json.dumps(stage_transitions, indent=2)}

        Time in Stages:
        {json.dumps(time_in_stages, indent=2)}

        Please provide a detailed analysis including:
        1. Trend Analysis: What patterns do you see in customer progression?
        2. Key Patterns: What are the most significant patterns in customer behavior?
        3. Recommendations: What specific actions should be taken based on this data?
        4. Risk Assessment: What potential risks or bottlenecks do you identify?

        Format the response as a JSON object with these keys:
        - trendAnalysis: A paragraph describing overall trends
        - keyPatterns: An array of significant patterns
        - recommendations: An array of actionable recommendations
        - riskAssessment: A paragraph describing potential risks
        """

        try:
            response = model.generate_content(prompt)
            insights = json.loads(response.text)
            
            return {
                "success": True,
                "data": insights
            }
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            # Return fallback insights if AI generation fails
            return {
                "success": True,
                "data": {
                    "trendAnalysis": "Unable to generate AI insights at this time.",
                    "keyPatterns": ["Please try again later"],
                    "recommendations": ["Check back for AI-powered recommendations"],
                    "riskAssessment": "Risk assessment temporarily unavailable"
                }
            }

    except Exception as e:
        logger.error(f"Error in get_ai_insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test/automation")
async def test_automation():
    """Test the automation system with a sample event."""
    try:
        # Create a test event
        test_event = {
            "eventName": "page_view",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "page": "homepage",
                "source": "direct"
            },
            "customer_id": "test_customer_001",
            "user_email": "mutation.forlife06@gmail.com",  # Your email to test
            "user_name": "Test User"
        }
        
        # Store the event
        event_id = store_event(test_event)
        
        # Get all events for this customer
        customer_events = get_customer_events(test_event['customer_id'])
        
        # Make prediction
        prediction = predictor.predict(customer_events)
        
        # Store prediction
        prediction_id = store_prediction(
            test_event['customer_id'],
            customer_events,
            prediction
        )

        # Trigger automation
        automation_result = automation_service.trigger_stage_automation(
            customer_id=test_event['customer_id'],
            stage=prediction['stage'],
            customer_email=test_event['user_email'],
            customer_name=test_event['user_name']
        )
        
        return {
            "success": True,
            "data": {
                "event_id": event_id,
                "prediction": prediction,
                "prediction_id": prediction_id,
                "automation": automation_result
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n=== Starting FastAPI server ===")  # Direct print
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 