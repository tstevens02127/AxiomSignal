import streamlit as st

st.set_page_config(
    page_title="AxiomSignal",
    page_icon="📡",
    layout="wide"
)

st.title("📡 AxiomSignal")

st.markdown(
    """
    # AI Operational Intelligence for Global Supply Chains

    Real-time threat monitoring, AI forecasting, maritime infrastructure awareness,
    and executive intelligence for operational decision-makers.
    """
)

col1, col2 = st.columns([1, 1])

with col1:
    st.button("Request Demo")

with col2:
    st.button("View Platform")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### What AxiomSignal Does")
    st.write(
        """
        AxiomSignal helps logistics, infrastructure, maritime, and risk teams detect,
        interpret, and respond to operational disruptions before they cascade across
        critical supply chains.
        """
    )

with col2:
    st.markdown("### Core Capabilities")
    st.write(
        """
        - Live seismic and weather monitoring
        - AI operational intelligence summaries
        - Maritime corridor impact analysis
        - Strategic port exposure scoring
        - Executive briefing generation
        """
    )

st.divider()

st.header("Platform Preview")

st.image(
    "https://placehold.co/1200x700/png",
    use_container_width=True
)

st.caption(
    "Live AI operational intelligence dashboard monitoring critical supply chain corridors."
)

st.divider()

st.header("Built for Operational Decision-Makers")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Real-Time Monitoring")
    st.write(
        """
        Track seismic, weather, news, and infrastructure risk signals across
        critical logistics corridors.
        """
    )

with col2:
    st.subheader("AI Intelligence")
    st.write(
        """
        Generate executive-grade summaries, forecasts, route impact analysis,
        and recommended actions.
        """
    )

with col3:
    st.subheader("Maritime Awareness")
    st.write(
        """
        Identify exposed ports, corridors, rerouting implications, and
        infrastructure risk propagation.
        """
    )

st.divider()

st.header("Operational resilience starts with visibility.")

st.write(
    """
    AxiomSignal is currently in MVP development and is focused on helping
    Latin American logistics and infrastructure operators improve disruption
    visibility, operational readiness, and executive decision-making.
    """
)

st.button("Contact AxiomSignal")

st.caption(
    "AxiomSignal — AI Operational Intelligence for Global Supply Chains"
)