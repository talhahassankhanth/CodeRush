"""
Heat-Risk Mapping Module
Renders Folium maps with color-coded risk markers and a custom legend.
"""

import folium
from folium import Element

RISK_COLOR_MAP = {
    "LOW": "green",
    "MODERATE": "orange",
    "HIGH": "darkred",
    "EXTREME": "black",
}

RISK_HEX_MAP = {
    "LOW": "#28a745",
    "MODERATE": "#ffc107",
    "HIGH": "#fd7e14",
    "EXTREME": "#dc3545",
}


def get_risk_color(risk_level: str) -> str:
    if not risk_level:
        return "blue"
    return RISK_COLOR_MAP.get(risk_level.upper(), "blue")


def add_map_legend(heat_map: folium.Map) -> None:
    legend_html = f"""
    <div style="
        position: fixed; 
        bottom: 25px; 
        left: 25px; 
        width: 160px; 
        background-color: rgba(255, 255, 255, 0.9);
        border: 2px solid #ccc;
        border-radius: 6px;
        z-index: 9999; 
        font-size: 12px;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    ">
        <b>Heat Risk Legend</b><br>
        <i style="background: {RISK_HEX_MAP['LOW']}; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> LOW<br>
        <i style="background: {RISK_HEX_MAP['MODERATE']}; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> MODERATE<br>
        <i style="background: {RISK_HEX_MAP['HIGH']}; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> HIGH<br>
        <i style="background: {RISK_HEX_MAP['EXTREME']}; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> EXTREME<br>
        <i style="background: #6c757d; width: 12px; height: 12px; display: inline-block; border-radius: 50%;"></i> No Live Data
    </div>
    """
    heat_map.get_root().html.add_child(Element(legend_html))


def create_risk_map(
    selected_lat: float,
    selected_lon: float,
    selected_name: str,
    prediction_data: dict = None,
    preset_locations: dict = None,
) -> folium.Map:
    heat_map = folium.Map(
        location=[selected_lat, selected_lon],
        zoom_start=6,
        tiles="CartoDB positron",
        control_scale=True,
    )

    if preset_locations:
        for name, coords in preset_locations.items():
            if name != selected_name:
                folium.CircleMarker(
                    location=[coords["lat"], coords["lon"]],
                    radius=6,
                    color="#6c757d",
                    fill=True,
                    fill_color="#6c757d",
                    fill_opacity=0.6,
                    tooltip=f"{name} (Select in sidebar to evaluate)",
                ).add_to(heat_map)

    if prediction_data:
        risk = prediction_data.get("risk", "UNKNOWN").upper()
        weather = prediction_data.get("weather", {})
        temp = weather.get("temperature", "N/A")
        htsi = prediction_data.get("htsi", "N/A")
        prob = prediction_data.get("probability", 0.0)
        prob_pct = f"{prob * 100:.1f}%" if isinstance(prob, (int, float)) else "N/A"

        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 140px;">
            <h4 style="margin: 0 0 5px 0;">{selected_name}</h4>
            <hr style="margin: 4px 0;">
            <b>Risk Level:</b> <span style="color:{RISK_HEX_MAP.get(risk, '#000')}; font-weight:bold;">{risk}</span><br>
            <b>Temperature:</b> {temp} °C<br>
            <b>HTSI:</b> {htsi}<br>
            <b>Probability:</b> {prob_pct}
        </div>
        """

        folium.Marker(
            location=[selected_lat, selected_lon],
            icon=folium.Icon(
                color=get_risk_color(risk),
                icon="exclamation-triangle" if risk in ["HIGH", "EXTREME"] else "info-sign",
                prefix="glyphicon",
            ),
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{selected_name} - Risk: {risk}",
        ).add_to(heat_map)

        folium.Circle(
            location=[selected_lat, selected_lon],
            radius=25000,
            color=RISK_HEX_MAP.get(risk, "#007bff"),
            fill=True,
            fill_color=RISK_HEX_MAP.get(risk, "#007bff"),
            fill_opacity=0.25,
        ).add_to(heat_map)
    else:
        folium.Marker(
            location=[selected_lat, selected_lon],
            icon=folium.Icon(color="blue", icon="map-marker"),
            tooltip=f"{selected_name} (Awaiting assessment)",
        ).add_to(heat_map)

    add_map_legend(heat_map)
    return heat_map