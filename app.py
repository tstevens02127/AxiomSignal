import streamlit as st
import pandas as pd
import requests
import folium

from datetime import datetime
from streamlit_folium import st_folium

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
st.set_page_config(
    page_title="AxiomSignal",
    page_icon="📡",
    layout="wide"
)

st.image("assets/logo.png", width=450)

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
    """
    <div style="padding: 14px 0 6px 0;">
        <h1 style="margin-bottom: 0;">📡 AxiomSignal</h1>
        <p style="font-size: 18px; color: #6b7280; margin-top: 4px;">
            Predictive Operational Intelligence for Latin American Logistics & Infrastructure
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.subheader("Real-Time Risk Monitoring Across Critical Supply Chain Corridors")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.info(
    """
    AxiomSignal helps mid-size logistics and infrastructure operators identify elevated
    operational risks before disruptions escalate.
    """
)

st.markdown(
    """
    **Monitored Risk Categories:** Seismic Activity · Severe Weather · Infrastructure Disruption · Geopolitical Events · Supply Chain Volatility
    """
)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Filters")

min_risk = st.sidebar.slider(
    "Minimum Risk Score",
    min_value=1,
    max_value=10,
    value=5
)

selected_categories = st.sidebar.multiselect(
    "Risk Categories",
    ["Earthquake", "Weather", "News / Geopolitical"],
    default=["Earthquake", "Weather", "News / Geopolitical"]
)

# -----------------------------
# RISK SCORING
# -----------------------------
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


def news_risk_score(title):
    title = title.lower()

    high_risk_keywords = [
        "strike",
        "protest",
        "blockade",
        "earthquake",
        "wildfire",
        "flood",
        "port",
        "shipping",
        "supply chain",
        "violence",
        "emergency",
        "disruption",
        "logistics",
        "transport",
        "infrastructure",
    ]

    score = 3

    for keyword in high_risk_keywords:
        if keyword in title:
            score += 2

    return min(score, 10)


def color_severity(val):
    if val == "Critical":
        return "background-color: #dc2626; color: white"
    elif val == "Elevated":
        return "background-color: #f59e0b; color: black"
    elif val == "Moderate":
        return "background-color: #fde68a; color: black"
    return "background-color: #16a34a; color: white"


# -----------------------------
# DATA SOURCES
# -----------------------------
@st.cache_data(ttl=300)
def fetch_earthquakes():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    rows = []

    for feature in data.get("features", []):
        props = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coords = geometry.get("coordinates", [None, None])

        if len(coords) < 2:
            continue

        magnitude = props.get("mag", 0) or 0
        longitude = coords[0]
        latitude = coords[1]

        if latitude is None or longitude is None:
            continue

        # LatAm + Pacific logistics corridor focus
        if not (-60 <= latitude <= 35 and -150 <= longitude <= -30):
            continue

        score = earthquake_risk_score(magnitude)

        rows.append(
            {
                "Type": "Earthquake",
                "Location": props.get("place", "Unknown location"),
                "Risk Score": score,
                "Severity": risk_label(score),
                "Magnitude": magnitude,
                "Latitude": latitude,
                "Longitude": longitude,
                "Headline": "",
                "URL": props.get("url", ""),
            }
        )

    return pd.DataFrame(rows)


@st.cache_data(ttl=1800)
def fetch_weather():
    locations = [
        {"name": "Santiago", "lat": -33.45, "lon": -70.66},
        {"name": "Valparaiso", "lat": -33.04, "lon": -71.63},
        {"name": "Lima", "lat": -12.05, "lon": -77.04},
        {"name": "Santos Port", "lat": -23.96, "lon": -46.33},
        {"name": "Buenaventura", "lat": 3.88, "lon": -77.03},
        {"name": "Cartagena", "lat": 10.39, "lon": -75.48},
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

        data = response.json()
        current = data.get("current", {})

        wind_speed = current.get("wind_speed_10m", 0) or 0
        precipitation = current.get("precipitation", 0) or 0
        temperature = current.get("temperature_2m", 0) or 0

        score = weather_risk_score(wind_speed, precipitation)

        rows.append(
            {
                "Type": "Weather",
                "Location": loc["name"],
                "Risk Score": score,
                "Severity": risk_label(score),
                "Temperature": temperature,
                "Wind Speed": wind_speed,
                "Precipitation": precipitation,
                "Latitude": loc["lat"],
                "Longitude": loc["lon"],
                "Headline": "",
                "URL": "",
            }
        )

    return pd.DataFrame(rows)


@st.cache_data(ttl=900)
def fetch_gdelt_news():
    url = "https://api.gdeltproject.org/api/v2/doc/doc"

    params = {
        "query": '(Chile OR Peru OR Brazil OR Colombia) (logistics OR port OR shipping OR "supply chain" OR protest OR strike OR disruption)',
        "mode": "ArtList",
        "format": "json",
        "maxrecords": 15,
        "sort": "HybridRel",
    }

    empty_df = pd.DataFrame(
        columns=["Type", "Location", "Risk Score", "Severity", "Headline", "URL"]
    )

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        if not response.text.strip():
            return empty_df

        data = response.json()
        rows = []

        for article in data.get("articles", []):
            title = article.get("title", "")
            source_country = article.get("sourceCountry", "LatAm")
            article_url = article.get("url", "")

            score = news_risk_score(title)

            rows.append(
                {
                    "Type": "News / Geopolitical",
                    "Location": source_country,
                    "Risk Score": score,
                    "Severity": risk_label(score),
                    "Headline": title,
                    "URL": article_url,
                }
            )

        return pd.DataFrame(rows)

    except Exception:
        return empty_df


# -----------------------------
# APP BODY
# -----------------------------
try:
    eq_df = fetch_earthquakes()
    weather_df = fetch_weather()
    news_df = fetch_gdelt_news()

    map_df = pd.concat(
        [
            eq_df[["Type", "Location", "Risk Score", "Severity", "Latitude", "Longitude", "Headline", "URL"]],
            weather_df[["Type", "Location", "Risk Score", "Severity", "Latitude", "Longitude", "Headline", "URL"]],
        ],
        ignore_index=True,
    )

    feed_df = pd.concat(
        [
            map_df[["Type", "Location", "Risk Score", "Severity", "Headline", "URL"]],
            news_df[["Type", "Location", "Risk Score", "Severity", "Headline", "URL"]],
        ],
        ignore_index=True,
    )

    feed_df = feed_df[
        (feed_df["Risk Score"] >= min_risk)
        & (feed_df["Type"].isin(selected_categories))
    ]

    filtered_map_df = map_df[
        (map_df["Risk Score"] >= min_risk)
        & (map_df["Type"].isin(selected_categories))
    ]

    # -----------------------------
    # METRICS
    # -----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Live Risk Events", len(feed_df))

    col2.metric(
        "Highest Risk Score",
        int(feed_df["Risk Score"].max()) if not feed_df.empty else 0,
    )

    col3.metric(
        "Critical / Elevated",
        len(feed_df[feed_df["Severity"].isin(["Critical", "Elevated"])])
        if not feed_df.empty else 0,
    )

    col4.metric(
        "Operational Status",
        "Elevated" if not feed_df.empty else "Normal",
    )

    st.divider()

    # -----------------------------
    # LIVE FEED
    # -----------------------------
    st.subheader("Live Operational Risk Feed")

    display_feed = feed_df.copy()

    if display_feed.empty:
        st.success("No elevated operational risks detected under current filters.")
    else:
        styled_feed = display_feed.style.map(
            color_severity,
            subset=["Severity"],
        )
        st.dataframe(styled_feed, width="stretch", hide_index=True)

    # -----------------------------
    # MAP
    # -----------------------------
    st.subheader("Operational Risk Map")

    risk_map = folium.Map(
        location=[-20, -70],
        zoom_start=3,
        tiles="CartoDB dark_matter",
    )

    for _, row in filtered_map_df.iterrows():
        risk = row["Risk Score"]

        if risk >= 8:
            color = "red"
        elif risk >= 5:
            color = "orange"
        elif risk >= 3:
            color = "yellow"
        else:
            color = "green"

        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=max(risk * 2, 6),
            popup=(
                f"<b>Type:</b> {row['Type']}<br>"
                f"<b>Location:</b> {row['Location']}<br>"
                f"<b>Risk Score:</b> {row['Risk Score']}<br>"
                f"<b>Severity:</b> {row['Severity']}"
            ),
            color=color,
            fill=True,
            fill_opacity=0.75,
        ).add_to(risk_map)

    st_folium(risk_map, width=1400, height=600)

    # -----------------------------
    # WEATHER TABLE
    # -----------------------------
    st.subheader("Regional Weather Monitoring")

    weather_display = weather_df[
        ["Location", "Temperature", "Wind Speed", "Precipitation", "Risk Score", "Severity"]
    ]

    styled_weather = weather_display.style.map(
        color_severity,
        subset=["Severity"],
    )

    st.dataframe(styled_weather, width="stretch", hide_index=True)

    # -----------------------------
    # NEWS TABLE
    # -----------------------------
    st.subheader("Geopolitical & Supply Chain Signal Feed")

    if news_df.empty:
        st.warning("No geopolitical or supply chain news signals detected.")
    else:
        styled_news = news_df.style.map(
            color_severity,
            subset=["Severity"],
        )
        st.dataframe(styled_news, width="stretch", hide_index=True)

    # -----------------------------
    # OPERATIONAL SUMMARY
    # -----------------------------
    st.subheader("AI Operational Summary")

    if not feed_df.empty:
        top_event = feed_df.sort_values("Risk Score", ascending=False).iloc[0]

        st.info(
            f"""
            Elevated operational risk detected from **{top_event['Type']}**
            near **{top_event['Location']}**.

            AxiomSignal is monitoring seismic, weather, and geopolitical disruption
            indicators across major Latin American logistics corridors and
            infrastructure hubs. Operators should review affected corridors, monitor
            nearby assets, and prepare contingency plans where risk remains elevated.
            """
        )
    else:
        st.success(
            "No elevated operational risks currently detected under the selected filters."
        )

except Exception as e:
    st.error(f"Unable to load live operational data: {e}")