import requests

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    current = response.json()["current"]

    return {
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        # Live solar radiation is intentionally not assumed here.
        # Add a suitable documented source when implementing it.
        "solar_radiation": 600.0
    }
