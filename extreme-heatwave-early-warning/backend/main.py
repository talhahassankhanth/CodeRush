from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.weather_api import get_weather
from backend.sms import send_sms
from ml.predict import predict_heatwave
from ml.htsi import calculate_htsi

app = FastAPI(title="Extreme Heatwave Early Warning API")

class Location(BaseModel):
    latitude: float
    longitude: float

class AlertRequest(BaseModel):
    phone: str
    message: str

@app.get("/")
def root():
    return {"message": "Extreme Heatwave Early Warning API"}

@app.post("/predict")
def predict(location: Location):
    try:
        weather = get_weather(location.latitude, location.longitude)
        htsi = calculate_htsi(
            weather["temperature"],
            weather["humidity"],
            weather["wind_speed"],
            weather["solar_radiation"],
        )
        prediction = predict_heatwave(**weather)

        return {
            "location": location.model_dump(),
            "weather": weather,
            "htsi": htsi,
            **prediction,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/send-alert")
def alert(request: AlertRequest):
    try:
        return send_sms(request.message, request.phone)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
