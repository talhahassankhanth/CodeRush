"""Weather provider integration."""

from __future__ import annotations

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherAPIError(RuntimeError):
    """Raised when the weather provider cannot return valid weather data."""


def get_weather(latitude: float, longitude: float) -> dict:
    """Fetch current weather for a coordinate from Open-Meteo.

    Open-Meteo exposes temperature, relative humidity, wind speed and
    shortwave solar radiation. Radiation is returned in W/m².
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,wind_speed_10m,"
            "shortwave_radiation"
        ),
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "timezone": "UTC",
    }

    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise WeatherAPIError("Weather provider is unavailable.") from exc
    except ValueError as exc:
        raise WeatherAPIError("Weather provider returned invalid JSON.") from exc

    current = payload.get("current")
    if not isinstance(current, dict):
        raise WeatherAPIError("Weather provider returned no current conditions.")

    required = (
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m",
        "shortwave_radiation",
    )
    if any(current.get(key) is None for key in required):
        raise WeatherAPIError("Required weather variables are unavailable.")

    return {
        "temperature": float(current["temperature_2m"]),
        "humidity": float(current["relative_humidity_2m"]),
        "wind_speed": float(current["wind_speed_10m"]),
        "solar_radiation": float(current["shortwave_radiation"]),
    }
