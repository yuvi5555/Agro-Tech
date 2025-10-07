import pandas as pd
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from xgboost import XGBClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import numpy as np


df = pd.read_csv("fertilizer_data.csv")


df['Crop'] = df['Crop'].str.strip().str.title()
df['Season'] = df['Season'].str.strip().str.title()
df['SoilType'] = df['SoilType'].str.strip().str.title()


X = df[['Crop', 'Season', 'SoilType', 'pH']]
y = df['FertilizerRecommendation']


le_target = LabelEncoder()
y_enc = le_target.fit_transform(y)


categorical_features = ['Crop', 'Season', 'SoilType']
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'  # keep pH numeric
)

# Pipeline with preprocessing + XGBoost
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42))
])

# Train the model
model_pipeline.fit(X, y_enc)

# Save model and label encoder
joblib.dump(model_pipeline, 'fertilizer_xgb_pipeline.pkl')
joblib.dump(le_target, 'le_target.pkl')

crop_rules = {
    "Wheat": {"season": ["Rabi"], "soil": ["Loamy", "Clayey"], "ph_range": (6.0, 7.5)},
    "Rice": {"season": ["Kharif"], "soil": ["Clayey", "Alluvial"], "ph_range": (5.5, 6.5)},
    "Maize": {"season": ["Kharif"], "soil": ["Loamy", "Alluvial", "Sandy"], "ph_range": (6.0, 7.0)},
    "Sugarcane": {"season": ["Annual"], "soil": ["Loamy", "Clayey", "Alluvial"], "ph_range": (6.5, 7.5)},
    "Cotton": {"season": ["Kharif"], "soil": ["Black", "Loamy"], "ph_range": (6.5, 7.5)},
    "Soybean": {"season": ["Kharif"], "soil": ["Alluvial", "Clayey", "Loamy"], "ph_range": (6.0, 7.0)}
}

# Fertilizer quantities per acre
fertilizer_quantity = {
    "Urea": "50kg/acre",
    "DAP": "30kg/acre",
    "MOP": "25kg/acre",
    "NPK": "40kg/acre"
}


# Prediction function

def predict_fertilizer(crop, season, soil_type, ph, top_n=3):
    crop = crop.strip().title()
    season = season.strip().title()
    soil_type = soil_type.strip().title()

    # Validate crop-season-soil
    rules = crop_rules.get(crop)
    if not rules:
        return f"❌ Crop '{crop}' not found in knowledge base."
    if season not in rules["season"]:
        return f"❌ {crop} is grown in {rules['season']} season only."
    if soil_type not in rules["soil"]:
        return f"❌ {crop} prefers soils: {rules['soil']}."

    # pH advice
    low, high = rules["ph_range"]
    if ph < low:
        ph_message = "Soil is acidic → Add lime or dolomite to increase pH."
    elif ph > high:
        ph_message = "Soil is alkaline → Add gypsum or organic matter to lower pH."
    else:
        ph_message = "Soil pH is optimal."

    # Prepare input for ML
    input_df = pd.DataFrame([[crop, season, soil_type, ph]],
                            columns=['Crop', 'Season', 'SoilType', 'pH'])

    # Predict top N fertilizers
    probs = model_pipeline.predict_proba(input_df)[0]
    top_indices = np.argsort(probs)[::-1][:top_n]
    top_fertilizers = [le_target.inverse_transform([i])[0] for i in top_indices]

    # Format output with quantities
    fertilizers_formatted = "\n".join(
        [f"- {f} - {fertilizer_quantity.get(f, 'N/A')}" for f in top_fertilizers]
    )

    output = (
        f"=== Soil Health Recommendation ===\n"
        f"{ph_message}\n\n"
        f"=== Fertilizer Recommendation ===\n"
        f"{fertilizers_formatted}"
    )
    return output


# Interactive input
if __name__ == "__main__":
    print("=== Fertilizer Recommendation System ===")
    crop = input("Enter crop name: ")
    season = input("Enter season: ")
    soil_type = input("Enter soil type: ")
    ph = float(input("Enter soil pH (e.g., 6.5): "))

    result = predict_fertilizer(crop, season, soil_type, ph, top_n=3)
    print("\n" + result)
