import streamlit as st
import requests
import json
from datetime import datetime, time
from zoneinfo import ZoneInfo
import sys
import os
from types import SimpleNamespace

# Ensure the engine can be imported
sys.path.append(os.getcwd())

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Phoenix Console",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme & South Indian Chart CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stButton>button { background-color: #e85a30; color: white; border: none; border-radius: 4px; }
    .chart-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        grid-template-rows: 1fr 1fr 1fr 1fr;
        gap: 2px;
        background-color: #444;
        border: 2px solid #e85a30;
        width: 100%;
        aspect-ratio: 1/1;
        max-width: 500px;
        margin: 0 auto;
        font-family: sans-serif;
    }
    .house {
        background-color: #1a1a1c;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-size: 0.85em;
        padding: 2px;
        text-align: center;
        position: relative;
        min-height: 80px;
    }
    .house-num {
        position: absolute;
        bottom: 2px;
        right: 4px;
        font-size: 0.6em;
        color: #666;
        text-transform: uppercase;
    }
    .center-space {
        grid-column: 2 / 4;
        grid-row: 2 / 4;
        background-color: #0e1117;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        border: 1px solid #333;
    }
    .planet { font-weight: bold; color: #e0e0e0; }
    .asc { color: #e85a30; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC ---
def search_city(query):
    if len(query) < 2: return []
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language=en&format=json"
        res = requests.get(url, timeout=5).json()
        return res.get("results", [])
    except:
        return []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🦅 Phoenix")
    st.caption("Cosmic Engine V13")
    
    name = st.text_input("Name", "Client")
    
    st.subheader("📍 Location")
    city_query = st.text_input("City Search", placeholder="e.g. Tehran")
    
    selected_city = None
    if city_query:
        results = search_city(city_query)
        if results:
            opts = {f"{r['name']}, {r.get('country')}": r for r in results}
            sel = st.selectbox("Select:", opts.keys())
            selected_city = opts[sel]
            if selected_city:
                st.caption(f"TZ: {selected_city['timezone']}")
    
    st.subheader("📅 Birth Data")
    b_date = st.date_input(
        "Date",
        value=datetime(1990, 1, 1),
        min_value=datetime(1900, 1, 1),
        max_value=datetime(2100, 12, 31)
    )
    b_time = st.time_input("Time", time(12, 0, 0), step=1)
    
    calc = st.button("Calculate Chart", use_container_width=True)

# --- 4. MAIN DISPLAY ---
if calc and selected_city:
    try:
        from phoenix_engine.engines.birth import BirthChartEngine
        
        # Prepare Inputs
        tz = ZoneInfo(selected_city['timezone'])
        dt = datetime.combine(b_date, b_time).replace(tzinfo=tz)
        lat, lon = selected_city['latitude'], selected_city['longitude']
        
        with st.spinner("Aligning Stars..."):
            # Convert dict config to Object for the Engine
            output_config = SimpleNamespace(
                include_doshas=True,
                include_shadbala=True,
                include_vargas=True
            )
            config = SimpleNamespace(output=output_config)

            engine = BirthChartEngine(dt, lat, lon, config=config)
            res = engine.process().dict()
            
        # South Indian Chart Logic
        # Fixed Signs: 1=Aries ... 12=Pisces
        # Grid Mapping (Row, Col) for 4x4 Grid
        # 0,0=Pisces(12) | 0,1=Aries(1)  | 0,2=Taurus(2) | 0,3=Gemini(3)
        # 1,0=Aqu(11)    |               |               | 1,3=Can(4)
        # 2,0=Cap(10)    |    CENTER     |               | 2,3=Leo(5)
        # 3,0=Sag(9)     | 3,1=Sco(8)    | 3,2=Lib(7)    | 3,3=Vir(6)
        
        # We need a flat list of 12 HTML strings for the 12 signs
        signs_html = {i: [] for i in range(1, 13)}
        
        # Add Ascendant
        asc_sign = int(res['ascendant'] / 30) + 1
        signs_html[asc_sign].append('<span class="asc">ASC</span>')
        
        # Add Planets
        for p, data in res['grahas'].items():
            s = data['sign_id']
            p_short = p[:2].capitalize()
            signs_html[s].append(f'<span class="planet">{p_short}</span>')
            
        def get_content(sign_id):
            return "<br>".join(signs_html[sign_id])

        # Render Grid
        html = f"""
        <div class="chart-grid">
            <div class="house">{get_content(12)}<span class="house-num">Pisces</span></div>
            <div class="house">{get_content(1)}<span class="house-num">Aries</span></div>
            <div class="house">{get_content(2)}<span class="house-num">Taurus</span></div>
            <div class="house">{get_content(3)}<span class="house-num">Gemini</span></div>
            
            <div class="house">{get_content(11)}<span class="house-num">Aqua</span></div>
            <div class="center-space">
                <h2>{name}</h2>
                <p>{dt.strftime('%Y-%m-%d %H:%M')}</p>
                <p>{selected_city['name']}</p>
            </div>
            <div class="house">{get_content(4)}<span class="house-num">Cancer</span></div>
            
            <div class="house">{get_content(10)}<span class="house-num">Capri</span></div>
            <div class="house">{get_content(5)}<span class="house-num">Leo</span></div>
            
            <div class="house">{get_content(9)}<span class="house-num">Sagit</span></div>
            <div class="house">{get_content(8)}<span class="house-num">Scorpio</span></div>
            <div class="house">{get_content(7)}<span class="house-num">Libra</span></div>
            <div class="house">{get_content(6)}<span class="house-num">Virgo</span></div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        
        # Data Table
        st.divider()
        cols = st.columns(4)
        cols[0].metric("Ascendant", f"{res['ascendant']:.2f}°")
        cols[1].metric("Moon Sign", res['grahas']['moon']['sign'])
        cols[2].metric("Nakshatra", res['panchanga']['nakshatra']['name'])
        
        manglik = res.get('dosha', {}).get('manglik', {}).get('is_present', False)
        cols[3].metric("Manglik", "Yes" if manglik else "No", delta_color="inverse" if manglik else "normal")

    except Exception as e:
        st.error(f"Engine Error: {e}")

elif calc and not selected_city:
    st.warning("Please select a city first!")
else:
    st.info("Enter details in the sidebar to generate the chart.")
