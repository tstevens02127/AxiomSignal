import streamlit as st
import pandas as pd
import folium
import requests

from datetime import datetime
from streamlit_folium import st_folium
from openai import OpenAI

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None


st.set_page_config(
    page_title="AxiomSignal",
    page_icon="📡",
    layout="wide"
)

if st_autorefresh:
    st_autorefresh(interval=300000, key="axiomsignal_refresh")


client = OpenAI(
    api_key=st.secrets.get("XAI_API_KEY", ""),
    base_url="https://api.x.ai/v1",
)


# -----------------------------
# HELPERS
# -----------------------------

def risk_label(score):
    if score >= 8:
        return "Critical"
    if score >= 5:
        return "Elevated"
    if score >= 3:
        return "Moderate"
    return "Low"


def risk_alert(score, message):
    if score >= 8:
        st.error(message)
    elif score >= 5:
        st.warning(message)
    elif score >= 3:
        st.info(message)
    else:
        st.success(message)


def earthquake_risk_score(magnitude):
    if magnitude >= 7:
        return 10
    if magnitude >= 6:
        return 8
    if magnitude >= 5:
        return 6
    if magnitude >= 4:
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

def calculate_port_exposure(ports_df, top_event):
    ports = ports_df.copy()

    event_lat = float(top_event["Latitude"])
    event_lon = float(top_event["Longitude"])

    ports["Distance Score"] = (
        abs(ports["Latitude"] - event_lat)
        + abs(ports["Longitude"] - event_lon)
    )

    base_risk = int(top_event["Risk Score"])

    base_risk = int(top_event["Risk Score"])

    ports["Exposure Score"] = ports["Distance Score"].apply(
        lambda x: max(
            1,
            min(10, int(base_risk + 3 - (x / 15)))
        )
)

    ports["Exposure Level"] = ports["Exposure Score"].apply(risk_label)

    return ports.sort_values("Exposure Score", ascending=False)

# -----------------------------
# DATA FETCHING
# -----------------------------

@st.cache_data(ttl=300)
def fetch_earthquakes():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_week.geojson"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        quake_data = response.json()
    except Exception:
        return pd.DataFrame(columns=[
            "Type", "Location", "Magnitude", "Temperature", "Wind Speed",
            "Precipitation", "Risk Score", "Severity", "Latitude", "Longitude"
        ])

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

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            weather_data = response.json()
            current = weather_data.get("current", {})
        except Exception:
            current = {}

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


@st.cache_data(ttl=1800)
def fetch_news():
    url = "https://api.gdeltproject.org/api/v2/doc/doc"

    params = {
        "query": "logistics OR shipping OR port OR earthquake OR infrastructure",
        "mode": "ArtList",
        "format": "json",
        "maxrecords": 10,
        "sort": "HybridRel",
    }

    columns = ["Headline", "Source Country", "URL"]

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 429:
            return pd.DataFrame(columns=columns)

        response.raise_for_status()

        if not response.text.strip():
            return pd.DataFrame(columns=columns)

        try:
            news_data = response.json()
        except Exception:
            return pd.DataFrame(columns=columns)

        rows = []

        for article in news_data.get("articles", []):
            rows.append({
                "Headline": article.get("title", ""),
                "Source Country": article.get("sourceCountry", ""),
                "URL": article.get("url", "")
            })

        return pd.DataFrame(rows)

    except Exception:
        return pd.DataFrame(columns=columns)

def get_major_ports():
    return pd.DataFrame([
        {
            "Port": "Port of Santos",
            "Country": "Brazil",
            "Latitude": -23.95,
            "Longitude": -46.33,
            "Importance": "Critical"
        },
        {
            "Port": "Port of Callao",
            "Country": "Peru",
            "Latitude": -12.05,
            "Longitude": -77.15,
            "Importance": "Critical"
        },
        {
            "Port": "Port of Valparaiso",
            "Country": "Chile",
            "Latitude": -33.03,
            "Longitude": -71.63,
            "Importance": "High"
        },
        {
            "Port": "Port of Cartagena",
            "Country": "Colombia",
            "Latitude": 10.40,
            "Longitude": -75.53,
            "Importance": "High"
        },
        {
            "Port": "Port of Buenaventura",
            "Country": "Colombia",
            "Latitude": 3.88,
            "Longitude": -77.03,
            "Importance": "High"
        }
    ])

# -----------------------------
# AI FUNCTIONS
# -----------------------------

def generate_ai_summary(top_risk):
    prompt = f"""
    You are an AI operational intelligence analyst for Latin American logistics infrastructure.

    Analyze this operational threat:

    {top_risk}

    Provide:
    1. Operational risk assessment
    2. Potential supply chain impact
    3. Recommended action

    Keep response concise and executive-level.
    """

    try:
        response = client.chat.completions.create(
            model="grok-3-mini",
            messages=[
                {"role": "system", "content": "You are a logistics intelligence analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content

    except Exception:
        return "AI summary temporarily unavailable. Continue monitoring live risk indicators and operational alerts."


def generate_route_impact_analysis(top_risk):
    prompt = f"""
    You are a global logistics corridor intelligence analyst.

    Analyze this operational threat:

    {top_risk}

    Identify:
    1. Ports potentially affected
    2. Shipping lanes at risk
    3. Supply chain corridors exposed
    4. Expected operational delays
    5. Recommended rerouting strategies

    Keep response operational, concise, and executive-level.
    """

    try:
        response = client.chat.completions.create(
            model="grok-3-mini",
            messages=[
                {"role": "system", "content": "You are a logistics corridor intelligence analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content

    except Exception:
        return "Route impact intelligence temporarily unavailable."


def generate_ai_adjusted_score(top_risk):
    prompt = f"""
    You are an operational risk scoring analyst.

    Review this event:

    {top_risk}

    Return ONLY a single integer from 1 to 10 representing adjusted operational risk.
    Consider proximity to ports, maritime corridors, logistics infrastructure, tsunami risk,
    weather exposure, and supply chain impact.
    """

    try:
        response = client.chat.completions.create(
            model="grok-3-mini",
            messages=[
                {"role": "system", "content": "Return only one integer from 1 to 10."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        score_text = response.choices[0].message.content.strip()
        return max(1, min(10, int(score_text)))

    except Exception:
        return int(top_risk["Risk Score"])


# -----------------------------
# APP HEADER
# -----------------------------

st.title("📡 AxiomSignal")
st.caption("Predictive Operational Intelligence for Latin American Logistics & Infrastructure")

st.subheader("Real-Time Risk Monitoring Across Critical Supply Chain Corridors")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.success("System operational.")


# -----------------------------
# LOAD DATA
# -----------------------------

earthquake_df = fetch_earthquakes()
weather_df = fetch_weather()
news_df = fetch_news()
ports_df = get_major_ports()

data = pd.concat([earthquake_df, weather_df], ignore_index=True)


# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.header("Filters")

min_risk = st.sidebar.slider(
    "Minimum Risk Score",
    min_value=1,
    max_value=10,
    value=1
)

event_types = st.sidebar.multiselect(
    "Event Types",
    ["Earthquake", "Weather"],
    default=["Earthquake", "Weather"]
)

filtered_data = data[
    (data["Risk Score"] >= min_risk)
    & (data["Type"].isin(event_types))
]


if filtered_data.empty:
    st.warning("No operational risk events match current filters.")
    st.stop()


top_event = filtered_data.sort_values(
    by="Risk Score",
    ascending=False
).iloc[0]

port_exposure_df = calculate_port_exposure(ports_df, top_event)

highest_score = int(filtered_data["Risk Score"].max())
highest_risk = highest_score
status = "Elevated" if highest_score >= 6 else "Normal"
ai_score = generate_ai_adjusted_score(top_event)


# -----------------------------
# METRICS
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Live Risk Events", len(filtered_data))

with col2:
    st.metric("Highest Risk Score", highest_score)

with col3:
    st.metric("Operational Status", status)

with col4:
    st.metric("AI Adjusted Score", ai_score)


st.divider()


# -----------------------------
# NEWS
# -----------------------------

st.subheader("Live News Intelligence Feed")

if news_df.empty:
    st.warning("No live news intelligence signals detected.")
else:
    for _, row in news_df.iterrows():
        st.markdown(
            f"""
            ### [{row['Headline']}]({row['URL']})

            Source Country: {row['Source Country']}
            """
        )
        st.divider()


st.subheader("News-Based Operational Intelligence")

if news_df.empty:
    st.info("No current news-based operational risks detected across monitored logistics corridors.")
else:
    top_headline = news_df.iloc[0]["Headline"]
    source_country = news_df.iloc[0]["Source Country"]

    st.warning(
        f"""
        Emerging news signal detected from {source_country}: {top_headline}

        Recommended action: monitor for potential downstream effects on port operations,
        cross-border logistics, shipping schedules, and regional infrastructure reliability.
        """
    )


# -----------------------------
# AI INTELLIGENCE
# -----------------------------

st.subheader("AI Operational Intelligence Summary")

summary = generate_ai_summary(top_event)
risk_alert(highest_risk, summary)

route_analysis = generate_route_impact_analysis(top_event)

st.subheader("AI Route & Corridor Impact Analysis")
st.warning(route_analysis)

risk_alert(
    top_event["Risk Score"],
    f"Top Active Threat: {top_event['Type']} detected near {top_event['Location']} with risk score {top_event['Risk Score']}."
)


st.subheader("Recommended Operational Actions")

if top_event["Risk Score"] >= 8:
    action = f"""
    Immediate action recommended: monitor assets near {top_event['Location']},
    review contingency routing, and alert operations teams responsible for exposed corridors.
    """
elif top_event["Risk Score"] >= 5:
    action = f"""
    Elevated monitoring recommended near {top_event['Location']}.
    Review affected routes and maintain readiness for operational adjustments.
    """
else:
    action = "No immediate intervention required. Continue routine monitoring."

risk_alert(top_event["Risk Score"], action)


# -----------------------------
# EXECUTIVE BRIEFING
# -----------------------------

st.subheader("Executive Intelligence Briefing")

briefing = f"""
# AxiomSignal Executive Briefing

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Operational Status
{status}

## Highest Operational Risk
{top_event['Type']} near {top_event['Location']}

## System Risk Score
{top_event['Risk Score']}

## AI Adjusted Risk Score
{ai_score}

## AI Operational Summary
{summary}

## Route & Corridor Impact Analysis
{route_analysis}

## Recommended Actions
{action}

Generated by AxiomSignal AI.
"""

st.download_button(
    label="Download Executive Briefing",
    data=briefing,
    file_name="axiomsignal_executive_briefing.txt",
    mime="text/plain"
)


st.divider()


# -----------------------------
# DATA TABLE
# -----------------------------

st.subheader("Live Operational Risk Feed")

display_columns = [
    "Type",
    "Location",
    "Magnitude",
    "Temperature",
    "Wind Speed",
    "Precipitation",
    "Risk Score",
    "Severity",
    "Latitude",
    "Longitude",
]

st.dataframe(
    filtered_data[display_columns],
    use_container_width=True
)


# -----------------------------
# MAP
# -----------------------------

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

st.subheader("Strategic Maritime Infrastructure")

st.dataframe(
    ports_df,
    use_container_width=True
)

st.subheader("Port Exposure Scoring")

st.dataframe(
    port_exposure_df,
    use_container_width=True
)

# -----------------------------
# WEATHER TABLE
# -----------------------------

st.subheader("Regional Weather Monitoring")

st.dataframe(
    weather_df[
        ["Location", "Temperature", "Wind Speed", "Precipitation", "Risk Score", "Severity"]
    ],
    use_container_width=True
)