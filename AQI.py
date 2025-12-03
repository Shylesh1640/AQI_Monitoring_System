import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import geopandas as gpd
import json
import time



@st.cache_data
def get_india_outline():
    # Load the states GeoJSON into GeoPandas
    gdf = gpd.read_file(GEOJSON_URL)
    # Dissolve all states into one polygon (India outline)
    india_outline = gdf.dissolve(by=None)
    return json.loads(india_outline.to_json())




# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="India AQI Monitor",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# THEME SWITCH
# =============================
def get_theme_css(theme):
    if theme == "Dark":
        return """
        <style>
            body { background-color: #0e1117 !important; color: white !important; }
            .block-container { background-color: #0e1117; }
            div[data-testid="stMetric"] {
                background-color: #1b1e27 !important;
                border: 1px solid #333 !important;
                color: white !important;
            }
        </style>
        """
    else:
        return """
        <style>
            body { background-color: white !important; color: black !important; }
            .block-container { background-color: white; }
            div[data-testid="stMetric"] {
                background-color: #f9f9f9 !important;
                border: 1px solid #e0e0e0 !important;
                color: black !important;
            }
        </style>
        """

if "theme" not in st.session_state:
    st.session_state.theme = "Auto"

auto_detect_theme = """
<script>
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
if (prefersDark) {
    window.parent.document.documentElement.setAttribute('data-theme', 'dark');
} else {
    window.parent.document.documentElement.setAttribute('data-theme', 'light');
}
</script>
"""

if st.session_state.theme == "Auto":
    st.markdown(auto_detect_theme, unsafe_allow_html=True)
    st.markdown(get_theme_css("Dark"), unsafe_allow_html=True)  # fallback
else:
    st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# =============================
# AQI API + GEOJSON CONFIG
# =============================
API_KEY = "b79fa81264294ca16e11de1af9e0bfac9fb5a9d8"

CITY_TO_STATE = {
    "Delhi": "NCT of Delhi", "Mumbai": "Maharashtra", "Chennai": "Tamil Nadu",
    "Kolkata": "West Bengal", "Bengaluru": "Karnataka", "Hyderabad": "Telangana",
    "Ahmedabad": "Gujarat", "Pune": "Maharashtra", "Jaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh", "Coimbatore": "Tamil Nadu", "Madurai": "Tamil Nadu",
    "Chandigarh": "Chandigarh", "Visakhapatnam": "Andhra Pradesh", "Kochi": "Kerala",
    "Patna": "Bihar", "Indore": "Madhya Pradesh", "Bhopal": "Madhya Pradesh",
    "Nagpur": "Maharashtra", "Guwahati": "Assam",
}

GEOJSON_URL = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

@st.cache_data
def load_geojson():
    return requests.get(GEOJSON_URL).json()

# 🆕 Dissolve state polygons into one India outline
@st.cache_data
def get_india_outline():
    gdf = gpd.read_file(GEOJSON_URL)
    india_outline = gdf.dissolve(by=None)  # merge all states
    return json.loads(india_outline.to_json())

# =============================
# FETCH AQI DATA
# =============================
def fetch_aqi(city):
    url = f"https://api.waqi.info/feed/{city}/?token={API_KEY}"
    try:
        res = requests.get(url).json()
        if res["status"] == "ok":
            val = res["data"]["aqi"]
            if isinstance(val, (int, float)):
                return val
            if isinstance(val, str) and val.replace(".", "", 1).isdigit():
                return float(val)
    except:
        return None
    return None

@st.cache_data(ttl=900)
def get_aqi_data():
    rows = []
    for city, state in CITY_TO_STATE.items():
        aqi = fetch_aqi(city)
        if aqi is not None:
            rows.append({"City": city, "State": state, "AQI": aqi})

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    state_df = df.groupby("State", as_index=False)["AQI"].mean().round(0)
    return df, state_df

# =============================
# DASHBOARD
# =============================
@st.fragment(run_every="15m")
def render_dashboard():
    df_city, df_states = get_aqi_data()
    india_geojson = load_geojson()
    india_outline = get_india_outline()

    if df_states.empty:
        st.error("Unable to fetch AQI data.")
        return

    avg_aqi = int(df_city["AQI"].mean())
    worst = df_city.loc[df_city["AQI"].idxmax()]
    best = df_city.loc[df_city["AQI"].idxmin()]

    st.markdown("## 🇮🇳 India Air Quality Dashboard")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("National Avg", avg_aqi)
    k2.metric("Most Polluted", worst["City"], f"{worst['AQI']} AQI")
    k3.metric("Cleanest City", best["City"], f"{best['AQI']} AQI")
    k4.metric("Cities Monitored", len(df_city))

    st.markdown("---")

    left, right = st.columns([1, 2])

    with left:
        st.subheader("📊 State AQI Ranking")
        df_sorted = df_states.sort_values("AQI", ascending=False)
        st.dataframe(df_sorted, use_container_width=True, height=550)

    with right:
        st.subheader("🗺️ India AQI Heatmap")

        fig = px.choropleth_mapbox(
            df_states,
            geojson=india_geojson,
            locations="State",
            featureidkey="properties.ST_NM",
            color="AQI",
            mapbox_style="carto-positron",
            zoom=3.6,
            center={"lat": 22.5, "lon": 82.0},
            opacity=0.7,
            color_continuous_scale=[
                (0.0, "#00e400"),
                (0.17, "#ffff00"),
                (0.33, "#ff7e00"),
                (0.50, "#ff0000"),
                (0.66, "#8f3f97"),
                (1.0, "#7e0023")
            ],
        )

        # State borders
        fig.update_traces(marker_line_width=1.5, marker_line_color="black")

        # 🆕 Add dissolved India outline with THICK border
        india_outline = get_india_outline()
        outline_trace = px.choropleth_mapbox(
            geojson=india_outline,
            locations=["India"],  # dummy
            featureidkey="properties.ST_NM",
            color_discrete_sequence=["rgba(0,0,0,0)"]  # transparent fill
        ).data[0]

        outline_trace.marker.line.width = 8   # 🔥 thick border
        outline_trace.marker.line.color = "black"

        fig.add_trace(outline_trace)

        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)


# RUN DASHBOARD
render_dashboard()
