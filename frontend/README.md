# Frontend

This directory contains the Streamlit UI for the Extreme Heatwave Early Warning System.

## Run

From the repository root:

```bash
streamlit run frontend/app.py
```

## Backend contract

The frontend expects:

```http
POST /predict
Content-Type: application/json
```

Request:

```json
{
  "latitude": 28.6139,
  "longitude": 77.2090
}
```

Expected response shape:

```json
{
  "location": {
    "latitude": 28.6139,
    "longitude": 77.2090
  },
  "weather": {
    "temperature": 44.2,
    "humidity": 40,
    "wind_speed": 8,
    "solar_radiation": 600
  },
  "htsi": 7.8,
  "probability": 0.87,
  "risk": "HIGH"
}
```

Optional fields supported by the frontend include `sms_status`/`sms` and `historical_trend`.

## Dependencies

Make sure the existing repository environment includes:

- streamlit
- folium
- streamlit-folium
- plotly
- requests
