"""FastAPI backend for the Extreme Heatwave Early Warning System."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from backend.database import (
    init_db,
    recent_duplicate_alert_exists,
    save_alert,
    save_location,
    save_prediction,
    save_weather_observation,
)
from backend.sms import SMSProviderError, send_sms
from backend.weather_api import WeatherAPIError, get_weather
from ml.htsi import calculate_htsi
from ml.predict import predict_heatwave


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Extreme Heatwave Early Warning API",
    description="Backend bridge for weather data, HTSI, ML risk prediction and alerts.",
    version="1.0.0",
    lifespan=lifespan,
)


class Location(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class AlertRequest(BaseModel):
    phone: str = Field(..., min_length=7, max_length=20)
    message: str = Field(..., min_length=1, max_length=320)


class PredictionResponse(BaseModel):
    location: Location
    weather: dict
    htsi: float
    probability: float
    risk: str
    recommendations: List[str]
    alert: dict


def recommendations_for(risk: str) -> list[str]:
    if risk == "EXTREME":
        return [
            "Avoid unnecessary outdoor exposure",
            "Stay hydrated",
            "Follow official local heat warnings",
        ]
    if risk == "HIGH":
        return [
            "Stay hydrated",
            "Avoid prolonged outdoor exposure",
            "Avoid unnecessary afternoon outdoor activity",
        ]
    if risk == "MODERATE":
        return [
            "Stay hydrated",
            "Take breaks during prolonged outdoor activity",
        ]
    return ["Continue normal precautions and stay hydrated"]


def build_alert_message(risk: str, temperature: float) -> str:
    if risk == "EXTREME":
        return (
            "EXTREME HEAT RISK: extreme heat conditions detected. "
            f"Temperature: {temperature:.1f}C. Avoid unnecessary outdoor exposure "
            "and follow official local warnings."
        )
    return (
        "HIGH HEAT RISK: high heat risk detected. "
        f"Temperature: {temperature:.1f}C. Stay hydrated and avoid prolonged outdoor exposure."
    )


@app.get("/")
def root():
    return {"message": "Extreme Heatwave Early Warning API"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponse)
def predict(location: Location):
    try:
        weather = get_weather(location.latitude, location.longitude)
    except WeatherAPIError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    try:
        htsi = calculate_htsi(
            weather["temperature"],
            weather["humidity"],
            weather["wind_speed"],
            weather["solar_radiation"],
        )
        prediction = predict_heatwave(
            weather["temperature"],
            weather["humidity"],
            weather["wind_speed"],
            weather["solar_radiation"],
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model is not available. Train the model first.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction service failed.",
        ) from exc

    risk = prediction["risk"]
    probability = float(prediction["probability"])

    try:
        save_location(location.latitude, location.longitude)
        save_weather_observation(location.latitude, location.longitude, weather)
        save_prediction(
            location.latitude,
            location.longitude,
            weather,
            htsi,
            probability,
            risk,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction was generated but could not be stored.",
        ) from exc

    # Automatic SMS is intentionally opt-in through an environment variable.
    # This prevents every dashboard refresh from generating an SMS.
    alert_result = {"sent": False, "message": "Automatic SMS disabled"}
    alert_phone = os.getenv("ALERT_PHONE_NUMBER")
    auto_alert = os.getenv("AUTO_ALERT_ENABLED", "false").lower() == "true"

    if auto_alert and risk in {"HIGH", "EXTREME"} and alert_phone:
        message = build_alert_message(risk, weather["temperature"])
        duplicate = recent_duplicate_alert_exists(
            location.latitude,
            location.longitude,
            alert_phone,
            risk,
            cooldown_minutes=int(os.getenv("ALERT_COOLDOWN_MINUTES", "60")),
        )

        if duplicate:
            alert_result = {"sent": False, "message": "Duplicate alert suppressed"}
        else:
            try:
                alert_result = send_sms(message, alert_phone)
                alert_status = "sent" if alert_result.get("sent") else "not_sent"
            except SMSProviderError:
                alert_result = {"sent": False, "message": "SMS provider request failed"}
                alert_status = "failed"

            save_alert(
                location.latitude,
                location.longitude,
                risk,
                alert_phone,
                message,
                alert_status,
            )

    return {
        "location": location.model_dump(),
        "weather": weather,
        "htsi": htsi,
        "probability": probability,
        "risk": risk,
        "recommendations": recommendations_for(risk),
        "alert": alert_result,
    }


@app.post("/send-alert")
def alert(request: AlertRequest):
    try:
        result = send_sms(request.message, request.phone)
    except SMSProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    # Log both successful and unsuccessful configured attempts.
    status_value = "sent" if result.get("sent") else "not_sent"
    try:
        save_alert(0.0, 0.0, "MANUAL", request.phone, request.message, status_value)
    except Exception:
        # Sending the message should not be reported as failed merely because
        # audit logging failed.
        pass

    return result
