from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path("ml/model/heatwave_model.pkl")

def predict_heatwave(temperature, humidity, wind_speed, solar_radiation):
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Train the model first: python ml/train.py")

    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    features = bundle["features"]

    row = pd.DataFrame([{
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "solar_radiation": solar_radiation
    }])[features]

    probability = float(model.predict_proba(row)[0][1])
    risk = "HIGH" if probability >= 0.70 else "MODERATE" if probability >= 0.40 else "LOW"

    return {"probability": round(probability, 4), "risk": risk}
