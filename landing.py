import streamlit as st

st.set_page_config(page_title="AxiomSignal", page_icon="📡", layout="wide")

st.title("📡 AxiomSignal")
st.header("AI Operational Intelligence for Global Supply Chains")

st.subheader(
    "Real-time monitoring, AI threat forecasting, and maritime infrastructure risk analysis."
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### What AxiomSignal Does")
    st.write(
        """
        AxiomSignal helps logistics, infrastructure, and risk teams detect,
        interpret, and respond to operational disruptions before they cascade.
        """
    )

with col2:
    st.markdown("### Core Capabilities")
    st.write(
        """
        - Live threat monitoring
        - AI operational intelligence
        - Maritime corridor analysis
        - Port exposure scoring
        - Executive briefing generation
        """
    )

st.divider()

st.header("Platform Preview")
st.write("Dashboard screenshot goes here.")

st.divider()

st.header("Built for Operational Decision-Makers")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Real-Time Monitoring")
    st.write("Track seismic, weather, and logistics risk signals.")

with col2:
    st.subheader("AI Intelligence")
    st.write("Generate executive-grade risk summaries and recommendations.")

with col3:
    st.subheader("Maritime Awareness")
    st.write("Identify exposed ports, corridors, and rerouting implications.")

st.divider()

st.header("Operational resilience starts with visibility.")
st.write("Contact AxiomSignal to request access to the MVP demo.")