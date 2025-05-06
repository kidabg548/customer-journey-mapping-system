import sys
import joblib

# Load model and vectorizer
model = joblib.load("ml-model/journey_model.pkl")
vectorizer = joblib.load("ml-model/vectorizer.pkl")

# Get input from Node.js
event_sequence = sys.argv[1]

# Convert input to vector format
input_vector = vectorizer.transform([event_sequence])

# Predict
prediction = model.predict(input_vector)[0]

# Return result
print(prediction)
