import streamlit as st
import pandas as pd
import requests
import folium

from datetime import datetime
from streamlit_folium import st_folium

col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.image(
        "assets/AxiomSignal transparent.png",
        width=450
    )

st.set_page_config(page_title="AxiomSignal", layout="wide")

st.caption(
    "Predictive Operational Intelligence for Latin American Logistics & Infrastructure"
)

st.subheader(
    "Real-Time Risk Monitoring Across Critical Supply Chain Corridors"
)

st.caption(
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

st.info(
    """
    AxiomSignal provides real-time operational risk intelligence
    for Latin American logistics and infrastructure operators.
    """
)

st.markdown(
    """
    ### Monitored Risk Categories

    - Seismic Activity
    - Severe Weather
    - Infrastructure Disruption
    - Geopolitical Events
    - Supply Chain Volatility
    """
)

st.sidebar.header("Filters")

min_risk = st.sidebar.slider("Minimum Risk Score", 1, 10, 5)


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
    else:
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
    else:
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
    ]

    score = 3

    for keyword in high_risk_keywords:
        if keyword in title:
            score += 2

    return min(score, 10)


def color_severity(val):
    if val == "Critical":
        return "background-color: #ff4b4b; color: white"
    elif val == "Elevated":
        return "background-color: #ffa500; color: black"
    elif val == "Moderate":
        return "background-color: #ffe066; color: black"
    else:
        return "background-color: #4caf50; color: white"


# -----------------------------
# EARTHQUAKE DATA
# -----------------------------
@st.cache_data(ttl=300)
def fetch_earthquakes():
    url = (
        "https://earthquake.usgs.gov/"
        "earthquakes/feed/v1.0/"
        "summary/4.5_week.geojson"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    rows = []

    for feature in data["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]

        magnitude = props.get("mag", 0)
        latitude = coords[1]
        longitude = coords[0]

        # Focus on LatAm + Pacific logistics corridor
        if not (-60 <= latitude <= 35 and -150 <= longitude <= -30):
            continue

        score = earthquake_risk_score(magnitude)

        rows.append(
            {
                "Type": "Earthquake",
                "Location": props.get("place", ""),
                "Risk Score": score,
                "Severity": risk_label(score),
                "Magnitude": magnitude,
                "Latitude": latitude,
                "Longitude": longitude,
            }
        )

    return pd.DataFrame(rows)


# -----------------------------
# WEATHER DATA
# -----------------------------
@st.cache_data(ttl=1800)
def fetch_weather():
    locations = [
        {"name": "Santiago", "lat": -33.45, "lon": -70.66},
        {"name": "Valparaiso", "lat": -33.04, "lon": -71.63},
        {"name": "Lima", "lat": -12.05, "lon": -77.04},
        {"name": "Santos Port", "lat": -23.96, "lon": -46.33},
    ]

    rows = []

    for loc in locations:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={loc['lat']}&longitude={loc['lon']}"
            f"&current=temperature_2m,precipitation,wind_speed_10m"
        )

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        current = data["current"]

        wind_speed = current.get("wind_speed_10m", 0)
        precipitation = current.get("precipitation", 0)
        score = weather_risk_score(wind_speed, precipitation)

        rows.append(
            {
                "Type": "Weather",
                "Location": loc["name"],
                "Temperature": current.get("temperature_2m", 0),
                "Wind Speed": wind_speed,
                "Precipitation": precipitation,
                "Risk Score": score,
                "Severity": risk_label(score),
                "Latitude": loc["lat"],
                "Longitude": loc["lon"],
            }
        )

    return pd.DataFrame(rows)


# -----------------------------
# GDELT NEWS / DISRUPTION DATA
# -----------------------------
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
        columns=[
            "Type",
            "Location",
            "Headline",
            "Risk Score",
            "Severity",
            "URL",
        ]
    )

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        if not response.text.strip():
            return empty_df

        data = response.json()
        articles = data.get("articles", [])

        rows = []

        for article in articles:
            title = article.get("title", "")
            source_country = article.get("sourceCountry", "LatAm")
            article_url = article.get("url", "")
            score = news_risk_score(title)

            rows.append(
                {
                    "Type": "News / Geopolitical",
                    "Location": source_country,
                    "Headline": title,
                    "Risk Score": score,
                    "Severity": risk_label(score),
                    "URL": article_url,
                }
            )

        return pd.DataFrame(rows)

    except Exception:
        return empty_df


# -----------------------------
# LOAD DATA
# -----------------------------
try:
    eq_df = fetch_earthquakes()
    weather_df = fetch_weather()
    news_df = fetch_gdelt_news()

    map_df = pd.concat(
        [
            eq_df[
                [
                    "Type",
                    "Location",
                    "Risk Score",
                    "Severity",
                    "Latitude",
                    "Longitude",
                ]
            ],
            weather_df[
                [
                    "Type",
                    "Location",
                    "Risk Score",
                    "Severity",
                    "Latitude",
                    "Longitude",
                ]
            ],
        ],
        ignore_index=True,
    )

    filtered_map_df = map_df[map_df["Risk Score"] >= min_risk]

    combined_feed = pd.concat(
        [
            map_df[
                [
                    "Type",
                    "Location",
                    "Risk Score",
                    "Severity",
                ]
            ],
            news_df[
                [
                    "Type",
                    "Location",
                    "Risk Score",
                    "Severity",
                    "Headline",
                    "URL",
                ]
            ],
        ],
        ignore_index=True,
    )

    combined_feed = combined_feed[combined_feed["Risk Score"] >= min_risk]

    col1, col2, col3 = st.columns(3)

    col1.metric("Live Risk Events", len(combined_feed))

    col2.metric(
        "Highest Risk Score",
        int(combined_feed["Risk Score"].max()) if not combined_feed.empty else 0,
    )

    col3.metric(
        "Operational Status",
        "Elevated" if not combined_feed.empty else "Normal",
    )

    st.divider()

    st.subheader("Live Operational Risk Feed")

    styled_feed = combined_feed.style.map(
        color_severity,
        subset=["Severity"],
    )

    st.dataframe(styled_feed, width="stretch")

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
        else:
            color = "green"

        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=risk * 2,
            popup=(
                f"<b>Type:</b> {row['Type']}<br>"
                f"<b>Location:</b> {row['Location']}<br>"
                f"<b>Risk Score:</b> {row['Risk Score']}<br>"
                f"<b>Severity:</b> {row['Severity']}"
            ),
            color=color,
            fill=True,
            fill_opacity=0.7,
        ).add_to(risk_map)

    st_folium(risk_map, width=1400, height=600)

    st.subheader("Regional Weather Monitoring")

    styled_weather = weather_df[
        [
            "Location",
            "Temperature",
            "Wind Speed",
            "Precipitation",
            "Risk Score",
            "Severity",
        ]
    ].style.map(
        color_severity,
        subset=["Severity"],
    )

    st.dataframe(styled_weather, width="stretch")

    st.subheader("Geopolitical & Supply Chain Signal Feed")

    if not news_df.empty:
        styled_news = news_df.style.map(
            color_severity,
            subset=["Severity"],
        )

        st.dataframe(styled_news, width="stretch")
    else:
        st.warning("No geopolitical or supply chain news signals detected.")

    st.subheader("AI Operational Summary")

    if not combined_feed.empty:
        top_event = combined_feed.sort_values("Risk Score", ascending=False).iloc[0]

        st.info(
            f"""
            Elevated operational risk detected from {top_event['Type']}
            near {top_event['Location']}.

            AxiomSignal is monitoring seismic, weather, and geopolitical disruption
            indicators across major Latin American logistics corridors and
            infrastructure hubs.
            """
        )
    else:
        st.success("No elevated operational risks detected.")

except Exception as e:
    st.error(f"Unable to load live operational data: {e}")