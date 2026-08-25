import requests
from langchain.tools import tool
@tool('get_weather', description = "Get the current weather of the given city using the OpenMeteo API")
def get_weather(city:str)->dict:
    """Get the current weather of the given city using OpenMeteo API"""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_data = requests.get(geo_url).json()

        if not geo_data.get("results"):
            return {"Error getting in the geocoding API', {city} 'not found"}
        Location = geo_data["results"][0]
        lat = Location["latitude"]
        lon = Location["longitude"]
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        date = requests.get(weather_url).json()
        temp = date["current"]["temperature_2m"]
        return {"city": city,"temp": temp, "unit": "C"}
    except Exception as e:
        return{"Error": f"Error getting in the geocoding API, '{city}':{e}"}
    