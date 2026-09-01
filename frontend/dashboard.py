"""
Dashboard Visual Components
Contains metric cards, gauges, risk alerts, and guidance views.
"""

import streamlit as st
import plotly.graph_objects as go


def display_header() -> None:
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="margin: 0; padding: 0; color: #1e293b; font-size: 2.2rem;">
                EXTREME HEATWAVE EARLY WARNING SYSTEM
            </h1>
            <p style="margin: 5px 0 0 0; color: #64748b; font-size: 1.1rem; font-weight: 500;">
                AI/ML-based Heat Risk Monitoring and Early Warning
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_risk_banner(risk_level: str, probability: float) -> None:
    norm_risk = (risk_level or "LOW").upper()
    prob_pct = f"{probability * 100:.1f}%" if isinstance(probability, (int, float)) else "N/A"

    if norm_risk == "EXTREME":
        st.error(
            f"🚨 **CRITICAL WARNING: EXTREME HEAT RISK**\n\n"
            f"Heatwave Probability: **{prob_pct}**. Immediate emergency precautions required."
        )
    elif norm_risk == "HIGH":
        st.warning(
            f"⚠️ **WARNING: HIGH HEAT RISK**\n\n"
            f"Heatwave Probability: **{prob_pct}**. Severe thermal conditions expected."
        )
    elif norm_risk == "MODERATE":
        st.info(
            f"🟡 **ADVISORY: MODERATE HEAT RISK**\n\n"
            f"Heatwave Probability: **{prob_pct}**. Elevated heat exposure expected."
        )
    else:
        st.success(
            f"🟢 **NORMAL: LOW HEAT RISK**\n\n"
            f"Heatwave Probability: **{prob_pct}**. Conditions within standard safety limits."
        )


def display_weather_metrics(weather: dict, htsi_value) -> None:
    st.markdown("### 📊 Atmospheric & Biometeorological Indicators")

    temp = weather.get("temperature", "N/A")
    humidity = weather.get("humidity", "N/A")
    wind_speed = weather.get("wind_speed", "N/A")
    solar_rad = weather.get("solar_radiation", "N/A")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🌡 Temperature", f"{temp} °C" if isinstance(temp, (int, float)) else str(temp))
    c2.metric("💧 Humidity", f"{humidity} %" if isinstance(humidity, (int, float)) else str(humidity))
    c3.metric("💨 Wind Speed", f"{wind_speed} km/h" if isinstance(wind_speed, (int, float)) else str(wind_speed))
    c4.metric("☀️ Solar Radiation", f"{solar_rad} W/m²" if isinstance(solar_rad, (int, float)) else str(solar_rad))
    c5.metric("🔥 HTSI Score", str(htsi_value) if htsi_value is not None else "N/A")


def display_probability_gauge(probability: float) -> None:
    prob_val = float(probability) if isinstance(probability, (int, float)) else 0.0
    percentage = prob_val * 100

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=percentage,
            number={"suffix": "%", "font": {"size": 28}},
            title={"text": "Heatwave Probability", "font": {"size": 18}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "gray"},
                "bar": {"color": "#1f2937"},
                "steps": [
                    {"range": [0, 30], "color": "#28a745"},
                    {"range": [30, 60], "color": "#ffc107"},
                    {"range": [60, 85], "color": "#fd7e14"},
                    {"range": [85, 100], "color": "#dc3545"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 4},
                    "thickness": 0.75,
                    "value": percentage,
                },
            },
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def display_safety_recommendations(risk_level: str) -> None:
    st.markdown("### 🛡️ Safety Recommendations")
    norm_risk = (risk_level or "LOW").upper()

    if norm_risk == "EXTREME":
        st.markdown(
            """
            * 🚨 **Avoid Outdoor Exposure:** Remain indoors in well-ventilated or air-conditioned environments.
            * 💧 **Continuous Hydration:** Drink ORS or water continuously; avoid caffeinated beverages.
            * 🛑 **Cease Heavy Labor:** Halt direct outdoor physical work from 11:00 AM to 4:30 PM.
            * 👥 **Vulnerable Support:** Monitor elderly individuals, infants, and those with chronic illnesses.
            """
        )
    elif norm_risk == "HIGH":
        st.markdown(
            """
            * ⚠️ **Limit Midday Sunlight:** Avoid prolonged outdoor exposure between 12:00 PM and 4:00 PM.
            * 💧 **Hydrate Regularly:** Drink fluids frequently before experiencing thirst.
            * 🧢 **Sun Protection:** Wear loose, light cotton clothing and wide-brimmed hats.
            * 🏢 **Cooling Breaks:** Outdoor workers must take mandatory rest intervals in the shade.
            """
        )
    elif norm_risk == "MODERATE":
        st.markdown(
            """
            * 🟡 **General Precaution:** Keep adequate hydration throughout the day.
            * 🧢 **Sun Protection:** Cover head and neck in direct sunlight.
            * ⚠️ **Vigilance:** Watch for early heat exhaustion signs (dizziness, fatigue).
            """
        )
    else:
        st.markdown(
            """
            * 🟢 **Normal Activity:** Thermal stress conditions are within normal limits.
            * 💧 **Standard Hydration:** Maintain normal daily fluid intake.
            """
        )
    st.caption("Guidance provided for public safety and awareness. Not clinical medical advice.")


def display_sms_status(sms_status_data: dict = None) -> None:
    st.markdown("### 📱 SMS Alert Status")
    if not sms_status_data:
        st.info("SMS Dispatch Status: **Not triggered** (Below threshold or backend dispatch idle).")
        return

    if sms_status_data.get("triggered", False):
        st.success(f"✓ **Alert Dispatched**: {sms_status_data.get('message', 'Alert delivered')}")
    else:
        st.info(f"Status: **Idle** — {sms_status_data.get('message', 'No alerts queued')}")


def display_historical_trend(history_data: list = None) -> None:
    if not history_data:
        return
    st.markdown("### 📈 Recent Temperature Trend")
    try:
        dates = [item.get("date", f"Day {i+1}") for i, item in enumerate(history_data)]
        temps = [item.get("temperature", 0) for item in history_data]
        fig = go.Figure(data=go.Scatter(x=dates, y=temps, mode="lines+markers", line=dict(color="#fd7e14", width=3)))
        fig.update_layout(
            height=260,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.caption("Historical trend data unavailable.")