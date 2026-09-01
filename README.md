# Extreme Heatwave Early Warning System

AI/ML-based system for heatwave risk prediction, Human Thermal Stress Index (HTSI), risk mapping, and alerts.

## Team structure
- Person 1: ML + HTSI
- Person 2: Backend + Weather API + SMS
- Person 3: Frontend + Map + Dashboard

## Run
1. Create a virtual environment.
2. Install: `pip install -r requirements.txt`
3. Train the model: `python ml/train.py`
4. Start API: `uvicorn backend.main:app --reload`
5. Start dashboard: `streamlit run frontend/app.py`

## Important
Do not commit API keys. Copy `.env.example` to `.env`.

The included demo-data generator is only for development/testing. Replace it with validated historical weather data and documented heatwave labels before presenting model performance.
