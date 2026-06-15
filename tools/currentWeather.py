import requests
import geocoder
import json

def obtainLatLon():
    try:
        location = geocoder.ip('me')
        return True, location.latlng, location.city, "Success"
    except Exception as e:
        return False, "", [], f"Error access latlng: {e}"
    
def getWeather(latlng:list, city:str): 
    codes = { 0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast", 45: "foggy", 48: "foggy", 51: "light drizzle", 61: "rain", 80: "rain showers", 95: "thunderstorm" }
    if not latlng or not city:
        return False, f"latlng or city not provided. Please try again later.", {}
    try:
        response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latlng[0]}&longitude={latlng[1]}&current_weather=true")
        data = response.json()
    
        return True, f"Success", data
    except Exception as e:
        return False, f"Error fetching weather: {e}", {}

def main():
    code, latlng, city, status = obtainLatLon()
    if not code:
        return status
    code, status, weather = getWeather(latlng, city)
    if not code:
        return status
    return json.dumps(weather)
     
if __name__ == "__main__":
    print(main())