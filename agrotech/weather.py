import requests

def get_coordinates(place):
    geo_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place, "format": "json", "limit": 1}
    response = requests.get(geo_url, params=params, headers={"User-Agent": "weather-app"})
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return float(data["lat"]), float(data["lon"]), data["display_name"]
    return None, None, None

def get_weather(lat, lon):
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": True}
    response = requests.get(weather_url, params=params)
    if response.status_code == 200:
        return response.json().get("current_weather", {})
    return {}

def fetch_weather_for_city(city_name):
    lat, lon, loc_name = get_coordinates(city_name)
    if not lat or not lon:
        return None
    weather = get_weather(lat, lon)
    return {
        "location": loc_name,
        "temperature": weather.get("temperature"),
        "windspeed": weather.get("windspeed"),
        "winddirection": weather.get("winddirection"),
        # "time": weather.get("time")
    }
