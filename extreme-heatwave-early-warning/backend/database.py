"""SQLite storage for locations, weather observations, predictions and alerts."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent / "heatwave.db"


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS weather_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                wind_speed REAL NOT NULL,
                solar_radiation REAL NOT NULL,
                observed_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                wind_speed REAL NOT NULL,
                solar_radiation REAL NOT NULL,
                htsi REAL NOT NULL,
                probability REAL NOT NULL,
                risk TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                risk TEXT NOT NULL,
                phone TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_alerts_lookup
            ON alerts (latitude, longitude, phone, risk, timestamp);
            """
        )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_location(latitude: float, longitude: float, name: Optional[str] = None) -> int:
    with _connect() as conn:
        existing = conn.execute(
            """
            SELECT id FROM locations
            WHERE latitude = ? AND longitude = ?
            LIMIT 1
            """,
            (latitude, longitude),
        ).fetchone()
        if existing:
            return int(existing["id"])

        cursor = conn.execute(
            """
            INSERT INTO locations (name, latitude, longitude, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (name, latitude, longitude, _now()),
        )
        return int(cursor.lastrowid)


def save_weather_observation(
    latitude: float,
    longitude: float,
    weather: dict,
) -> int:
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO weather_observations
            (latitude, longitude, temperature, humidity, wind_speed,
             solar_radiation, observed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                latitude,
                longitude,
                weather["temperature"],
                weather["humidity"],
                weather["wind_speed"],
                weather["solar_radiation"],
                _now(),
            ),
        )
        return int(cursor.lastrowid)


def save_prediction(
    latitude: float,
    longitude: float,
    weather: dict,
    htsi: float,
    probability: float,
    risk: str,
) -> int:
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO predictions
            (latitude, longitude, temperature, humidity, wind_speed,
             solar_radiation, htsi, probability, risk, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                latitude,
                longitude,
                weather["temperature"],
                weather["humidity"],
                weather["wind_speed"],
                weather["solar_radiation"],
                htsi,
                probability,
                risk,
                _now(),
            ),
        )
        return int(cursor.lastrowid)


def recent_duplicate_alert_exists(
    latitude: float,
    longitude: float,
    phone: str,
    risk: str,
    cooldown_minutes: int = 60,
) -> bool:
    """Return True when an identical alert was already logged recently."""
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id
            FROM alerts
            WHERE latitude = ?
              AND longitude = ?
              AND phone = ?
              AND risk = ?
              AND julianday(timestamp) >= julianday('now', ?)
            LIMIT 1
            """,
            (
                latitude,
                longitude,
                phone,
                risk,
                f"-{int(cooldown_minutes)} minutes",
            ),
        ).fetchone()
        return row is not None


def save_alert(
    latitude: float,
    longitude: float,
    risk: str,
    phone: str,
    message: str,
    status: str,
) -> int:
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO alerts
            (latitude, longitude, risk, phone, message, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (latitude, longitude, risk, phone, message, status, _now()),
        )
        return int(cursor.lastrowid)
