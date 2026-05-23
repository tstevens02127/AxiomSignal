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

    AI-powered operational intelligence for supply chain resilience.
    """
)

col1, col2 = st.columns([1, 1])

with col1:
    st.link_button(
        "Request Demo",
        "mailto:arnoldmstevens@gmail.com"
    )

with col2:
    st.link_button(
        "View Platform",
        "https://axiomsignal.streamlit.app"
    )

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
    "screenshots/dashboard-preview.png",
    use_container_width=True
)

st.markdown(
    "### Real-time AI operational intelligence dashboard"
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
    AxiomSignal provides AI-powered operational intelligence for resilient global supply chains.
    """
)

st.link_button(
    "Request Demo",
    "mailto:arnoldmstevens@gmail.com?subject=AxiomSignal%20Demo%20Request"
)

st.caption(
    "AxiomSignal — AI Operational Intelligence for Global Supply Chains"
)