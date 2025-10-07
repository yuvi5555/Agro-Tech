# utils/yield_predictor.py
import pandas as pd
import joblib
import os


# Direct absolute path to the trained model
MODEL_PATH = r"C:\CEP\agrotech\yield_model.pkl"

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully!")
else:
    model = None
    print("❌ Model not found at:", MODEL_PATH)

# Encoding mappings (must match training)
crop_map = {
    "Arecanut": 0, "Arhar/Tur": 1, "Castor seed": 2,
    "Coconut": 3, "Cotton(lint)": 4, "Rice": 5, "Wheat": 6, "Maize": 7
}
season_map = {"Kharif": 0, "Rabi": 1, "Whole Year": 2}
state_map = {"Assam": 0, "Punjab": 1, "Tamil Nadu": 2, "Maharashtra": 3}

def predict_yield(crop, season, state, area, rainfall, fertilizer, pesticide):
    if model is None:
        return "Model not loaded."

    features = pd.DataFrame([[
        crop_map.get(crop, -1),
        season_map.get(season, -1),
        state_map.get(state, -1),
        area,
        rainfall,
        fertilizer,
        pesticide
    ]], columns=["Crop", "Season", "State", "Area", "Annual_Rainfall", "Fertilizer", "Pesticide"])

    prediction = model.predict(features)[0]
    return float(prediction)
