import streamlit as st
import pandas as pd
import folium

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

data = pd.DataFrame({
    "Type": ["Earthquake", "Port Disruption", "Severe Weather"],
    "Location": ["Chile", "Panama Canal", "Brazil"],
    "Risk Score": [8, 6, 7],
    "Latitude": [-33.45, 9.08, -23.55],
    "Longitude": [-70.66, -79.68, -46.63]
})

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
    st.metric("Live Risk Events", len(filtered_data))

with col2:
    highest_score = int(filtered_data["Risk Score"].max()) if not filtered_data.empty else 0
    st.metric("Highest Risk Score", highest_score)

with col3:
    status = "Elevated" if highest_score >= 6 else "Normal"
    st.metric("Operational Status", status)

st.divider()

st.subheader("Live Operational Risk Feed")

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
        radius=row["Risk Score"] * 2,
        popup=(
            f"{row['Type']}<br>"
            f"{row['Location']}<br>"
            f"Risk Score: {row['Risk Score']}"
        ),
        color=color,
        fill=True,
        fill_opacity=0.7,
    ).add_to(risk_map)

st_folium(risk_map, width=1400, height=500)