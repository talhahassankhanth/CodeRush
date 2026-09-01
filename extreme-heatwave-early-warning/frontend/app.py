"""
Main Streamlit Application Entrypoint
"""

import streamlit as st
import requests
from streamlit_folium import st_folium

from map import create_risk_map
from dashboard import (
    display_header,
    display_risk_banner,
    display_weather_metrics,
    display_probability_gauge,
    display_safety_recommendations,
    display_sms_status,
    display_historical_trend,
)

st.set_page_config(
    page_title="Extreme Heatwave Early Warning",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRESET_LOCATIONS = {
    "Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
}

DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"


def fetch_prediction(backend_url: str, latitude: float, longitude: float) -> dict:
    endpoint = f"{backend_url.rstrip('/')}/predict"
    payload = {"latitude": float(latitude), "longitude": float(longitude)}

    try:
        response = requests.post(endpoint, json=payload, timeout=12)
        response.raise_for_status()
        data = response.json()

        for key in ["weather", "htsi", "probability", "risk"]:
            if key not in data:
                st.error(f"Incomplete backend response: Missing field '{key}'.")
                return None
        return data

    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to `{endpoint}`. Ensure the FastAPI backend server is running.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏳ Backend request timed out after 12 seconds.")
        return None
    except requests.exceptions.HTTPError as err:
        st.error(f"❌ Server Error: HTTP status {err.response.status_code}.")
        return None
    except Exception as err:
        st.error(f"❌ Request Error: {str(err)}")
        return None


def main():
    display_header()

    if "prediction_data" not in st.session_state:
        st.session_state.prediction_data = None
    if "last_queried_location" not in st.session_state:
        st.session_state.last_queried_location = "Delhi"
    if "current_lat" not in st.session_state:
        st.session_state.current_lat = PRESET_LOCATIONS["Delhi"]["lat"]
    if "current_lon" not in st.session_state:
        st.session_state.current_lon = PRESET_LOCATIONS["Delhi"]["lon"]

    st.sidebar.markdown("## ⚙️ Configuration & Target")
    location_choice = st.sidebar.selectbox(
        "Select Target Location",
        options=list(PRESET_LOCATIONS.keys()) + ["Custom Coordinates"],
        index=0,
    )

    if location_choice != "Custom Coordinates":
        target_lat = PRESET_LOCATIONS[location_choice]["lat"]
        target_lon = PRESET_LOCATIONS[location_choice]["lon"]
        location_label = location_choice
        st.sidebar.caption(f"Latitude: `{target_lat}`, Longitude: `{target_lon}`")
    else:
        location_label = "Custom Location"
        target_lat = st.sidebar.number_input(
            "Latitude", min_value=-90.0, max_value=90.0, value=28.6139, format="%.4f"
        )
        target_lon = st.sidebar.number_input(
            "Longitude", min_value=-180.0, max_value=180.0, value=77.2090, format="%.4f"
        )

    st.sidebar.markdown("---")
    backend_url = st.sidebar.text_input("Backend API URL", value=DEFAULT_BACKEND_URL)
    check_button = st.sidebar.button("CHECK HEAT RISK", type="primary", use_container_width=True)

    if check_button:
        st.session_state.last_queried_location = location_label
        st.session_state.current_lat = target_lat
        st.session_state.current_lon = target_lon

        with st.spinner("Fetching weather and calculating heat risk..."):
            result = fetch_prediction(backend_url, target_lat, target_lon)
            if result:
                st.session_state.prediction_data = result

    pred_data = st.session_state.prediction_data

    if pred_data:
        display_risk_banner(pred_data.get("risk", "LOW"), pred_data.get("probability", 0.0))
        display_weather_metrics(pred_data.get("weather", {}), pred_data.get("htsi"))

        st.markdown("---")
        left_col, right_col = st.columns([3, 2])

        with left_col:
            st.markdown(f"### 📍 Heat Risk Map — {st.session_state.last_queried_location}")
            risk_map = create_risk_map(
                selected_lat=st.session_state.current_lat,
                selected_lon=st.session_state.current_lon,
                selected_name=st.session_state.last_queried_location,
                prediction_data=pred_data,
                preset_locations=PRESET_LOCATIONS,
            )
            st_folium(risk_map, width="100%", height=420)

        with right_col:
            st.markdown("### 🎯 Model Confidence")
            display_probability_gauge(pred_data.get("probability", 0.0))
            display_sms_status(pred_data.get("sms_status"))

        st.markdown("---")
        rec_col, hist_col = st.columns([3, 2])

        with rec_col:
            display_safety_recommendations(pred_data.get("risk", "LOW"))

        with hist_col:
            if pred_data.get("historical_trend"):
                display_historical_trend(pred_data["historical_trend"])
            else:
                st.markdown("### 📈 Recent Temperature Trend")
                st.info("Historical trend data is currently unavailable from the active weather source.")
    else:
        st.info("👋 Select a target location in the sidebar and click **CHECK HEAT RISK** to perform real-time assessment.")
        default_map = create_risk_map(
            selected_lat=st.session_state.current_lat,
            selected_lon=st.session_state.current_lon,
            selected_name=st.session_state.last_queried_location,
            prediction_data=None,
            preset_locations=PRESET_LOCATIONS,
        )
        st_folium(default_map, width="100%", height=480)


if __name__ == "__main__":
    main()