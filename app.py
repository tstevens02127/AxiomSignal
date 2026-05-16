import streamlit as st
import pandas as pd
import folium
import requests

from datetime import datetime
from streamlit_folium import st_folium

st.set_page_config(
    page_title="AxiomSignal",
    page_icon="📡",
    layout="wide"
)

st.title("📡 AxiomSignal")

st.caption(
    "Predictive Operational Intelligence for Latin American Logistics & Infrastructure"
)

st.subheader(
    "Real-Time Risk Monitoring Across Critical Supply Chain Corridors"
)

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.success("System operational.")


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

        rows.append({
            "Type": "Earthquake",
            "Location": props.get("place", "Unknown"),
            "Magnitude": mag,
            "Risk Score": earthquake_risk_score(mag),
            "Latitude": lat,
            "Longitude": lon
        })

    return pd.DataFrame(rows)


data = fetch_earthquakes()

st.sidebar.header("Filters")

min_risk = st.sidebar.slider(
    "Minimum Risk Score",
    min_value=1,
    max_value=10,
    value=5
)

filtered_data = data[data["Risk Score"] >= min_risk]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Live Earthquake Events", len(filtered_data))

with col2:

    highest_score = (
        int(filtered_data["Risk Score"].max())
        if not filtered_data.empty
        else 0
    )

    st.metric("Highest Risk Score", highest_score)

with col3:

    status = "Elevated" if highest_score >= 6 else "Normal"

    st.metric("Operational Status", status)

st.divider()

st.subheader("Live Seismic Risk Feed")

st.dataframe(filtered_data, use_container_width=True)

st.subheader("Operational Risk Map")

risk_map = folium.Map(
    location=[-20, -70],
    zoom_start=3,
    tiles="CartoDB dark_matter"
)

for _, row in filtered_data.iterrows():

    if row["Risk Score"] >= 8:
        color = "red"

    elif row["Risk Score"] >= 5:
        color = "orange"

    else:
        color = "green"

    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=max(row["Risk Score"] * 2, 6),
        popup=(
            f"{row['Type']}<br>"
            f"{row['Location']}<br>"
            f"Magnitude: {row['Magnitude']}<br>"
            f"Risk Score: {row['Risk Score']}"
        ),
        color=color,
        fill=True,
        fill_opacity=0.7,
    ).add_to(risk_map)

st_folium(risk_map, width=1400, height=500)