Set-Content -Path app.py -Value @'
import streamlit as st
import pandas as pd
import folium
import requests

from datetime import datetime
from streamlit_folium import st_folium

st.set_page_config(page_title="AxiomSignal", page_icon="📡", layout="wide")

st.title("📡 AxiomSignal")
st.caption("Predictive Operational Intelligence for Latin American Logistics & Infrastructure")
st.subheader("Real-Time Risk Monitoring Across Critical Supply Chain Corridors")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.success("System operational.")

def risk_label(score):
    if score >= 8:
        return "Critical"
    elif score >= 5:
        return "Elevated"
    elif score >= 3:
        return "Moderate"
    return "Low"

def earthquake_risk_score(magnitude):
    if magnitude >= 7:
        return 10
    elif magnitude >= 6:
        return 8
    elif magnitude >= 5:
        return 6
    elif magnitude >= 4:
        return 4
    return 2

def weather_risk_score(wind_speed, precipitation):
    score = 1
    if wind_speed > 70:
        score += 4
    elif wind_speed > 40:
        score += 2
    if precipitation > 40:
        score += 4
    elif precipitation > 15:
        score += 2
    return min(score, 10)

@st.cache_data(ttl=300)
def fetch_earthquakes():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    quake_data = response.json()

    rows = []
    for feature in quake_data.get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [])
        if len(coords) < 2:
            continue

        lon = coords[0]
        lat = coords[1]
        mag = props.get("mag", 0) or 0

        if not (-60 <= lat <= 35 and -150 <= lon <= -30):
            continue

        score = earthquake_risk_score(mag)

        rows.append({
            "Type": "Earthquake",
            "Location": props.get("place", "Unknown"),
            "Magnitude": mag,
            "Temperature": None,
            "Wind Speed": None,
            "Precipitation": None,
            "Risk Score": score,
            "Severity": risk_label(score),
            "Latitude": lat,
            "Longitude": lon
        })

    return pd.DataFrame(rows)

@st.cache_data(ttl=1800)
def fetch_weather():
    locations = [
        {"name": "Santiago", "lat": -33.45, "lon": -70.66},
        {"name": "Valparaiso", "lat": -33.04, "lon": -71.63},
        {"name": "Lima", "lat": -12.05, "lon": -77.04},
        {"name": "Santos Port", "lat": -23.96, "lon": -46.33},
        {"name": "Cartagena", "lat": 10.39, "lon": -75.48},
        {"name": "Buenaventura", "lat": 3.88, "lon": -77.03},
    ]

    rows = []
    for loc in locations:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={loc['lat']}&longitude={loc['lon']}"
            "&current=temperature_2m,precipitation,wind_speed_10m"
        )

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        current = weather_data.get("current", {})

        temperature = current.get("temperature_2m", 0) or 0
        precipitation = current.get("precipitation", 0) or 0
        wind_speed = current.get("wind_speed_10m", 0) or 0

        score = weather_risk_score(wind_speed, precipitation)

        rows.append({
            "Type": "Weather",
            "Location": loc["name"],
            "Magnitude": None,
            "Temperature": temperature,
            "Wind Speed": wind_speed,
            "Precipitation": precipitation,
            "Risk Score": score,
            "Severity": risk_label(score),
            "Latitude": loc["lat"],
            "Longitude": loc["lon"]
        })

    return pd.DataFrame(rows)

earthquake_df = fetch_earthquakes()
weather_df = fetch_weather()
data = pd.concat([earthquake_df, weather_df], ignore_index=True)

st.sidebar.header("Filters")

min_risk = st.sidebar.slider("Minimum Risk Score", 1, 10, 1)

event_types = st.sidebar.multiselect(
    "Event Types",
    ["Earthquake", "Weather"],
    default=["Earthquake", "Weather"]
)

filtered_data = data[
    (data["Risk Score"] >= min_risk)
    & (data["Type"].isin(event_types))
]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Live Risk Events", len(filtered_data))

with col2:
    highest_score = int(filtered_data["Risk Score"].max()) if not filtered_data.empty else 0
    st.metric("Highest Risk Score", highest_score)

with col3:
    status = "Elevated" if highest_score >= 6 else "Normal"
    st.metric("Operational Status", status)

st.divider()

st.subheader("Live Operational Risk Feed")

display_columns = [
    "Type", "Location", "Magnitude", "Temperature", "Wind Speed",
    "Precipitation", "Risk Score", "Severity", "Latitude", "Longitude"
]

st.dataframe(filtered_data[display_columns], use_container_width=True)

st.subheader("Operational Risk Map")

risk_map = folium.Map(location=[-20, -70], zoom_start=3, tiles="CartoDB dark_matter")

for _, row in filtered_data.iterrows():
    if row["Risk Score"] >= 8:
        color = "red"
    elif row["Risk Score"] >= 5:
        color = "orange"
    elif row["Risk Score"] >= 3:
        color = "yellow"
    else:
        color = "green"

    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=max(row["Risk Score"] * 2, 6),
        popup=(
            f"{row['Type']}<br>"
            f"{row['Location']}<br>"
            f"Risk Score: {row['Risk Score']}<br>"
            f"Severity: {row['Severity']}"
        ),
        color=color,
        fill=True,
        fill_opacity=0.7,
    ).add_to(risk_map)

st_folium(risk_map, width=1400, height=500)

st.subheader("Regional Weather Monitoring")

st.dataframe(
    weather_df[
        ["Location", "Temperature", "Wind Speed", "Precipitation", "Risk Score", "Severity"]
    ],
    use_container_width=True
)
'@