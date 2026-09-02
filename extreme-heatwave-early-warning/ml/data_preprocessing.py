import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "heatwave_weather_demo.csv"
PROCESSED_FILE = BASE_DIR / "data" / "processed" / "heatwave_weather_processed.csv"


def preprocess_data():

    print("Loading dataset...")

    df = pd.read_csv(RAW_FILE)

    print(f"Original rows: {len(df)}")

    required_columns = [
        "date",
        "latitude",
        "longitude",
        "temperature",
        "humidity",
        "wind_speed",
        "solar_radiation",
        "heatwave",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # Convert date
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # Convert numerical columns
    numerical_columns = [
        "latitude",
        "longitude",
        "temperature",
        "humidity",
        "wind_speed",
        "solar_radiation",
        "heatwave",
    ]

    for column in numerical_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Remove missing values
    df = df.dropna()

    # Sort by date
    df = df.sort_values("date")

    # Remove impossible values
    df = df[
        (df["humidity"] >= 0)
        & (df["humidity"] <= 100)
        & (df["wind_speed"] >= 0)
        & (df["solar_radiation"] >= 0)
    ]

    # Make heatwave an integer
    df["heatwave"] = df["heatwave"].astype(int)

    # Previous-day temperature
    df["temperature_previous_day"] = (
        df["temperature"].shift(1)
    )

    # 3-day average temperature
    df["temperature_3day_avg"] = (
        df["temperature"]
        .rolling(3)
        .mean()
    )

    # 7-day average temperature
    df["temperature_7day_avg"] = (
        df["temperature"]
        .rolling(7)
        .mean()
    )

    # Remove rows without enough history
    df = df.dropna()

    # Create processed folder
    PROCESSED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save processed dataset
    df.to_csv(
        PROCESSED_FILE,
        index=False
    )

    print(f"Processed rows: {len(df)}")
    print(f"Saved to: {PROCESSED_FILE}")


if __name__ == "__main__":
    preprocess_data()