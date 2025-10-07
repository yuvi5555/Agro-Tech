import pandas as pd
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from xgboost import XGBClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import numpy as np

# Load dataset
df = pd.read_csv("fertilizer_data.csv")

# Clean categorical columns
df['Crop'] = df['Crop'].str.strip().str.title()
df['Season'] = df['Season'].str.strip().str.title()
df['SoilType'] = df['SoilType'].str.strip().str.title()

# Features and target
X = df[['Crop', 'Season', 'SoilType', 'pH']]
y = df['FertilizerRecommendation']

# Encode target
le_target = LabelEncoder()
y_enc = le_target.fit_transform(y)

# OneHotEncoder for categorical features
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
    ('classifier', XGBClassifier(use_label_encoder=False, eval_metric='mlogloss'))
])

# Train the model
model_pipeline.fit(X, y_enc)

# Save model and label encoder
joblib.dump(model_pipeline, 'fertilizer_xgb_pipeline.pkl')
joblib.dump(le_target, 'le_target.pkl')

# Function to generate pH advice
def soil_ph_advice(ph):
    if ph < 5.5:
        return "Soil is acidic → Add lime/dolomite to raise pH and improve nutrient availability."
    elif 5.5 <= ph <= 7.5:
        return "Soil pH is neutral → Good for most crops. No major amendment needed."
    else:
        return "Soil is alkaline → Add gypsum or organic matter to lower pH and improve structure."

# Function to predict top 3 fertilizers
def predict_fertilizer(crop, season, soil_type, ph, top_n=3):
    crop = crop.strip().title()
    season = season.strip().title()
    soil_type = soil_type.strip().title()
    
    input_df = pd.DataFrame([[crop, season, soil_type, ph]],
                            columns=['Crop', 'Season', 'SoilType', 'pH'])
    
    # Predict probabilities for all classes
    probs = model_pipeline.predict_proba(input_df)[0]
    
    # Get indices of top N fertilizers
    top_indices = np.argsort(probs)[::-1][:top_n]
    
    # Convert indices back to fertilizer names
    top_fertilizers = [le_target.inverse_transform([i])[0] for i in top_indices]
    
    # Get soil pH advice
    ph_message = soil_ph_advice(ph)
    
    # Format top fertilizers in required format
    fertilizers_formatted = "; ".join(top_fertilizers)
    
    output = f"{ph_message}\nRecommended Fertilizers: {fertilizers_formatted}"
    return output

# Interactive input
if __name__ == "__main__":
    print("=== Fertilizer Recommendation System (Top 3) ===")
    crop = input("Enter crop name: ")
    season = input("Enter season: ")
    soil_type = input("Enter soil type: ")
    ph = float(input("Enter soil pH (e.g., 6.5): "))
    
    result = predict_fertilizer(crop, season, soil_type, ph, top_n=3)
    print("\n" + result)
