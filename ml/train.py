from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

DATA = Path("data/raw/heatwave_weather_demo.csv")
MODEL = Path("ml/model/heatwave_model.pkl")

if not DATA.exists():
    raise FileNotFoundError(
        "data/demo_weather.csv not found. Run: python ml/generate_demo_data.py"
    )

df = pd.read_csv(DATA)

features = ["temperature", "humidity", "wind_speed", "solar_radiation"]
X = df[features]
y = df["heatwave"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

pred = model.predict(X_test)
print("Accuracy:", round(accuracy_score(y_test, pred), 4))
print(classification_report(y_test, pred))

MODEL.parent.mkdir(parents=True, exist_ok=True)
joblib.dump({"model": model, "features": features}, MODEL)
print(f"Saved model to {MODEL}")
