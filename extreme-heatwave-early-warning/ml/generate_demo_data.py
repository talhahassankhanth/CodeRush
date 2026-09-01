import numpy as np
import pandas as pd

np.random.seed(42)
n = 1500

temperature = np.random.normal(36, 6, n).clip(25, 50)
humidity = np.random.normal(50, 15, n).clip(15, 95)
wind_speed = np.random.normal(10, 4, n).clip(1, 30)
solar_radiation = np.random.normal(600, 150, n).clip(100, 1000)

# DEVELOPMENT-ONLY labels for testing the pipeline.
heatwave = (
    (temperature >= 42)
    & (humidity <= 65)
).astype(int)

df = pd.DataFrame({
    "temperature": temperature,
    "humidity": humidity,
    "wind_speed": wind_speed,
    "solar_radiation": solar_radiation,
    "heatwave": heatwave
})

df.to_csv("data/demo_weather.csv", index=False)
print("Created data/demo_weather.csv (development-only synthetic data).")
