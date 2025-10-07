# smart_crop_advisory.py

"""
Smart Crop Advisory System
For Small and Marginal Farmers
Includes Fertilizer Guidance and Soil Health Recommendation (pH-based)
"""

import csv

# Function to load fertilizer data from CSV
def load_fertilizer_data(filename):
    data = []
    try:
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            # Strip spaces from headers and row keys/values
            reader.fieldnames = [f.strip() for f in reader.fieldnames]
            for row in reader:
                row = {k.strip(): v.strip() for k, v in row.items()}
                data.append(row)
    except FileNotFoundError:
        print(f"Error: '{filename}' not found in this folder.")
        exit()
    return data

# Function to get fertilizer recommendations
def get_fertilizer_recommendation(data, crop, season, soil_type):
    for row in data:
        if (row['Crop'].capitalize() == crop.capitalize() and
            row['Season'].capitalize() == season.capitalize() and
            row['SoilType'].capitalize() == soil_type.capitalize()):
            return row['FertilizerRecommendations'].split('; ')
    return ["No recommendation available for this combination"]

# Function to give soil health recommendation based on pH
def soil_health_recommendation(pH):
    if pH < 5.5:
        return "Soil is acidic. Add lime (calcium carbonate) to raise pH."
    elif 5.5 <= pH < 6.5:
        return "Soil is slightly acidic. You may add some lime."
    elif 6.5 <= pH <= 7.5:
        return "Soil pH is ideal for most crops. No major adjustment needed."
    else:
        return "Soil is alkaline. Add sulfur or organic matter to reduce pH."

# Main program
def main():
    # Load fertilizer data
    data = load_fertilizer_data('fertilizer_data.csv')
    
    print("=== Smart Crop Advisory System ===")
    print("Fertilizer Guidance & Soil Health Recommendation\n")
    
    # Take input from user
    crop = input("Enter crop name (e.g., Wheat, Rice, Maize): ")
    season = input("Enter season (Rabi/Kharif): ")
    soil_type = input("Enter soil type (Loamy/Clay/Sandy): ")
    pH = float(input("Enter your soil pH (e.g., 5.5, 6.8, 7.2): "))
    
    # Get recommendations
    fertilizer_recs = get_fertilizer_recommendation(data, crop, season, soil_type)
    soil_rec = soil_health_recommendation(pH)
    
    # Display results
    print("\n=== Soil Health Recommendation ===")
    print(soil_rec)
    
    print("\n=== Fertilizer Recommendations ===")
    for rec in fertilizer_recs:
        print("- " + rec)
    
    

# Run program
if __name__ == "__main__":
    main()
