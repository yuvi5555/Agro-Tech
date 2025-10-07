import requests

def get_coordinates(place):
    """Get latitude, longitude for a place using Nominatim"""
    geo_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json", "limit": 1}
    response = requests.get(geo_url, params=params, headers={"User-Agent": "weather-app"})
    
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"]), data["display_name"]
    else:
        return None, None, None

def get_weather(lat, lon):
    """Get current live weather from Open-Meteo"""
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }
    response = requests.get(weather_url, params=params)
    
    if response.status_code == 200:
        return response.json().get("current_weather", {})
    return {}

def display_weather(place):
    lat, lon, loc_name = get_coordinates(place)
    if not lat or not lon:
        print("❌ Location not found. Use full details.")
        return
    
    weather = get_weather(lat, lon)
    if not weather:
        print("❌ Weather data not available right now.")
        return
    
    print(f"\n🌍 Location: {loc_name}")
    print(f"🌡️ Temperature: {weather['temperature']}°C")
    print(f"💨 Wind Speed: {weather['windspeed']} km/h")
    print(f"🧭 Wind Direction: {weather['winddirection']}°")
    print(f"⏰ Time: {weather['time']} (latest live data)")

# -------- Run once --------
if __name__ == "__main__":
    place_input = input("Enter city/village name : ")
    display_weather(place_input)
