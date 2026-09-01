import requests
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Extreme Heat Early Warning", page_icon="🌡️", layout="wide")

st.title("🌡️ Extreme Heatwave Early Warning System")
st.caption("ML + HTSI + live weather + risk mapping")

API_URL = st.sidebar.text_input("Backend URL", "http://127.0.0.1:8000")

city = st.sidebar.text_input("Location", "Delhi")
latitude = st.sidebar.number_input("Latitude", value=28.6139)
longitude = st.sidebar.number_input("Longitude", value=77.2090)

if st.button("Check Heat Risk"):
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={"latitude": latitude, "longitude": longitude},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()

        weather = data["weather"]
        probability = data["probability"] * 100
        risk = data["risk"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Temperature", f"{weather['temperature']} °C")
        c2.metric("Humidity", f"{weather['humidity']} %")
        c3.metric("Wind", f"{weather['wind_speed']} km/h")
        c4.metric("HTSI", data["htsi"])

        st.metric("Heatwave Probability", f"{probability:.1f}%")

        if risk == "HIGH":
            st.error(f"🔴 {risk} HEAT RISK")
            st.warning("Avoid prolonged outdoor exposure and stay hydrated.")
        elif risk == "MODERATE":
            st.warning(f"🟠 {risk} HEAT RISK")
        else:
            st.success(f"🟢 {risk} HEAT RISK")

        m = folium.Map(location=[latitude, longitude], zoom_start=7)
        folium.Marker(
            [latitude, longitude],
            popup=f"{city}: {risk}",
            tooltip=f"{city} - {risk}",
        ).add_to(m)
        st_folium(m, width=900, height=500)

    except Exception as exc:
        st.error(f"Could not connect to backend: {exc}")
