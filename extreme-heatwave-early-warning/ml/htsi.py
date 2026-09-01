def calculate_htsi(temperature, humidity, wind_speed, solar_radiation):
    """Development placeholder for the project HTSI calculation.

    IMPORTANT: Replace this with the validated/documented thermal-stress
    methodology selected by the team. Do not claim this placeholder as an
    official HTSI formula.
    """
    # Simple development score only; NOT an official index.
    score = (
        0.55 * temperature
        + 0.20 * humidity
        - 0.10 * wind_speed
        + 0.15 * (solar_radiation / 100.0)
    )
    return round(score, 2)
