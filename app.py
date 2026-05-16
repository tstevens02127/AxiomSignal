import streamlit as st
import pandas as pd
from datetime import datetime

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

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Live Risk Events", 3)

with col2:
    st.metric("Highest Risk Score", 8)

with col3:
    st.metric("Operational Status", "Elevated")

data = pd.DataFrame({
    "Type": ["Earthquake", "Port Disruption", "Severe Weather"],
    "Location": ["Chile", "Panama Canal", "Brazil"],
    "Risk Score": [8, 6, 7]
})

st.dataframe(data, use_container_width=True)