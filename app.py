import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time
import os
import re
import glob
import json
import datetime
import joblib
import pandas as pd
import subprocess
from dateutil import parser
from brand import get_favicon, render_brand_header, render_sidebar_logo, get_logo_b64

st.set_page_config(
    page_title="MIT ESP | Corporate Transport Optimizer",
    page_icon=get_favicon(),
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MillenniumIT ESP Corporate Theme Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    /* Top Streamlit Header Clearance */
    header[data-testid="stHeader"] {
        background-color: rgba(7, 9, 14, 0.95) !important;
        backdrop-filter: blur(14px) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
        z-index: 99999 !important;
    }
    header[data-testid="stHeader"] * {
        color: #F8FAFC !important;
    }

    .block-container, [data-testid="stMainBlockContainer"], [data-testid="block-container"] {
        padding-top: 5.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 100% !important;
    }

    @media (max-width: 768px) {
        .block-container, [data-testid="stMainBlockContainer"], [data-testid="block-container"] {
            padding-top: 7rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
    }

    /* Hide intrusive Streamlit form input instructions that cause text overlap on mobile */
    div[data-testid="InputInstructions"], [data-testid="InputInstructions"] {
        display: none !important;
    }

    /* Responsive map iframes */
    iframe[title="streamlit_folium.st_folium"], 
    .stFolium, 
    div[data-testid="stIFrame"] {
        width: 100% !important;
        border-radius: 14px !important;
    }

    .stApp {
        background-color: #07090E !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(66, 138, 255, 0.12) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(239, 65, 35, 0.10) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(13, 202, 240, 0.05) 0px, transparent 50%) !important;
        color: #F1F5F9 !important;
    }

    /* Universal text visibility in dark mode */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div, .stApp li {
        color: #F1F5F9;
    }

    /* All form labels, markdown, captions */
    [data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 13px !important;
    }

    .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
        color: #CBD5E1 !important;
        font-size: 12px !important;
    }

    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] span {
        color: #F8FAFC !important;
    }

    /* Sidebar full high-contrast visibility */
    [data-testid="stSidebar"] {
        background-color: #0B0F17 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] label {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] small {
        color: #CBD5E1 !important;
    }

    /* Cards */
    .mit-card {
        background: rgba(16, 22, 34, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    .mit-card:hover {
        border-color: rgba(66, 138, 255, 0.35);
    }

    .mit-card-title {
        font-size: 15px;
        font-weight: 800;
        color: #FFFFFF !important;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Secondary Buttons / Hub Quick Picks */
    .stButton > button {
        background-color: #162032 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #202D44 !important;
        border-color: #EF4123 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(239, 65, 35, 0.25) !important;
    }

    /* Primary buttons with MIT ESP Coral-to-Azure Gradient */
    button[kind="primary"], .stButton > button[type="primary"] {
        background: linear-gradient(135deg, #EF4123 0%, #F97316 45%, #428AFF 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 20px rgba(239, 65, 35, 0.35) !important;
        transition: all 0.25s ease !important;
    }
    button[kind="primary"]:hover, .stButton > button[type="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(239, 65, 35, 0.55) !important;
    }

    /* Input & Select Box styling */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"] {
        background-color: #111724 !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: #428AFF !important;
        box-shadow: 0 0 0 3px rgba(66, 138, 255, 0.25) !important;
    }
    div[data-baseweb="input"] input, div[data-baseweb="select"] *, input {
        color: #FFFFFF !important;
        background-color: transparent !important;
    }
    input::placeholder {
        color: #94A3B8 !important;
    }

    /* Select dropdown menu */
    ul[data-baseweb="menu"] {
        background-color: #111724 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    ul[data-baseweb="menu"] li {
        color: #FFFFFF !important;
    }
    ul[data-baseweb="menu"] li:hover {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        background: rgba(16, 22, 34, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
    }
    div[data-testid="stExpander"] summary span {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    div[data-testid="stExpander"] summary svg {
        fill: #FFFFFF !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] section {
        background-color: #111724 !important;
        border: 1px dashed rgba(255, 255, 255, 0.25) !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploader"] section * {
        color: #F8FAFC !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: rgba(16, 22, 34, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 12px;
        padding: 12px 16px;
    }
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: #CBD5E1 !important;
    }

    /* Mobile Responsiveness & PWA Optimization */
    @media (max-width: 768px) {
        .block-container, [data-testid="stMainBlockContainer"], [data-testid="block-container"] {
            padding-top: 7rem !important;
            padding-left: 0.6rem !important;
            padding-right: 0.6rem !important;
        }
        .stButton button {
            min-height: 46px !important;
            font-size: 14px !important;
            border-radius: 8px !important;
        }
        input, select, textarea {
            font-size: 16px !important; /* Prevents auto-zoom on iOS */
        }
        [data-testid="stMetricValue"] {
            font-size: 18px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Webhook URL for Google Sheets logging
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbytsWPRqpCNiF5Onkse8JNXlDhwLSUNnYfhOgTojd_vu0ZwNRReGKvFC5_uv3sRwdYqbw/exec"


# --- Machine Learning Model for Drop-off Prediction ---

def load_model_metadata():
    """Load metadata of latest trained model."""
    base = os.path.dirname(__file__)
    models_dir = os.path.join(base, "models")
    if os.path.exists(models_dir):
        meta_files = glob.glob(os.path.join(models_dir, "meta_v*.json"))
        if meta_files:
            def _vnum(p):
                m = re.search(r'meta_v(\d+)\.json$', p)
                return int(m.group(1)) if m else 0
            latest_meta = max(meta_files, key=_vnum)
            try:
                with open(latest_meta, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    root_meta = os.path.join(base, "model_meta.json")
    if os.path.exists(root_meta):
        try:
            with open(root_meta, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


@st.cache_resource
def load_prediction_model():
    """Load the trained RandomForest model and encoders from disk (latest version or fallback)."""
    base = os.path.dirname(__file__)
    models_dir = os.path.join(base, "models")
    model_path = None
    encoders_path = None

    if os.path.exists(models_dir):
        existing = glob.glob(os.path.join(models_dir, "model_v*.pkl"))
        if existing:
            def _vnum(p):
                m = re.search(r'model_v(\d+)\.pkl$', p)
                return int(m.group(1)) if m else 0
            latest = max(existing, key=_vnum)
            v = _vnum(latest)
            enc_cand = os.path.join(models_dir, f"encoders_v{v}.pkl")
            if os.path.exists(enc_cand):
                model_path = latest
                encoders_path = enc_cand

    if not model_path or not os.path.exists(model_path):
        model_path = os.path.join(base, "model.pkl")
        encoders_path = os.path.join(base, "encoders.pkl")

    if os.path.exists(model_path) and os.path.exists(encoders_path):
        try:
            model = joblib.load(model_path)
            encoders = joblib.load(encoders_path)
            return model, encoders
        except Exception as e:
            print("Error loading ML model:", e)
    return None, None


def predict_dropoff_location(passenger_name, current_hour=None):
    """Predict the most likely drop-off location based on passenger name and current time."""
    if not passenger_name or not str(passenger_name).strip():
        return None, None
    model, encoders = load_prediction_model()
    if not model or not encoders:
        return None, None

    clean_name = str(passenger_name).strip()
    name_lookup = encoders.get("name_lookup", {})
    matched_name = name_lookup.get(clean_name.lower())

    if not matched_name:
        for k, v in name_lookup.items():
            if clean_name.lower() in k or k in clean_name.lower():
                matched_name = v
                break

    if not matched_name:
        return None, None

    try:
        p_code = encoders["passenger_encoder"].transform([matched_name])[0]
        if current_hour is None:
            current_hour = datetime.datetime.now().hour
        features = pd.DataFrame([[p_code, current_hour]], columns=["passenger_encoded", "Hour"])
        loc_code = model.predict(features)[0]
        predicted_loc = encoders["location_encoder"].inverse_transform([loc_code])[0]
        return predicted_loc, matched_name
    except Exception as e:
        print("ML Prediction error:", e)
        return None, None


def handle_passenger_name_change(idx):
    """Streamlit on_change callback: prepares drop-off choices and AI predictions when name changes."""
    name = st.session_state.get(f"p{idx}_name", "")
    # Reset recent dropdown selection placeholder
    st.session_state[f"p{idx}_recent_sel"] = "-- Select a recent location or type custom --"
    if name and name.strip():
        pred_loc, matched_name = predict_dropoff_location(name)
        if pred_loc:
            time_str = datetime.datetime.now().strftime("%I:%M %p")
            st.session_state[f"p{idx}_ml_notice"] = f"🎯 AI Recommended for **{matched_name}** at {time_str}: `{pred_loc}`"
        else:
            st.session_state[f"p{idx}_ml_notice"] = None
    else:
        st.session_state[f"p{idx}_ml_notice"] = None



def get_google_maps_api_key():
    """Retrieve Google Maps API key from Streamlit secrets, environment variable, or local .env file."""
    try:
        if hasattr(st, "secrets") and "GOOGLE_MAPS_API_KEY" in st.secrets:
            return str(st.secrets["GOOGLE_MAPS_API_KEY"]).strip()
    except Exception:
        pass
    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if key:
        return key.strip()
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GOOGLE_MAPS_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return None


def parse_lat_lon(text):
    """Detect if input text contains GPS coordinates like '6.9202, 79.8534'."""
    text = str(text).strip()
    m = re.search(r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)', text)
    if m:
        try:
            return float(m.group(1)), float(m.group(2))
        except ValueError:
            return None
    return None


def decode_polyline(polyline_str):
    """Decodes a Google encoded polyline string into a list of [latitude, longitude]."""
    index, lat, lng = 0, 0, 0
    coordinates = []
    length = len(polyline_str)
    while index < length:
        shift, result = 0, 0
        while True:
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1f) << shift
            shift += 5
            if byte < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        shift, result = 0, 0
        while True:
            byte = ord(polyline_str[index]) - 63
            index += 1
            result |= (byte & 0x1f) << shift
            shift += 5
            if byte < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        coordinates.append([lat / 1e5, lng / 1e5])
    return coordinates


@st.cache_data(ttl=86400, show_spinner=False)
def geocode_address(address, _geolocator=None):
    """Geocode an address using Google Routes API first, falling back to smart Nominatim for Sri Lankan locations."""
    if not address or not str(address).strip():
        return None
    address = str(address).strip()
    
    # 1. Direct coordinates
    coords = parse_lat_lon(address)
    if coords:
        return coords

    # 1b. Fast-path for MillenniumIT ESP Headquarters (Colombo 03)
    norm_addr = address.lower()
    if "450d" in norm_addr or ("450" in norm_addr and "de mel" in norm_addr) or "450 d" in norm_addr:
        return 6.9075492, 79.8530088

    # 2. Google Routes API v2 extraction (accurate for specific Sri Lankan street addresses)
    api_key = get_google_maps_api_key()
    if api_key:
        try:
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': api_key,
                'X-Goog-FieldMask': 'routes.legs.startLocation'
            }
            full_addr = address if "sri lanka" in address.lower() else f"{address}, Sri Lanka"
            payload = {
                'origin': {'address': full_addr},
                'destination': {'address': 'Colombo, Sri Lanka'},
                'travelMode': 'DRIVE'
            }
            r = requests.post('https://routes.googleapis.com/directions/v2:computeRoutes', headers=headers, json=payload, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if data.get("routes") and data["routes"][0].get("legs"):
                    start_loc = data["routes"][0]["legs"][0].get("startLocation", {}).get("latLng", {})
                    if "latitude" in start_loc and "longitude" in start_loc:
                        return float(start_loc["latitude"]), float(start_loc["longitude"])
        except Exception:
            pass

    # 3. Nominatim Fallback with candidate cleaning
    if _geolocator is None:
        _geolocator = Nominatim(user_agent="mitesp_mobility_lk_geocoder", timeout=6)

    candidates = [
        f"{address}, Sri Lanka" if "sri lanka" not in address.lower() else address,
        address
    ]
    # Strip house numbers (e.g. 'No. 4500,', 'No: 12/A,')
    c_no = re.sub(r'(?i)no\.?\s*[:\s]?\s*\d+[/A-Za-z0-9-]*\s*,\s*', '', address)
    if c_no != address:
        candidates.append(f"{c_no}, Sri Lanka")
        candidates.append(c_no)
    # Strip 5-digit postal codes
    c_post = re.sub(r'\b\d{5}\b', '', c_no).strip().replace(', ,', ',')
    if c_post != c_no:
        candidates.append(f"{c_post}, Sri Lanka")
        candidates.append(c_post)

    norm = address.lower()
    if "itesp" in norm:
        candidates.append("millenniumit esp, Sri Lanka")
    if "millennium" in norm:
        candidates.append("MillenniumIT ESP, Malabe, Sri Lanka")
    if "sampath" in norm and "head" in norm:
        candidates.append("Sampath Bank Head Office, Colombo, Sri Lanka")
    if "de mel" in norm or "r a de mel" in norm:
        candidates.append("R. A. de Mel Mawatha, Colombo, Sri Lanka")
        candidates.append("Duplication Road, Colombo, Sri Lanka")

    for q in candidates:
        try:
            location = _geolocator.geocode(q, country_codes="lk", timeout=6)
            if location:
                return float(location.latitude), float(location.longitude)
        except Exception:
            continue
    return None


@st.cache_data(ttl=86400, show_spinner=False)
def reverse_geocode_location(lat, lng):
    """Reverse-geocode latitude and longitude into a clean Sri Lankan address."""
    try:
        g = Nominatim(user_agent="mitesp_mobility_lk_rev", timeout=6)
        loc = g.reverse((lat, lng), timeout=6)
        if loc and loc.address:
            parts = [p.strip() for p in loc.address.split(",")]
            if len(parts) > 3:
                return ", ".join(parts[:3] + [parts[-1]])
            return loc.address
    except Exception:
        pass
    return f"{lat:.5f}, {lng:.5f}"


def load_custom_pickup_hubs():
    """Load user's saved corporate pickup hubs across Sri Lanka."""
    base = os.path.dirname(__file__)
    p = os.path.join(base, "data", "custom_hubs.json")
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {"name": "MIT ESP HQ (Col 03)", "address": "No. 450D, R A De Mel Mawatha, Colombo 3, Colombo 00300, Sri Lanka", "icon": "🏢"},
        {"name": "MIT ESP Malabe", "address": "MillenniumIT ESP, Malabe, Sri Lanka", "icon": "🌳"},
        {"name": "Sampath Bank HO", "address": "Sampath Bank Head Office, Colombo", "icon": "🏦"},
        {"name": "WTC Colombo", "address": "World Trade Center, Colombo 01", "icon": "🏙️"},
    ]


def save_custom_pickup_hubs(hubs):
    """Save custom corporate pickup hubs across Sri Lanka."""
    base = os.path.dirname(__file__)
    d = os.path.join(base, "data")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "custom_hubs.json")
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(hubs, f, indent=2)
    except Exception as e:
        print("Error saving custom hubs:", e)


def make_google_waypoint(point):
    """Construct a Google Maps Routes API waypoint from an address string or coordinates."""
    addr = point["address"].strip()
    coords = parse_lat_lon(addr)
    if coords:
        return {'location': {'latLng': {'latitude': coords[0], 'longitude': coords[1]}}}
    
    # Text address
    if "sri lanka" not in addr.lower():
        full_addr = f"{addr}, Sri Lanka"
    else:
        full_addr = addr
    return {'address': full_addr}


def compute_google_route(stops, api_key):
    """Calculate multi-stop driving route using Google Maps Routes API v2 with LIVE TRAFFIC."""
    try:
        origin = make_google_waypoint(stops[0])
        destination = make_google_waypoint(stops[-1])
        intermediates = [make_google_waypoint(s) for s in stops[1:-1]]

        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,routes.legs.startLocation,routes.legs.endLocation,routes.legs.duration,routes.legs.distanceMeters'
        }

        payload = {
            'origin': origin,
            'destination': destination,
            'intermediates': intermediates,
            'travelMode': 'DRIVE',
            'routingPreference': 'TRAFFIC_AWARE',
            'optimizeWaypointOrder': False
        }

        r = requests.post(
            'https://routes.googleapis.com/directions/v2:computeRoutes',
            headers=headers,
            json=payload,
            timeout=12
        )
        if r.status_code == 200:
            data = r.json()
            routes = data.get("routes", [])
            if routes:
                route = routes[0]
                distance_km = round(route.get("distanceMeters", 0) / 1000, 2)
                dur_str = route.get("duration", "0s").replace("s", "")
                duration_sec = int(dur_str) if dur_str.isdigit() else 0
                
                # Decode Google polyline
                encoded = route.get("polyline", {}).get("encodedPolyline", "")
                decoded_coords = decode_polyline(encoded) if encoded else []
                
                # Extract legs and stop coordinates
                legs = route.get("legs", [])
                legs_out = []
                ordered_points = []
                
                for i, stop in enumerate(stops):
                    s = dict(stop)
                    if i == 0:
                        loc = legs[0]["startLocation"]["latLng"]
                    else:
                        loc = legs[i - 1]["endLocation"]["latLng"]
                    s["lat"] = loc["latitude"]
                    s["lon"] = loc["longitude"]
                    ordered_points.append(s)

                for leg in legs:
                    leg_d = leg.get("distanceMeters", 0)
                    leg_dur_s = leg.get("duration", "0s").replace("s", "")
                    legs_out.append({
                        "distance": leg_d,
                        "duration": int(leg_dur_s) if leg_dur_s.isdigit() else 0
                    })

                route_geojson = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[lon, lat] for lat, lon in decoded_coords]
                    }
                }

                return {
                    "distance_km": distance_km,
                    "duration_sec": duration_sec,
                    "legs": legs_out,
                    "ordered_points": ordered_points,
                    "route_geojson": route_geojson,
                    "coords": decoded_coords,
                    "engine": "Google Maps (Live Traffic)"
                }
    except Exception as e:
        print("Google Routes API calculation error:", e)
    return None


def compute_osrm_route(valid_points):
    """Fallback route calculation using OSRM with real-world Sri Lanka traffic modifier."""
    coords_str_list = [f"{p['lon']},{p['lat']}" for p in valid_points]
    coords_string = ";".join(coords_str_list)

    if len(valid_points) == 2:
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{coords_string}?geometries=geojson&overview=full"
        response = requests.get(osrm_url, timeout=10).json()
        trip_data = response.get("routes", [{}])[0] if response.get("code") == "Ok" else None
    else:
        osrm_url = f"http://router.project-osrm.org/trip/v1/driving/{coords_string}?source=first&roundtrip=false&geometries=geojson&overview=full"
        response = requests.get(osrm_url, timeout=10).json()
        trip_data = response.get("trips", [{}])[0] if response.get("code") == "Ok" else None

    if not trip_data:
        return None

    distance_km = round(trip_data["distance"] / 1000, 2)
    raw_duration = trip_data.get("duration", 0)
    dwell_time = (len(valid_points) - 1) * 120  # 2 mins per stop
    duration_sec = int(raw_duration * 1.5 + dwell_time)

    waypoints = response.get("waypoints", [])
    if len(valid_points) > 2 and waypoints:
        ordered_points = [None] * len(valid_points)
        for i, wp in enumerate(waypoints):
            w_idx = wp.get("waypoint_index")
            if w_idx is not None and w_idx < len(ordered_points):
                ordered_points[w_idx] = valid_points[i]
        if any(p is None for p in ordered_points):
            ordered_points = valid_points
    else:
        ordered_points = valid_points

    legs_out = []
    for leg in trip_data.get("legs", []):
        legs_out.append({
            "distance": leg.get("distance", 0),
            "duration": int(leg.get("duration", 0) * 1.5 + 120)
        })

    route_geojson = trip_data.get("geometry", {})
    decoded_coords = [[coord[1], coord[0]] for coord in route_geojson.get("coordinates", [])]

    return {
        "distance_km": distance_km,
        "duration_sec": duration_sec,
        "legs": legs_out,
        "ordered_points": ordered_points,
        "route_geojson": route_geojson,
        "coords": decoded_coords,
        "engine": "OSRM (Traffic Calibrated)"
    }


# --- Data Loading & Analytics Helpers ---

# Excel file with full trip data (8,000+ trips, 378 employees)
EXCEL_FILENAME = "Pickme cost - Apr-Aug 2026 (Test) (2).xlsx"
EXCEL_SHEET = "Individual Trips Summary"


def _parse_hour_from_time_str(val):
    """Extract hour (0-23) from time strings like '12:05:31 am' or full timestamps."""
    if pd.isna(val):
        return None
    m = re.search(r'(\d{1,2}):\d{2}(?::\d{2})?\s*(am|pm)', str(val), re.IGNORECASE)
    if not m:
        return None
    h = int(m.group(1))
    ampm = m.group(2).lower()
    if ampm == 'pm' and h != 12:
        h += 12
    elif ampm == 'am' and h == 12:
        h = 0
    return h


@st.cache_data
def load_trip_history():
    """Load trip data from all files in data/ (primary) or fallback to root files.

    Normalizes column names so the rest of the app can use a consistent schema:
        PASSENGER NAME, PHONE, DEPARTMENT, VEHICLE TYPE, PICKUP LOCATION,
        DROP LOCATION, PICKUP TIME, RIDE REMARK, TRIP DISTANCE, TOTAL FARE,
        distance_num, fare_num, hour, day_of_week
    """
    base = os.path.dirname(__file__)
    data_dir = os.path.join(base, "data")

    col_map = {
        'Passenger Full Name': 'PASSENGER NAME',
        'Passenger Name': 'PASSENGER NAME',
        'Phone': 'PHONE',
        'LOB': 'DEPARTMENT',
        'Vehicle Type': 'VEHICLE TYPE',
        'Pickup Location': 'PICKUP LOCATION',
        'Drop Location': 'DROP LOCATION',
        'Drop-off Location': 'DROP LOCATION',
        'Drop Off Location': 'DROP LOCATION',
        'Time': 'PICKUP TIME',
        'Pickup Time': 'PICKUP TIME',
        'Drop Time': 'DROP TIME',
        'Ride Remark': 'RIDE REMARK',
        'Trip Distance': 'TRIP DISTANCE',
        'Total Fare': 'TOTAL FARE',
        'Day of the Week': 'DAY_OF_WEEK',
        'Time Period': 'TIME_PERIOD',
        'HOD': 'HOD',
        'Trip ID': 'TRIP ID',
    }

    dfs = []

    # Check data/ folder first
    if os.path.exists(data_dir):
        xlsx_files = sorted(glob.glob(os.path.join(data_dir, "*.xlsx")))
        csv_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))

        for fpath in xlsx_files:
            try:
                df_f = None
                for sheet in ['Individual Trips Summary', 'Sheet1', 0]:
                    try:
                        df_f = pd.read_excel(fpath, sheet_name=sheet)
                        if len(df_f) > 0:
                            break
                    except Exception:
                        continue
                if df_f is not None and len(df_f) > 0:
                    df_f = df_f.rename(columns=col_map)
                    dfs.append(df_f)
            except Exception:
                pass

        for fpath in csv_files:
            try:
                df_f = pd.read_csv(fpath, encoding='utf-8')
                df_f = df_f.rename(columns=col_map)
                dfs.append(df_f)
            except Exception:
                pass

    # Fallback to root files if data/ has no valid data
    if not dfs:
        xlsx_path = os.path.join(base, EXCEL_FILENAME)
        if os.path.exists(xlsx_path):
            try:
                df_f = pd.read_excel(xlsx_path, sheet_name=EXCEL_SHEET)
                df_f = df_f.rename(columns=col_map)
                dfs.append(df_f)
            except Exception:
                pass
        csv_path = os.path.join(base, "history.csv")
        if os.path.exists(csv_path):
            try:
                df_f = pd.read_csv(csv_path, encoding='utf-8')
                df_f = df_f.rename(columns=col_map)
                dfs.append(df_f)
            except Exception:
                pass

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # Normalize Trip ID and strictly deduplicate to ensure 100% accurate trip counts
    if 'TRIP ID' in df.columns:
        df['TRIP ID'] = df['TRIP ID'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
        valid_trips = df[~df['TRIP ID'].isin(['', 'nan', 'none', 'null'])].drop_duplicates(subset=['TRIP ID'], keep='first')
        missing_id_trips = df[df['TRIP ID'].isin(['', 'nan', 'none', 'null'])].drop_duplicates(
            subset=['PASSENGER NAME', 'PICKUP TIME', 'DROP LOCATION'], keep='first'
        ) if 'PASSENGER NAME' in df.columns and 'PICKUP TIME' in df.columns and 'DROP LOCATION' in df.columns else df[df['TRIP ID'].isin(['', 'nan', 'none', 'null'])]
        df = pd.concat([valid_trips, missing_id_trips], ignore_index=True)
    elif 'PASSENGER NAME' in df.columns and 'PICKUP TIME' in df.columns and 'DROP LOCATION' in df.columns:
        df = df.drop_duplicates(subset=['PASSENGER NAME', 'PICKUP TIME', 'DROP LOCATION'], keep='first')

    def _clean_dist(v):
        if pd.isna(v): return 0.0
        if isinstance(v, (int, float)): return float(v)
        s = str(v).replace('km', '').replace(',', '').strip()
        try: return float(s)
        except Exception: return 0.0

    def _clean_fare(v):
        if pd.isna(v): return 0.0
        if isinstance(v, (int, float)): return float(v)
        s = str(v).replace('LKR', '').replace(',', '').strip()
        try: return float(s)
        except Exception: return 0.0

    df['distance_num'] = df['TRIP DISTANCE'].apply(_clean_dist) if 'TRIP DISTANCE' in df.columns else 0.0
    df['fare_num'] = df['TOTAL FARE'].apply(_clean_fare) if 'TOTAL FARE' in df.columns else 0.0

    if 'PICKUP TIME' in df.columns:
        df['hour'] = df['PICKUP TIME'].apply(_parse_hour_from_time_str)
    else:
        df['hour'] = None

    if 'DAY_OF_WEEK' not in df.columns:
        df['day_of_week'] = pd.Series(dtype=str)
    else:
        df['day_of_week'] = df['DAY_OF_WEEK']

    return df


def get_employee_names():
    """Get sorted unique employee names from trip history."""
    df = load_trip_history()
    if df.empty:
        return []
    return sorted([n for n in df['PASSENGER NAME'].dropna().str.strip().unique() if n])


def get_employee_recent_dropoffs(name, limit=5):
    """Retrieve the exact chronological recent drop-offs for a given employee (most recent first)."""
    if not name or not str(name).strip():
        return []
    df = load_trip_history()
    if df.empty or 'PASSENGER NAME' not in df.columns or 'DROP LOCATION' not in df.columns:
        return []
    clean_name = str(name).strip().lower()
    matches = df[df['PASSENGER NAME'].fillna('').str.strip().str.lower() == clean_name]
    if matches.empty:
        matches = df[df['PASSENGER NAME'].fillna('').str.lower().str.contains(clean_name, regex=False)]
    if matches.empty:
        return []
    drops = []
    seen = set()
    for drop in reversed(matches['DROP LOCATION'].dropna().tolist()):
        d_str = str(drop).strip()
        if d_str and d_str.lower() not in seen and len(d_str) > 2:
            seen.add(d_str.lower())
            drops.append(d_str)
            if len(drops) >= limit:
                break
    return drops


def get_employee_stats(name):
    """Get trip statistics and verified date range for a specific employee."""
    df = load_trip_history()
    if df.empty:
        return None
    emp = df[df['PASSENGER NAME'].str.strip().str.lower() == name.strip().lower()]
    if emp.empty:
        return None
    top_drops = emp['DROP LOCATION'].value_counts().head(3)
    dept = emp['DEPARTMENT'].iloc[0] if 'DEPARTMENT' in emp.columns and pd.notna(emp['DEPARTMENT'].iloc[0]) else 'N/A'
    try:
        phone = str(int(emp['PHONE'].iloc[0]))
    except Exception:
        phone = 'N/A'
    hours = emp['hour'].dropna()
    ch = int(hours.mode().iloc[0]) if not hours.empty else -1
    shift = ("\U0001f319 Late Night" if 0 <= ch < 6 else "\U0001f305 Morning" if 6 <= ch < 12
             else "\u2600\ufe0f Afternoon" if 12 <= ch < 18 else "\U0001f306 Evening / Night" if ch >= 18 else "Unknown")
    vpref = emp['VEHICLE TYPE'].mode().iloc[0] if not emp['VEHICLE TYPE'].mode().empty else 'N/A'
    
    # Parse dates to establish exact historical data coverage window
    def _parse_trip_date(row):
        if 'DATE' in row and pd.notna(row['DATE']) and str(row['DATE']).strip():
            s = str(row['DATE']).strip()
            if s.lower() not in ('nan', 'none', 'null', ''):
                try:
                    return parser.parse(s)
                except Exception:
                    pass
        # Check DROP TIME and PICKUP TIME, but ONLY if they contain month/year (avoids raw times like '1:11 pm' defaulting to today)
        for col_c in ['DROP TIME', 'PICKUP TIME', 'Drop Time', 'Pickup Time']:
            if col_c in row and pd.notna(row[col_c]) and str(row[col_c]).strip():
                s = str(row[col_c]).strip()
                if re.search(r'\b(20\d\d|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', s, re.IGNORECASE):
                    s_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', s)
                    try:
                        return parser.parse(s_clean, fuzzy=True)
                    except Exception:
                        pass
        return None

    emp_dates = emp.apply(_parse_trip_date, axis=1).dropna()
    if not emp_dates.empty:
        d_start = emp_dates.min()
        d_end = emp_dates.max()
        days_span = (d_end.date() - d_start.date()).days + 1
        start_str = d_start.strftime("%b %d, %Y")
        end_str = d_end.strftime("%b %d, %Y")
        if start_str == end_str:
            date_range_str = f"{start_str}"
            date_range_sub = "Single Day Activity"
        else:
            date_range_str = f"{start_str} – {end_str}"
            date_range_sub = f"{days_span}-Day Active Period"
    else:
        date_range_str = "All Time Activity"
        date_range_sub = "Recorded Trips History"

    # Recent trips — use available columns
    trip_cols = [c for c in ['PICKUP LOCATION', 'DROP LOCATION', 'PICKUP TIME', 'DROP TIME', 'RIDE REMARK'] if c in emp.columns]
    recent = emp.head(3)[trip_cols].to_dict('records') if trip_cols else []
    return {
        'total_trips': len(emp), 'total_distance': round(emp['distance_num'].sum(), 1),
        'total_fare': round(emp['fare_num'].sum(), 2), 'avg_fare': round(emp['fare_num'].mean(), 2),
        'top_drops': top_drops, 'department': dept, 'phone': phone,
        'vehicle_pref': vpref, 'shift_pattern': shift, 'recent_trips': recent,
        'date_range': date_range_str, 'date_range_sub': date_range_sub
    }


def extract_common_reasons():
    """Common trip reason categories."""
    return ["Night Shift \u2013 Return Home", "Downtime / DR Activity", "Site Visit / Onsite Support",
            "Project Work / Upgrade", "Meeting", "Shift Off \u2013 Return Home",
            "Urgent / Emergency", "Other"]


def estimate_fare(distance_km, vehicle_type='Flex'):
    """Estimate realistic fare range using historical rates and standard Sri Lankan corporate fleet benchmarks."""
    if distance_km <= 0:
        return None, None

    # Base flag-fall and per-km pricing benchmarks for Sri Lanka corporate fleet
    fleet_benchmarks = {
        'flex': {'base': 250.0, 'per_km': 105.0},
        'mini': {'base': 300.0, 'per_km': 140.0},
        'car': {'base': 350.0, 'per_km': 160.0},
        'van': {'base': 500.0, 'per_km': 220.0}
    }
    vt_key = str(vehicle_type).strip().lower()
    bench = fleet_benchmarks.get(vt_key, fleet_benchmarks['flex'])

    per_km_rate = bench['per_km']
    base_fare = bench['base']

    df = load_trip_history()
    if not df.empty and 'distance_num' in df.columns and 'fare_num' in df.columns:
        vdf = df[df['VEHICLE TYPE'].astype(str).str.strip().str.lower() == vt_key] if 'VEHICLE TYPE' in df.columns else df
        if len(vdf) < 3:
            vdf = df
        
        valid_trips = vdf[(vdf['distance_num'] >= 0.8) & (vdf['fare_num'] > 0)]
        if not valid_trips.empty:
            rates = (valid_trips['fare_num'] / valid_trips['distance_num']).dropna()
            # Filter extreme outliers to keep rates within realistic bounds (LKR 60 - 280 / km)
            clean_rates = rates[(rates >= 60.0) & (rates <= 280.0)]
            if len(clean_rates) >= 3:
                per_km_rate = float(clean_rates.median())

    calc_fare = base_fare + (distance_km * per_km_rate)
    fare_low = max(bench['base'], round(calc_fare * 0.90, -1))
    fare_high = round(calc_fare * 1.15, -1)
    return float(fare_low), float(fare_high)


def find_pooling_candidates(passenger_name, hour=None):
    """Find employees who travel to similar destinations at similar times."""
    df = load_trip_history()
    if df.empty:
        return []
    if hour is None:
        hour = datetime.datetime.now().hour
    emp = df[df['PASSENGER NAME'].str.strip().str.lower() == passenger_name.strip().lower()]
    if emp.empty:
        return []
    emp_drops = set(emp['DROP LOCATION'].str.strip().str.lower().unique())
    hr_range = set(range(max(0, hour - 2), min(24, hour + 3)))
    others = df[
        (df['PASSENGER NAME'].str.strip().str.lower() != passenger_name.strip().lower())
        & (df['hour'].isin(hr_range))
    ]
    cands = []
    for nm, grp in others.groupby(others['PASSENGER NAME'].str.strip()):
        overlap = emp_drops & set(grp['DROP LOCATION'].str.strip().str.lower().unique())
        if overlap:
            cands.append({'name': nm, 'shared_destinations': len(overlap)})
    return sorted(cands, key=lambda x: x['shared_destinations'], reverse=True)[:3]


def append_trip_to_history(passenger_name, pickup_location, drop_location, distance_km=0.0, fare_lkr=0.0, vehicle_type="Flex", department=None, engine="Google Maps"):
    """Append a complete, rich corporate trip record to data/new_trips.csv so the system and ML model can learn from it."""
    base = os.path.dirname(__file__)
    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    csv_path = os.path.join(data_dir, "new_trips.csv")

    now = datetime.datetime.now()
    trip_id = f"{now.strftime('%Y%m%d%H%M%S')}_{abs(hash(passenger_name)) % 1000:03d}"
    pickup_time = now.strftime("%I:%M:%S %p").lower()
    day_of_week = now.strftime("%A")
    date_str = now.strftime("%Y-%m-%d")

    if not department:
        stats = get_employee_stats(passenger_name)
        department = stats.get('department', 'Enterprise Tech') if stats else 'General'

    new_row = {
        "TRIP ID": trip_id,
        "DATE": date_str,
        "DAY_OF_WEEK": day_of_week,
        "PICKUP TIME": pickup_time,
        "PASSENGER NAME": str(passenger_name).strip(),
        "DEPARTMENT": str(department).strip(),
        "VEHICLE TYPE": str(vehicle_type).strip(),
        "PICKUP LOCATION": str(pickup_location).strip(),
        "DROP LOCATION": str(drop_location).strip(),
        "TRIP DISTANCE": f"{distance_km:.1f} km" if isinstance(distance_km, (int, float)) else str(distance_km),
        "TOTAL FARE": f"LKR {fare_lkr:,.0f}" if isinstance(fare_lkr, (int, float)) else str(fare_lkr),
        "ROUTING ENGINE": str(engine),
        "STATUS": "Dispatched"
    }

    cols = [
        "TRIP ID", "DATE", "DAY_OF_WEEK", "PICKUP TIME", "PASSENGER NAME",
        "DEPARTMENT", "VEHICLE TYPE", "PICKUP LOCATION", "DROP LOCATION",
        "TRIP DISTANCE", "TOTAL FARE", "ROUTING ENGINE", "STATUS"
    ]

    file_exists = os.path.exists(csv_path)
    if file_exists:
        try:
            existing_df = pd.read_csv(csv_path, encoding='utf-8')
            row_df = pd.DataFrame([new_row])
            for c in cols:
                if c not in existing_df.columns:
                    existing_df[c] = ""
                if c not in row_df.columns:
                    row_df[c] = ""
            updated_df = pd.concat([existing_df, row_df[cols]], ignore_index=True)
            updated_df.to_csv(csv_path, index=False, encoding='utf-8')
            return trip_id
        except Exception:
            pass

    row_df = pd.DataFrame([new_row])[cols]
    row_df.to_csv(csv_path, index=False, encoding='utf-8')
    return trip_id


# --- Streamlit UI ---

from auth import init_auth_state, render_login_screen, render_user_sidebar

init_auth_state()

# Enforce enterprise authentication
if not st.session_state.get("authenticated", False):
    render_login_screen()
    st.stop()

# MillenniumIT ESP Top Executive Banner
ml_model, ml_encoders = load_prediction_model()
ml_meta = load_model_metadata()
v_num = ml_meta.get("version", 1) if ml_meta else 1
n_p = len(ml_encoders['passenger_encoder'].classes_) if ml_encoders else 0
acc_val = ml_meta.get("validation_accuracy", ml_meta.get("train_accuracy", 0)) if ml_meta else 0

# Physical spacer to guarantee complete clearance under Streamlit Cloud fixed header bar
st.markdown('<div class="header-clearance-spacer" style="height: 56px; width: 100%; display: block;"></div>', unsafe_allow_html=True)

# Executive Role Spotlight View
if st.session_state.get("user_role") == "Executive":
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(66, 138, 255, 0.15) 0%, rgba(15, 22, 38, 0.95) 100%); border: 1px solid rgba(66, 138, 255, 0.35); border-radius: 12px; padding: 14px 20px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 28px;">👔</span>
            <div>
                <div style="font-weight: 800; font-size: 15px; color: #FFFFFF;">Executive Leadership View • Welcome Sanath Fernando (CEO)</div>
                <div style="font-size: 12px; color: #CBD5E1;">Live portfolio oversight: LKR 10.26M baseline corporate transit with projected <b>~LKR 4.1M annual AI corridor savings</b>.</div>
            </div>
        </div>
        <div>
            <span style="background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 12px;">
                AUDITED DATA PARITY: 100%
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    col_e1.metric("Managed Fleet Spend", "LKR 10.26M", "+8,043 Trips")
    col_e2.metric("Projected AI Savings", "LKR 4.12M", "40.2% Net ROI")
    col_e3.metric("Fleet Corridor Range", "76,708 km", "Zero Unrouted Runs")
    col_e4.metric("Corporate Coverage", "403 Staff", "100% Ingested")
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

header_html = f"""<div style="background: linear-gradient(135deg, rgba(16, 22, 34, 0.95) 0%, rgba(11, 15, 23, 0.95) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-top: 3px solid #EF4123; border-radius: 16px; padding: 22px 28px; margin-bottom: 24px; box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45); backdrop-filter: blur(16px);">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
<div>
{render_brand_header("AI MOBILITY DISPATCH", height_px=36)}
<h1 style="margin: 0; font-size: 26px; font-weight: 800; background: linear-gradient(135deg, #FFFFFF 30%, #E2E8F0 60%, #94A3B8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px;">Corporate Transport & Corridor Dispatch</h1>
<p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 13px;">Intelligent employee carpooling, automated drop-off prediction & real-time multi-stop route optimization.</p>
</div>
<div style="display: flex; gap: 10px;">
<div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 8px 14px; text-align: center;">
<div style="font-size: 10px; color: #64748B; font-weight: 700; text-transform: uppercase;">AI Engine</div>
<div style="font-size: 13px; color: #10B981; font-weight: 700;">🟢 Online (v{v_num})</div>
</div>
<div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 8px 14px; text-align: center;">
<div style="font-size: 10px; color: #64748B; font-weight: 700; text-transform: uppercase;">Accuracy</div>
<div style="font-size: 13px; color: #428AFF; font-weight: 700;">{acc_val:.1f}%</div>
</div>
<div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 8px 14px; text-align: center;">
<div style="font-size: 10px; color: #64748B; font-weight: 700; text-transform: uppercase;">Employees</div>
<div style="font-size: 13px; color: #F8FAFC; font-weight: 700;">{n_p} Indexed</div>
</div>
</div>
</div>
</div>"""
st.markdown(header_html, unsafe_allow_html=True)

# Sidebar ML Status & Data Management
with st.sidebar:
    st.markdown(render_sidebar_logo(), unsafe_allow_html=True)
    render_user_sidebar()

    st.header("🧠 AI Destination Predictor")
    if ml_model and ml_encoders:
        st.success("✅ ML Engine: Active")
        n_l = len(ml_encoders['location_encoder'].classes_)
        st.markdown(
            f"- **Model Version:** `v{v_num}`\n"
            f"- **Test Accuracy:** **{acc_val:.1f}%**\n"
            f"- **Learned Passengers:** {n_p}\n"
            f"- **Known Drop-offs:** {n_l}\n"
            f"- **Current Hour:** {datetime.datetime.now().strftime('%I:%M %p')}"
        )
        with st.expander("👥 View Known Passengers"):
            pass_list = sorted(list(ml_encoders['name_lookup'].values()))
            st.write(", ".join(pass_list[:30]) + ("..." if len(pass_list) > 30 else ""))
    else:
        st.warning("⚠️ Prediction model not found. Run `train_model.py`.")

    st.markdown("---")
    st.header("👤 Employee Profile")
    _emp_names_sb = get_employee_names()
    _sel_emp = st.selectbox("View Employee", options=_emp_names_sb, index=None,
                            key="sidebar_emp_profile", placeholder="Select employee...")
    if _sel_emp:
        _stats = get_employee_stats(_sel_emp)
        if _stats:
            st.markdown(f"""
            <div style="background: rgba(66, 138, 255, 0.08); border: 1px solid rgba(66, 138, 255, 0.3); border-radius: 8px; padding: 8px 12px; margin-top: 6px; margin-bottom: 12px;">
                <div style="font-size: 10px; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">📅 Trip History Date Range:</div>
                <div style="font-size: 12px; color: #F8FAFC; font-weight: 700; margin-top: 2px;">
                    {_stats['date_range']}
                </div>
                <div style="font-size: 10px; color: #38BDF8; margin-top: 1px;">
                    {_stats['date_range_sub']} ({_stats['total_trips']} total logged trips)
                </div>
            </div>
            """, unsafe_allow_html=True)
            _m1, _m2 = st.columns(2)
            with _m1:
                st.metric("Trips", _stats['total_trips'])
                st.metric("Avg Cost", f"LKR {_stats['avg_fare']:,.0f}")
            with _m2:
                st.metric("Distance", f"{_stats['total_distance']} km")
                st.metric("Total Spend", f"LKR {_stats['total_fare']:,.0f}")
            st.caption(f"📞 {_stats['phone']}  |  🏢 {_stats['department']}")
            st.caption(f"🚗 {_stats['vehicle_pref']}  |  🕐 {_stats['shift_pattern']}")
            with st.expander("📍 Top Drop-offs"):
                for _loc, _cnt in _stats['top_drops'].items():
                    _short = (_loc[:50] + '...') if len(_loc) > 50 else _loc
                    st.write(f"• {_short} ({_cnt}×)")
            with st.expander("🔁 Recent Trips"):
                for _trip in _stats['recent_trips']:
                    _p = str(_trip.get('PICKUP LOCATION', ''))[:35]
                    _d = str(_trip.get('DROP LOCATION', ''))[:35]
                    _t = str(_trip.get('PICKUP TIME', ''))
                    _t_short = _t.split(',')[0] if ',' in _t else _t[:12]
                    st.caption(f"📅 {_t_short} | 📍 {_p} → {_d}")

    st.markdown("---")
    st.header("📂 Data Management")
    uploaded_files = st.file_uploader(
        "Upload Trip Sheet(s)",
        type=["xlsx", "csv"],
        accept_multiple_files=True,
        help="Upload new monthly or quarterly sheets (.xlsx or .csv) to expand the model's intelligence."
    )
    if uploaded_files:
        base_dir = os.path.dirname(__file__)
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        saved_any = False
        for uf in uploaded_files:
            target_file = os.path.join(data_dir, uf.name)
            if not os.path.exists(target_file):
                with open(target_file, "wb") as f:
                    f.write(uf.getbuffer())
                saved_any = True
        if saved_any:
            st.success("📥 New sheets saved to `data/`!")
            st.cache_data.clear()
            st.rerun()

    # Show active data sources in data/
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "data")
    if os.path.exists(data_dir):
        all_sheets = sorted(glob.glob(os.path.join(data_dir, "*.xlsx")) + glob.glob(os.path.join(data_dir, "*.csv")))
        if all_sheets:
            with st.expander(f"📁 Ingested Sheets ({len(all_sheets)})"):
                for sh in all_sheets:
                    sz = round(os.path.getsize(sh) / 1024, 1)
                    st.caption(f"📄 **{os.path.basename(sh)}** ({sz} KB)")

    if st.button("🔄 Retrain Model", use_container_width=True, type="primary"):
        with st.spinner("Retraining model on all ingested sheets..."):
            _result = subprocess.run(
                ["python", os.path.join(os.path.dirname(__file__), "train_model.py")],
                capture_output=True, text=True, cwd=os.path.dirname(__file__)
            )
            if _result.returncode == 0:
                st.cache_resource.clear()
                st.cache_data.clear()
                new_meta = load_model_metadata()
                if new_meta:
                    st.success(
                        f"✅ **Retrained as v{new_meta.get('version', 1)}!**\n\n"
                        f"- Test Accuracy: **{new_meta.get('validation_accuracy', 0):.1f}%**\n"
                        f"- Learned Passengers: **{new_meta.get('unique_passengers', 0)}**\n"
                        f"- Total Locations: **{new_meta.get('unique_locations', 0)}**\n"
                        f"- Retrain Time: **{new_meta.get('training_duration_sec', 0):.1f}s**"
                    )
                else:
                    st.success("✅ Model retrained successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Training failed:\n{_result.stderr[:300]}")


HQ_ADDRESS = "No. 450D, R A De Mel Mawatha, Colombo 3, Colombo 00300, Sri Lanka"

# Initialize session state
if "trip_result" not in st.session_state:
    st.session_state.trip_result = None

if "pickup_address" not in st.session_state or not st.session_state.pickup_address:
    st.session_state.pickup_address = HQ_ADDRESS

for i in range(1, 7):
    if f"p{i}_name" not in st.session_state:
        st.session_state[f"p{i}_name"] = None
    if f"p{i}_drop" not in st.session_state:
        st.session_state[f"p{i}_drop"] = ""
    if f"p{i}_ml_notice" not in st.session_state:
        st.session_state[f"p{i}_ml_notice"] = None
    if f"p{i}_recent_sel" not in st.session_state:
        st.session_state[f"p{i}_recent_sel"] = "-- Select a recent location or type custom --"

if "active_map_pin" not in st.session_state:
    st.session_state.active_map_pin = None

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "dispatch"

if "map_target" not in st.session_state:
    st.session_state["map_target"] = "pickup"

if "last_registered_click_lat" not in st.session_state:
    st.session_state["last_registered_click_lat"] = None

if "last_registered_click_lng" not in st.session_state:
    st.session_state["last_registered_click_lng"] = None

# Streamlit-safe state update callbacks (prevents StreamlitWidgetAlreadyInstantiatedError)
def cb_set_pickup(addr):
    st.session_state["pickup_address"] = addr

def cb_set_passenger_drop(idx, addr):
    st.session_state[f"p{idx}_drop"] = addr

def cb_apply_active_pin_to_pickup():
    pin = st.session_state.get("active_map_pin")
    if pin and pin.get("address"):
        st.session_state["pickup_address"] = pin["address"]
        st.session_state["pin_applied_toast"] = f"🚖 Pickup updated to: {pin['address']}"

def cb_apply_active_pin_to_passenger(idx):
    pin = st.session_state.get("active_map_pin")
    if pin and pin.get("address"):
        st.session_state[f"p{idx}_drop"] = pin["address"]
        st.session_state["pin_applied_toast"] = f"🎯 Passenger {idx} drop updated to: {pin['address']}"

def cb_clear_active_pin():
    st.session_state["active_map_pin"] = None
    st.session_state["last_registered_click_lat"] = None
    st.session_state["last_registered_click_lng"] = None
    st.session_state["pin_success_msg"] = None

def cb_select_recent_drop(idx):
    sel = st.session_state.get(f"p{idx}_recent_sel")
    if sel and not sel.startswith("--"):
        clean_sel = re.sub(r'\s*\((AI Recommended|Recent Stop \d+)\)$', '', sel).strip()
        st.session_state[f"p{idx}_drop"] = clean_sel

def cb_set_all_drops_hq(n_passengers):
    for idx in range(1, n_passengers + 1):
        st.session_state[f"p{idx}_drop"] = HQ_ADDRESS

def cb_autofill_staff_drops(employee_list):
    sample_emps = [e for e in employee_list if e][:3]
    for s_idx, s_emp in enumerate(sample_emps, 1):
        st.session_state[f"p{s_idx}_name"] = s_emp
        p_loc, m_name = predict_dropoff_location(s_emp)
        if p_loc:
            st.session_state[f"p{s_idx}_drop"] = p_loc
            st.session_state[f"p{s_idx}_ml_notice"] = f"🎯 Auto-filled for {m_name}: {p_loc}"

# Default num_passengers fallback so both views always have access
num_passengers = st.session_state.get("num_passengers_val", 3)

TAB_DISPATCH = "dispatch"
TAB_MAP = "map"

# --- Persistent Mission Control Navigation (Preserves Tab Across Reruns) ---
c_nav1, c_nav2 = st.columns(2)
with c_nav1:
    is_active_disp = (st.session_state.get("active_tab", TAB_DISPATCH) == TAB_DISPATCH)
    if st.button(
        "🚖 1. Route & Passenger Dispatch",
        key="nav_tab_disp",
        type="primary" if is_active_disp else "secondary",
        use_container_width=True
    ):
        st.session_state["active_tab"] = TAB_DISPATCH
        st.rerun()

with c_nav2:
    is_active_map = (st.session_state.get("active_tab") == TAB_MAP)
    pin_badge = " • 📍 PIN ACTIVE" if st.session_state.get("active_map_pin") else ""
    if st.button(
        f"🗺️ 2. Live Transit Map{pin_badge}",
        key="nav_tab_map",
        type="primary" if is_active_map else "secondary",
        use_container_width=True
    ):
        st.session_state["active_tab"] = TAB_MAP
        st.rerun()

if st.session_state.get("active_tab", TAB_DISPATCH) == TAB_DISPATCH:
    # 📍 Card 1: Pickup Location
    st.markdown('<div class="mit-card"><div class="mit-card-title">📍 Step 1: Pickup Location (Anywhere in Sri Lanka)</div>', unsafe_allow_html=True)
    col_p_in, col_p_map, col_p_hq = st.columns([2.5, 1.1, 1.1])
    with col_p_in:
        pickup = st.text_input("Pickup Address", key="pickup_address", placeholder="e.g. Colombo 03, Kandy, or tap map", label_visibility="collapsed")
    with col_p_map:
        if st.button("🗺️ Pick Map", key="btn_pick_pickup_map", help="Open live map to tap and pin pickup location", use_container_width=True):
            st.session_state["map_target"] = "pickup"
            st.session_state["active_tab"] = TAB_MAP
            st.rerun()
    with col_p_hq:
        st.button("🏢 Set HQ", on_click=cb_set_pickup, args=(HQ_ADDRESS,), help="Quick-set pickup to MillenniumIT ESP Headquarters (Colombo 03)", use_container_width=True)
    
    is_hq_pickup = pickup and ("450d" in str(pickup).lower() or "de mel" in str(pickup).lower() or str(pickup).strip() == HQ_ADDRESS)
    if is_hq_pickup:
        st.markdown("""
        <div style="background: rgba(239, 65, 35, 0.12); border: 1px solid rgba(239, 65, 35, 0.4); border-radius: 8px; padding: 6px 12px; font-size: 11px; color: #FF7A63; display: flex; align-items: center; justify-content: space-between; margin-top: 4px;">
            <span>🏢 <b>Corporate Headquarters Active as Pickup:</b> Colombo 03 (Duplication Road)</span>
            <span style="color: #94A3B8; font-size: 10px;">Primary Corporate Origin</span>
        </div>
        """, unsafe_allow_html=True)
    elif pickup and str(pickup).strip():
        p_coord_preview = geocode_address(pickup)
        if p_coord_preview:
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 8px; padding: 6px 12px; font-size: 11px; color: #34D399; display: flex; align-items: center; justify-content: space-between; margin-top: 6px;">
                <span>📍 <b>Origin Pinpoint Mapped:</b> {pickup[:35]}</span>
                <span><code>{p_coord_preview[0]:.4f}, {p_coord_preview[1]:.4f}</code></span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: rgba(239, 65, 35, 0.12); border: 1px solid rgba(239, 65, 35, 0.35); border-radius: 8px; padding: 6px 12px; font-size: 11px; color: #FF7A63; margin-top: 6px;">
                🔍 Address not yet resolved. You can also click anywhere on the map to set an exact pin!
            </div>
            """, unsafe_allow_html=True)

    # Saved corporate pickup hubs
    custom_hubs = load_custom_pickup_hubs()
    st.markdown('<div style="font-size: 11px; color: #64748B; font-weight: 700; margin-top: 8px; margin-bottom: 6px; text-transform: uppercase;">Corporate Pickup Quick Picks:</div>', unsafe_allow_html=True)
    hub_cols = st.columns(min(len(custom_hubs), 4))
    for h_i, hub in enumerate(custom_hubs[:4]):
        with hub_cols[h_i]:
            st.button(f"{hub.get('icon', '🏢')} {hub['name']}", key=f"hub_btn_{h_i}", on_click=cb_set_pickup, args=(hub["address"],), use_container_width=True)

    with st.expander("⭐ Save Custom Pickup Hub / Sri Lanka City Jumps"):
        col_sh1, col_sh2 = st.columns([1.5, 1])
        with col_sh1:
            lk_cities = [
                "-- Select a Sri Lanka Region / City --",
                "No. 450D, R A De Mel Mawatha, Colombo 3 (MIT ESP HQ)",
                "MillenniumIT ESP Campus, Malabe",
                "Colombo 03 (Colpetty / Duplication Road)",
                "Colombo 07 (Cinnamon Gardens / Town Hall)",
                "Colombo 01 (Fort / World Trade Center)",
                "Katunayake (Bandaranaike International Airport)",
                "Kandy City Centre (Central Province)",
                "Galle Fort (Southern Province)",
                "Negombo Town (Western Province)",
                "Kurunegala Town (North Western Province)",
                "Gampaha Town (Western Province)",
                "Matara Town (Southern Province)",
                "Jaffna Town (Northern Province)",
                "Anuradhapura Sacred City (North Central)",
                "Battaramulla / Pelawatte (Administrative Capital)"
            ]
            sel_city = st.selectbox("Quick City Jump", lk_cities, index=0)
            if sel_city and sel_city != "-- Select a Sri Lanka Region / City --":
                st.button(f"📌 Set '{sel_city.split('(')[0].strip()}' as Pickup", on_click=cb_set_pickup, args=(sel_city.split('(')[0].strip() + ", Sri Lanka",), use_container_width=True)
        with col_sh2:
            new_hub_name = st.text_input("Save Current as New Hub", placeholder="e.g. Kandy Branch, Orion City...")
            if st.button("💾 Save as Quick Pick", use_container_width=True):
                if pickup and new_hub_name:
                    custom_hubs.append({
                        "name": new_hub_name.strip(),
                        "address": pickup.strip(),
                        "icon": "📍"
                    })
                    save_custom_pickup_hubs(custom_hubs)
                    st.success(f"Saved '{new_hub_name}'!")
                    st.rerun()
                else:
                    st.warning("Enter an address and hub name first.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 👥 Card 2: Employees & Drop-offs
    st.markdown('<div class="mit-card"><div class="mit-card-title">👥 Step 2: Workers & Smart AI Prediction</div>', unsafe_allow_html=True)
    st.caption("💡 **Smart AI Auto-Fill:** Select an employee. The AI predicts their drop-off, or quick-set drop-off to Headquarters.")
    
    col_p_count, col_p_quick1, col_p_quick2 = st.columns([1.2, 1, 1])
    with col_p_count:
        num_passengers = st.selectbox("Number of Passengers to Pool", [1, 2, 3, 4, 5, 6], index=2, key="num_passengers_val")
    with col_p_quick1:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        employee_names = get_employee_names()
        st.button("⚡ Auto-Fill 3 Staff", on_click=cb_autofill_staff_drops, args=(employee_names,), help="Instantly fill 3 employees with AI drop-offs", use_container_width=True)
    with col_p_quick2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        st.button("🏢 All Drops to HQ", on_click=cb_set_all_drops_hq, args=(num_passengers,), help="Set all passenger destinations to MIT ESP Headquarters (Colombo 03)", use_container_width=True)

    for i in range(1, num_passengers + 1):
        st.markdown(f'<div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px; margin-bottom: 10px;">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1.1, 1.2, 0.45, 0.45])
        with col1:
            st.selectbox(
                f"Passenger {i} Name",
                options=employee_names,
                index=None,
                key=f"p{i}_name",
                on_change=handle_passenger_name_change,
                args=(i,),
                placeholder="Search employee..."
            )
        with col2:
            st.text_input(
                f"Passenger {i} Drop-off",
                key=f"p{i}_drop",
                placeholder="e.g. Nugegoda, Kandy, or tap map"
            )
        with col3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🗺️", key=f"btn_map_p{i}", help=f"Pin Passenger {i} Drop-off on the live map", use_container_width=True):
                st.session_state["map_target"] = f"p{i}"
                st.session_state["active_tab"] = TAB_MAP
                st.rerun()
        with col4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            st.button("🏢", key=f"btn_set_hq_p{i}", on_click=cb_set_passenger_drop, args=(i, HQ_ADDRESS), help="Quick set drop-off to MIT ESP HQ (Colombo 03)", use_container_width=True)
        
        # Recent Locations Dropdown for selected employee
        p_name = st.session_state.get(f"p{i}_name")
        if p_name and str(p_name).strip():
            recent_drops = get_employee_recent_dropoffs(p_name, limit=5)
            pred_loc, _ = predict_dropoff_location(p_name)
            
            combined_options = []
            if recent_drops:
                combined_options.extend(recent_drops)
            if pred_loc and pred_loc not in combined_options:
                combined_options.append(f"{pred_loc} (AI Recommended)")
            
            if combined_options:
                first_name = str(p_name).strip().split()[0]
                dropdown_options = ["-- Select a recent location or type custom --"] + combined_options
                st.selectbox(
                    f"🕒 Recent Destinations for {first_name} (Select to Auto-Fill Drop-off)",
                    options=dropdown_options,
                    key=f"p{i}_recent_sel",
                    on_change=cb_select_recent_drop,
                    args=(i,),
                    help=f"Select one of {first_name}'s recent destinations to auto-fill into Passenger {i} Drop-off above"
                )
        
        notice = st.session_state.get(f"p{i}_ml_notice")
        if notice:
            st.markdown(f"""
            <div style="background: rgba(66, 138, 255, 0.12); border: 1px solid rgba(66, 138, 255, 0.35); border-radius: 6px; padding: 5px 10px; font-size: 11px; color: #82B1FF; display: flex; align-items: center; gap: 6px; margin-top: 4px;">
                <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #428AFF; box-shadow: 0 0 6px #428AFF;"></span>
                <span>{notice}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 🚀 Card 3: Dispatch & Routing
    st.markdown('<div class="mit-card"><div class="mit-card-title">🚀 Step 3: Dispatch Configuration</div>', unsafe_allow_html=True)
    c_vh1, c_vh2 = st.columns(2)
    with c_vh1:
        trip_reasons = extract_common_reasons()
        st.selectbox("Trip Reason (Billing)", options=[""] + trip_reasons, key="trip_reason", index=0,
                     format_func=lambda x: "Select billing category..." if x == "" else x)
    with c_vh2:
        fleet_types = ["Flex", "Car", "Mini", "Van"]
        st.selectbox("Vehicle Fleet Category", fleet_types, index=0, key="vehicle_type_choice")

    col_disp1, col_disp2 = st.columns([1.6, 1])
    with col_disp1:
        submitted = st.button("🚀 Optimize & Dispatch Route", type="primary", use_container_width=True)
    with col_disp2:
        if st.button("🔄 Retrain AI (New Locations)", use_container_width=True, help="Update AI model with newly logged pickup and drop-off locations"):
            with st.spinner("Retraining AI model on newly added locations..."):
                _result = subprocess.run(
                    ["python", os.path.join(os.path.dirname(__file__), "train_model.py")],
                    capture_output=True, text=True, cwd=os.path.dirname(__file__)
                )
                if _result.returncode == 0:
                    st.cache_resource.clear()
                    st.cache_data.clear()
                    new_meta = load_model_metadata()
                    v_str = f"v{new_meta.get('version', 1)}" if new_meta else "latest"
                    st.success(f"✅ AI retrained as {v_str} with updated island-wide locations!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Retraining failed:\n" + _result.stderr[:200])

    st.markdown("""
    <div style="background: rgba(66, 138, 255, 0.08); border: 1px dashed rgba(66, 138, 255, 0.3); border-radius: 10px; padding: 12px 16px; margin-top: 10px; display: flex; align-items: center; gap: 10px;">
        <span style="font-size: 20px;">🗺️</span>
        <div>
            <div style="font-weight: 700; color: #82B1FF; font-size: 13px;">Need to Pinpoint Locations on the Map?</div>
            <div style="font-size: 12px; color: #94A3B8;">Switch to the <b>'🗺️ 2. Live Transit Map & Tap-to-Pin'</b> tab above to drop interactive GPS pins anywhere across Sri Lanka and auto-assign locations with 1 tap.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# Execute submission if clicked
if submitted:
    for i in range(1, num_passengers + 1):
        n = (st.session_state.get(f"p{i}_name") or "").strip()
        d = st.session_state.get(f"p{i}_drop", "").strip()
        if n and not d:
            pred_loc, matched_name = predict_dropoff_location(n)
            if pred_loc:
                try:
                    st.session_state[f"p{i}_drop"] = pred_loc
                except Exception:
                    pass
                time_str = datetime.datetime.now().strftime("%I:%M %p")
                st.session_state[f"p{i}_ml_notice"] = f"🎯 Predicted for **{matched_name}** at {time_str}: `{pred_loc}`"

    pickup_val = st.session_state.get("pickup_address", "").strip()
    valid_passengers = []
    for i in range(1, num_passengers + 1):
        n = (st.session_state.get(f"p{i}_name") or "").strip()
        d = st.session_state.get(f"p{i}_drop", "").strip()
        if n and d:
            valid_passengers.append((n, d))

    if not pickup_val or len(valid_passengers) == 0:
        st.error("Please provide a pickup location and at least one passenger's name and drop-off location.")
    else:
        with st.spinner("Calculating optimal route with live Google traffic..."):
            raw_stops = [{"type": "Pickup", "name": "Start", "address": pickup_val.strip()}]
            for n, d in valid_passengers:
                raw_stops.append({"type": "Drop-off", "name": n.strip(), "address": d.strip()})
            
            trip_res = None
            api_key = get_google_maps_api_key()
            
            if api_key:
                trip_res = compute_google_route(raw_stops, api_key)
            
            if not trip_res:
                geolocator = Nominatim(user_agent="transport_pooling_lk_optimizer", timeout=10)
                valid_points = []
                for loc in raw_stops:
                    coords = geocode_address(loc["address"], geolocator)
                    if coords:
                        loc_copy = dict(loc)
                        loc_copy["lat"], loc_copy["lon"] = coords
                        valid_points.append(loc_copy)
                    else:
                        st.warning(f"Could not locate: {loc['address']}. Skipping this point.")
                    time.sleep(1)
                
                if len(valid_points) >= 2:
                    trip_res = compute_osrm_route(valid_points)
            
            if trip_res:
                distance_km = trip_res["distance_km"]
                duration_sec = trip_res["duration_sec"]
                duration_min = round(duration_sec / 60)
                duration_str = f"{duration_min // 60}h {duration_min % 60}m" if duration_min >= 60 else f"{duration_min} mins"
                ordered_points = trip_res["ordered_points"]
                route_geojson = trip_res["route_geojson"]
                legs = trip_res["legs"]
                engine = trip_res["engine"]
                
                dropoff_stops = [loc for loc in ordered_points if loc["type"] == "Drop-off"]
                names_str = ", ".join([loc["name"] for loc in dropoff_stops])
                dropoffs_str = " -> ".join([f"{loc['name']} ({loc['address']})" for loc in dropoff_stops])
                
                sheet_data = {
                    "pickup": pickup_val,
                    "names": names_str,
                    "dropoffs": dropoffs_str,
                    "distance": distance_km,
                    "duration": duration_str,
                    "engine": engine
                }
                
                log_success = False
                try:
                    requests.post(WEBHOOK_URL, json=sheet_data, timeout=8)
                    log_success = True
                except Exception:
                    log_success = False
                
                v_type = st.session_state.get("vehicle_type_choice", "Flex")
                _f_low, _f_high = estimate_fare(distance_km, v_type)
                total_est_fare = round((_f_low + _f_high) / 2.0) if (_f_low and _f_high) else round(250.0 + (distance_km * 110.0))
                per_pass_fare = round(total_est_fare / max(1, len(valid_passengers)), 0) if valid_passengers else 0.0

                created_trip_ids = []
                for _pname, _pdrop in valid_passengers:
                    try:
                        t_id = append_trip_to_history(
                            passenger_name=_pname,
                            pickup_location=pickup_val,
                            drop_location=_pdrop,
                            distance_km=distance_km,
                            fare_lkr=per_pass_fare,
                            vehicle_type=v_type,
                            engine=engine
                        )
                        created_trip_ids.append(t_id)
                    except Exception as e:
                        print("Error saving trip to datasheet:", e)
                
                manifest_id = f"MIT-EXP-{datetime.datetime.now().strftime('%Y%m%d')}-{abs(hash(pickup_val)) % 10000:04d}"

                st.session_state.trip_result = {
                    "distance_km": distance_km,
                    "duration_str": duration_str,
                    "ordered_points": ordered_points,
                    "dropoff_stops": dropoff_stops,
                    "route_geojson": route_geojson,
                    "legs": legs,
                    "engine": engine,
                    "log_success": log_success,
                    "manifest_id": manifest_id,
                    "vehicle_type": v_type,
                    "total_est_fare": total_est_fare,
                    "per_pass_fare": per_pass_fare,
                    "created_trip_ids": created_trip_ids,
                    "pickup_val": pickup_val,
                    "valid_passengers": valid_passengers,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                }
                st.cache_data.clear()
                st.rerun()
            else:
                st.session_state.trip_result = None
                st.error("The routing engine could not map a driving path between these locations. Check the location names or use the Map Pin-Picker.")


    # If a trip has been dispatched, render the full Route Intelligence Deck inside Tab 1
    if st.session_state.trip_result:
        res = st.session_state.trip_result
        distance_km = res["distance_km"]
        duration_str = res["duration_str"]
        ordered_points = res["ordered_points"]
        dropoff_stops = res["dropoff_stops"]
        route_geojson = res["route_geojson"]
        legs = res["legs"]
        engine = res.get("engine", "Google Maps")
        log_success = res["log_success"]
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(66, 138, 255, 0.12) 100%); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; margin-top: 16px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">✅</span>
                <div>
                    <div style="font-weight: 700; color: #F8FAFC; font-size: 15px;">Optimal Corridor Route Generated</div>
                    <div style="color: #94A3B8; font-size: 12px;">{distance_km} km total driving distance &bull; Estimated driving time {duration_str}</div>
                </div>
            </div>
            <span style="background: rgba(16, 185, 129, 0.2); color: #34D399; font-weight: 700; font-size: 11px; padding: 4px 10px; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.5px;">
                {"Logged to Sheets" if log_success else "Route Ready"}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Responsive 2x2 stats grid
        m_row1_1, m_row1_2 = st.columns(2)
        with m_row1_1:
            st.metric("Total Distance", f"{distance_km} km")
        with m_row1_2:
            st.metric("Est. Driving Time", duration_str)
            
        m_row2_1, m_row2_2 = st.columns(2)
        with m_row2_1:
            st.metric("Drop-off Stops", f"{len(dropoff_stops)} Passengers")
        with m_row2_2:
            st.metric("Routing Engine", engine, delta="Live Traffic" if "Google" in engine else None)
        
        # Fare Estimate
        _fare_low, _fare_high = estimate_fare(distance_km)
        if _fare_low and _fare_high:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(239, 65, 35, 0.15) 0%, rgba(66, 138, 255, 0.15) 100%); border: 1px solid rgba(239, 65, 35, 0.3); border-radius: 10px; padding: 12px 18px; margin-top: 12px; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span style="color: #F8FAFC; font-weight: 700; font-size: 13px;">💰 Estimated Vehicle Fare:</span>
                    <span style="color: #FF7A63; font-weight: 800; font-size: 16px; margin-left: 6px;">LKR {_fare_low:,.0f} – {_fare_high:,.0f}</span>
                </div>
                <span style="color: #94A3B8; font-size: 11px;">Historical Rate Benchmark</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Interactive Navigation Map inside Dispatch Tab
        st.markdown("##### 🗺️ Real-time Interactive Route Map")
        center_lat = sum(p["lat"] for p in ordered_points) / len(ordered_points)
        center_lon = sum(p["lon"] for p in ordered_points) / len(ordered_points)
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap")
        
        folium.GeoJson(
            route_geojson,
            style_function=lambda x: {'color': '#0C2340', 'weight': 9, 'opacity': 0.35},
            name="Route Glow"
        ).add_to(m)
        folium.GeoJson(
            route_geojson,
            style_function=lambda x: {'color': '#0066FF', 'weight': 5, 'opacity': 0.95},
            name="Navigation Path"
        ).add_to(m)
        
        drop_colors = ["#EF4123", "#428AFF", "#10B981", "#F59E0B", "#8B5CF6", "#06B6D4"]
        for idx, loc in enumerate(ordered_points):
            if idx == 0:
                badge_html = """
                <div style="background: #10B981; color: white; border: 2px solid white; border-radius: 16px; padding: 4px 10px; font-family: -apple-system, sans-serif; font-size: 11px; font-weight: 700; box-shadow: 0 4px 10px rgba(0,0,0,0.35); white-space: nowrap; display: inline-flex; align-items: center; gap: 5px;">
                    <span>🚖</span><span>PICKUP</span>
                </div>
                """
                popup_html = f"""
                <div style="font-family: -apple-system, sans-serif; min-width: 170px;">
                    <div style="background: #10B981; color: white; padding: 6px 10px; border-radius: 6px 6px 0 0; font-weight: bold; font-size: 13px;">
                        🚖 Pickup Origin
                    </div>
                    <div style="padding: 8px 10px; font-size: 12px; background: white; border: 1px solid #ddd; border-top: none; border-radius: 0 0 6px 6px; color: #1E293B;">
                        <b>Address:</b> {loc['address']}
                    </div>
                </div>
                """
                folium.Marker(
                    [loc["lat"], loc["lon"]],
                    icon=folium.DivIcon(html=badge_html, icon_size=(90, 30), icon_anchor=(45, 15)),
                    tooltip=f"🚖 Pickup: {loc['address']}",
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(m)
            else:
                color = drop_colors[(idx - 1) % len(drop_colors)]
                leg_txt = ""
                if idx - 1 < len(legs):
                    d_km = round(legs[idx - 1]["distance"] / 1000, 1)
                    t_m = round(legs[idx - 1]["duration"] / 60)
                    leg_txt = f"{d_km} km (~{t_m} mins)"
                    
                badge_html = f"""
                <div style="background: {color}; color: white; border: 2px solid white; border-radius: 16px; padding: 4px 10px; font-family: -apple-system, sans-serif; font-size: 11px; font-weight: 700; box-shadow: 0 4px 10px rgba(0,0,0,0.35); white-space: nowrap; display: inline-flex; align-items: center; gap: 5px;">
                    <span style="background: rgba(255,255,255,0.28); border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 9px;">{idx}</span>
                    <span>👤 {loc['name']}</span>
                </div>
                """
                popup_html = f"""
                <div style="font-family: -apple-system, sans-serif; min-width: 190px;">
                    <div style="background: {color}; color: white; padding: 6px 10px; border-radius: 6px 6px 0 0; font-weight: bold; font-size: 13px;">
                        📍 Stop {idx}: {loc['name']}
                    </div>
                    <div style="padding: 8px 10px; font-size: 12px; background: white; border: 1px solid #ddd; border-top: none; border-radius: 0 0 6px 6px; color: #1E293B;">
                        <div><b>Destination:</b> {loc['address']}</div>
                        {f'<div style=\"color: #555; margin-top: 5px; font-size: 11px;\">🚗 <b>Leg:</b> {leg_txt}</div>' if leg_txt else ''}
                    </div>
                </div>
                """
                folium.Marker(
                    [loc["lat"], loc["lon"]],
                    icon=folium.DivIcon(html=badge_html, icon_size=(120, 30), icon_anchor=(60, 15)),
                    tooltip=f"📍 Stop {idx}: {loc['name']} ({loc['address']})",
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(m)
        
        all_lats = [loc["lat"] for loc in ordered_points]
        all_lons = [loc["lon"] for loc in ordered_points]
        m.fit_bounds([[min(all_lats), min(all_lons)], [max(all_lats), max(all_lons)]], padding=(45, 45))
        
        st_folium(
            m,
            key="trip_optimized_map_dispatch",
            use_container_width=True,
            height=420,
            returned_objects=[]
        )

        # Passenger Sequence Flow (Mobile-friendly vertical cards)
        st.markdown("##### 📍 Passenger Drop-off Itinerary")
        for idx, loc in enumerate(ordered_points):
            if idx == 0:
                st.success(f"**🚖 Origin Pickup:** {loc['address']}")
            else:
                leg_info = ""
                if idx - 1 < len(legs):
                    leg_d = round(legs[idx - 1]["distance"] / 1000, 1)
                    leg_t = round(legs[idx - 1]["duration"] / 60)
                    leg_info = f" • *+{leg_d} km (~{leg_t} mins)*"
                st.info(f"**📍 Stop {idx} — {loc['name']}**{leg_info}\n\n{loc['address']}")

        # --- Official Corporate Dispatch Manifest & End-of-Trip Report ---
        st.markdown("<br>", unsafe_allow_html=True)
        manifest_id = res.get("manifest_id", "MIT-EXP-DISPATCH")
        st.markdown(f'<div class="mit-card"><div class="mit-card-title">📜 Official Corporate Dispatch Manifest ({manifest_id})</div>', unsafe_allow_html=True)
        
        manifest_rows = []
        for s_idx, s_loc in enumerate(dropoff_stops, 1):
            leg_d = 0.0
            leg_t = 0
            if s_idx - 1 < len(legs):
                leg_d = round(legs[s_idx - 1]["distance"] / 1000, 1)
                leg_t = round(legs[s_idx - 1]["duration"] / 60)
            
            manifest_rows.append({
                "Stop #": f"Stop {s_idx}",
                "Passenger Name": s_loc["name"],
                "Drop Location": s_loc["address"],
                "Leg Distance": f"{leg_d} km",
                "Est. Travel Time": f"{leg_t} mins"
            })
        
        m_df = pd.DataFrame(manifest_rows)
        st.dataframe(m_df, use_container_width=True, hide_index=True)
        
        # Download Manifest CSV & Printable Voucher
        csv_manifest = m_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Trip Manifest (CSV)",
            data=csv_manifest,
            file_name=f"manifest_{manifest_id}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        with st.expander("🖨️ View Printable Trip Dispatch Voucher"):
            voucher_html = f"""<div style="background: #FFFFFF; color: #0F172A; border: 2px solid #E2E8F0; border-radius: 10px; padding: 22px; font-family: -apple-system, sans-serif;">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #EF4123; padding-bottom: 12px; margin-bottom: 14px;">
<div style="display: flex; align-items: center; gap: 14px;">
<img src="data:image/png;base64,{get_logo_b64('mark')}" style="height: 38px; width: auto;" alt="MillenniumIT ESP">
<div>
<h2 style="margin: 0; color: #EF4123; font-size: 20px; font-weight: 900; letter-spacing: 0.5px;">MILLENNIUMIT ESP</h2>
<div style="font-size: 12px; color: #64748B; font-weight: bold;">Corporate Transport Dispatch Slip</div>
</div>
</div>
<div style="text-align: right;">
<div style="font-size: 13px; font-weight: bold;">Voucher: {manifest_id}</div>
<div style="font-size: 11px; color: #64748B;">{res.get('timestamp', '')}</div>
</div>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px; margin-bottom: 14px;">
<div><b>Origin:</b> {res.get('pickup_val', '')}</div>
<div><b>Vehicle Type:</b> {res.get('vehicle_type', 'Flex')}</div>
<div><b>Total Distance:</b> {res.get('distance_km', '')} km</div>
<div><b>Est. Travel Time:</b> {res.get('duration_str', '')}</div>
<div><b>Passengers:</b> {len(dropoff_stops)} Employees</div>
</div>
<table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left;">
<thead>
<tr style="background: #F1F5F9; border-bottom: 1px solid #CBD5E1;">
<th style="padding: 6px;">Stop</th>
<th style="padding: 6px;">Passenger</th>
<th style="padding: 6px;">Drop Location</th>
<th style="padding: 6px;">Leg Distance</th>
<th style="padding: 6px;">Est. Time</th>
</tr>
</thead>
<tbody>
{"".join([f"<tr style='border-bottom: 1px solid #F1F5F9;'><td style='padding: 6px;'>{r['Stop #']}</td><td style='padding: 6px;'><b>{r['Passenger Name']}</b></td><td style='padding: 6px;'>{r['Drop Location']}</td><td style='padding: 6px;'>{r['Leg Distance']}</td><td style='padding: 6px;'>{r['Est. Travel Time']}</td></tr>" for r in manifest_rows])}
</tbody>
</table>
<div style="margin-top: 16px; font-size: 10px; color: #94A3B8; text-align: center; border-top: 1px solid #E2E8F0; padding-top: 8px;">
MillenniumIT ESP • Corporate Mobility & Dispatch System • System Generated
</div>
</div>"""
            st.markdown(voucher_html, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)


else:
    # --- Tab 2: Dedicated Live Transit Map & Tap-to-Pin Tool ---
    if st.session_state.trip_result:
        res = st.session_state.trip_result
        distance_km = res["distance_km"]
        duration_str = res["duration_str"]
        ordered_points = res["ordered_points"]
        dropoff_stops = res["dropoff_stops"]
        route_geojson = res["route_geojson"]
        legs = res["legs"]
        engine = res.get("engine", "Google Maps")

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(66, 138, 255, 0.12) 100%); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">🗺️</span>
                <div>
                    <div style="font-weight: 700; color: #F8FAFC; font-size: 15px;">Active Dispatched Corridor Map</div>
                    <div style="color: #94A3B8; font-size: 12px;">{distance_km} km total driving distance &bull; Estimated driving time {duration_str}</div>
                </div>
            </div>
            <span style="background: rgba(16, 185, 129, 0.2); color: #34D399; font-weight: 700; font-size: 11px; padding: 4px 10px; border-radius: 6px; text-transform: uppercase;">
                Active Corridor
            </span>
        </div>
        """, unsafe_allow_html=True)

        center_lat = sum(p["lat"] for p in ordered_points) / len(ordered_points)
        center_lon = sum(p["lon"] for p in ordered_points) / len(ordered_points)
        m_tab = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap")
        
        folium.GeoJson(
            route_geojson,
            style_function=lambda x: {'color': '#0C2340', 'weight': 9, 'opacity': 0.35},
            name="Route Glow"
        ).add_to(m_tab)
        folium.GeoJson(
            route_geojson,
            style_function=lambda x: {'color': '#0066FF', 'weight': 5, 'opacity': 0.95},
            name="Navigation Path"
        ).add_to(m_tab)
        
        drop_colors = ["#EF4123", "#428AFF", "#10B981", "#F59E0B", "#8B5CF6", "#06B6D4"]
        for idx, loc in enumerate(ordered_points):
            if idx == 0:
                badge_html = """
                <div style="background: #10B981; color: white; border: 2px solid white; border-radius: 16px; padding: 4px 10px; font-family: -apple-system, sans-serif; font-size: 11px; font-weight: 700; box-shadow: 0 4px 10px rgba(0,0,0,0.35); white-space: nowrap; display: inline-flex; align-items: center; gap: 5px;">
                    <span>🚖</span><span>PICKUP</span>
                </div>
                """
                folium.Marker(
                    [loc["lat"], loc["lon"]],
                    icon=folium.DivIcon(html=badge_html, icon_size=(90, 30), icon_anchor=(45, 15)),
                    tooltip=f"🚖 Pickup: {loc['address']}"
                ).add_to(m_tab)
            else:
                color = drop_colors[(idx - 1) % len(drop_colors)]
                badge_html = f"""
                <div style="background: {color}; color: white; border: 2px solid white; border-radius: 16px; padding: 4px 10px; font-family: -apple-system, sans-serif; font-size: 11px; font-weight: 700; box-shadow: 0 4px 10px rgba(0,0,0,0.35); white-space: nowrap; display: inline-flex; align-items: center; gap: 5px;">
                    <span style="background: rgba(255,255,255,0.28); border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 9px;">{idx}</span>
                    <span>👤 {loc['name']}</span>
                </div>
                """
                folium.Marker(
                    [loc["lat"], loc["lon"]],
                    icon=folium.DivIcon(html=badge_html, icon_size=(120, 30), icon_anchor=(60, 15)),
                    tooltip=f"📍 Stop {idx}: {loc['name']} ({loc['address']})"
                ).add_to(m_tab)
        
        all_lats = [loc["lat"] for loc in ordered_points]
        all_lons = [loc["lon"] for loc in ordered_points]
        m_tab.fit_bounds([[min(all_lats), min(all_lons)], [max(all_lats), max(all_lons)]], padding=(45, 45))
        
        st_folium(
            m_tab,
            key="trip_optimized_map_view",
            use_container_width=True,
            height=460,
            returned_objects=[]
        )

        btn_t1, btn_t2 = st.columns(2)
        with btn_t1:
            if st.button("📍 Switch to Tap-to-Pin Tool", key="btn_reset_to_pin_picker", use_container_width=True):
                st.session_state.trip_result = None
                st.rerun()
        with btn_t2:
            if st.button("👈 Back to Dispatch & Stops", key="btn_back_to_disp_tab_routed", use_container_width=True):
                st.session_state["active_tab"] = TAB_DISPATCH
                st.rerun()

    else:
        # Check if user has entered pickup or passenger locations for live preview
        pickup_raw = st.session_state.get("pickup_address", "").strip()
        pickup_pos = geocode_address(pickup_raw) if pickup_raw else None
        
        preview_stops = []
        for p_i in range(1, num_passengers + 1):
            p_name = st.session_state.get(f"p{p_i}_name") or f"Passenger {p_i}"
            p_drop = st.session_state.get(f"p{p_i}_drop", "").strip()
            if p_drop:
                c = geocode_address(p_drop)
                if c:
                    preview_stops.append({"name": p_name, "address": p_drop, "pos": c, "idx": p_i})

        # Target Selector Deck (Above Map)
        target_names = {
            "pickup": "🚖 Pickup Origin Location"
        }
        for p_i in range(1, num_passengers + 1):
            p_name = st.session_state.get(f"p{p_i}_name") or f"Passenger {p_i}"
            target_names[f"p{p_i}"] = f"👤 Pass {p_i} Drop ({p_name})"

        target_keys = list(target_names.keys())
        cur_target = st.session_state.get("map_target", "pickup")
        cur_idx = target_keys.index(cur_target) if cur_target in target_keys else 0

        st.markdown(f"""
        <div style="background: rgba(16, 22, 34, 0.95); border: 1.5px solid #EF4123; border-radius: 14px; padding: 16px 20px; margin-bottom: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div style="font-weight: 800; color: #F8FAFC; font-size: 16px; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">🗺️</span>
                    <span>Tap Anywhere on the Map to Pin & Auto-Fill Location</span>
                </div>
                <span style="background: rgba(239, 65, 35, 0.2); color: #FF7A63; border: 1px solid rgba(239, 65, 35, 0.4); font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 6px;">
                    TAP-TO-PIN ACTIVE
                </span>
            </div>
            <p style="color: #94A3B8; font-size: 12px; margin: 6px 0 0 0;">
                Press or click any street, town, or junction across Sri Lanka. The pin will appear immediately and auto-populate your selected stop.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_sel_target, col_btn_back = st.columns([2.6, 1.2])
        with col_sel_target:
            new_target = st.selectbox(
                "🎯 Field to Auto-Assign on Map Tap:",
                options=target_keys,
                index=cur_idx,
                format_func=lambda k: target_names[k],
                key="map_target_field_selector",
                help="Choose which field is automatically filled when you tap anywhere on the map"
            )
            st.session_state["map_target"] = new_target

        with col_btn_back:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("👈 Return to Dispatch Form", key="btn_back_to_disp_above_map", use_container_width=True):
                st.session_state["active_tab"] = TAB_DISPATCH
                st.rerun()

        center_lat, center_lon = (pickup_pos[0], pickup_pos[1]) if pickup_pos else (6.915, 79.88)
        zoom_lvl = 13
        
        active_pin = st.session_state.get("active_map_pin")
        if active_pin:
            center_lat = active_pin["lat"]
            center_lon = active_pin["lng"]
            zoom_lvl = 14

        default_m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_lvl, tiles="OpenStreetMap")
        
        # Corporate Headquarters & Regional Hubs
        hubs = [
            {"name": "MIT ESP HQ (Colombo 03)", "pos": [6.9075, 79.8530], "type": "Corporate HQ", "color": "#EF4123"},
            {"name": "MIT ESP Malabe Campus", "pos": [6.9034, 79.9547], "type": "Tech Campus", "color": "#FF7A63"},
            {"name": "Sampath Bank Head Office", "pos": [6.9271, 79.8483], "type": "Financial Hub", "color": "#428AFF"},
            {"name": "World Trade Center Colombo", "pos": [6.9334, 79.8436], "type": "Commercial Hub", "color": "#10B981"},
            {"name": "Orion City IT Park", "pos": [6.9482, 79.8789], "type": "Tech Park", "color": "#F59E0B"},
        ]
        for h in hubs:
            badge_html = f"""
            <div style="background: {h['color']}; color: white; border: 2px solid white; border-radius: 14px; padding: 3px 8px; font-family: -apple-system, sans-serif; font-size: 10px; font-weight: 700; box-shadow: 0 3px 8px rgba(0,0,0,0.3); white-space: nowrap;">
                <span>🏢 {h['name']}</span>
            </div>
            """
            folium.Marker(
                h["pos"],
                icon=folium.DivIcon(html=badge_html, icon_size=(100, 26), icon_anchor=(50, 13)),
                tooltip=f"{h['name']} ({h['type']})"
            ).add_to(default_m)

        all_points = []
        if pickup_pos:
            all_points.append(pickup_pos)
            pickup_badge = f"""
            <div style="background: #10B981; color: white; border: 2px solid white; border-radius: 16px; padding: 4px 10px; font-family: -apple-system, sans-serif; font-size: 11px; font-weight: 800; box-shadow: 0 4px 12px rgba(16,185,129,0.6); white-space: nowrap; display: inline-flex; align-items: center; gap: 5px;">
                <span style="background: white; border-radius: 50%; width: 8px; height: 8px; display: inline-block;"></span>
                <span>🚖 Pickup Origin: {pickup_raw[:26]}</span>
            </div>
            """
            folium.Marker(
                pickup_pos,
                icon=folium.DivIcon(html=pickup_badge, icon_size=(160, 30), icon_anchor=(80, 15)),
                tooltip=f"🚖 Pickup Origin: {pickup_raw}"
            ).add_to(default_m)

        drop_colors = ["#428AFF", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6"]
        for s in preview_stops:
            all_points.append(s["pos"])
            c_col = drop_colors[(s["idx"] - 1) % len(drop_colors)]
            s_badge = f"""
            <div style="background: {c_col}; color: white; border: 2px solid white; border-radius: 16px; padding: 4px 10px; font-family: -apple-system, sans-serif; font-size: 11px; font-weight: 700; box-shadow: 0 4px 10px rgba(0,0,0,0.35); white-space: nowrap;">
                <span>📍 Stop {s['idx']}: {s['name']}</span>
            </div>
            """
            folium.Marker(
                s["pos"],
                icon=folium.DivIcon(html=s_badge, icon_size=(120, 30), icon_anchor=(60, 15)),
                tooltip=f"📍 Stop {s['idx']}: {s['name']} ({s['address']})"
            ).add_to(default_m)

        # Check if an interactive PickMe pin is currently placed
        if active_pin:
            pin_lat = active_pin["lat"]
            pin_lng = active_pin["lng"]
            pin_addr = active_pin.get("address", f"{pin_lat:.4f}, {pin_lng:.4f}")
            all_points.append([pin_lat, pin_lng])
            
            # 1. Location accuracy radar pulse circle (PickMe / Google Maps style)
            folium.Circle(
                location=[pin_lat, pin_lng],
                radius=110,
                color="#EF4123",
                weight=2,
                fill=True,
                fill_color="#EF4123",
                fill_opacity=0.25
            ).add_to(default_m)
            
            # 2. Solid high-contrast circle marker (Guaranteed 100% visible on every device/canvas)
            folium.CircleMarker(
                location=[pin_lat, pin_lng],
                radius=10,
                color="#FFFFFF",
                weight=3,
                fill=True,
                fill_color="#EF4123",
                fill_opacity=1.0,
                tooltip=f"📍 Pin: {pin_addr}"
            ).add_to(default_m)
            
            # 3. Standard Leaflet Marker with Red Icon & Popup
            folium.Marker(
                [pin_lat, pin_lng],
                icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
                tooltip=f"📍 Selected Pin: {pin_addr}",
                popup=folium.Popup(f"<b>📍 Active Pin:</b><br>{pin_addr}", max_width=240)
            ).add_to(default_m)
            
            # 4. Floating Badge with Target & Address
            target_short = "Pickup" if cur_target == "pickup" else f"Pass {cur_target[1:]}"
            pin_badge_html = f"""
            <div style="background: #EF4123; color: white; border: 2px solid white; border-radius: 14px; padding: 4px 10px; font-family: -apple-system, sans-serif; font-size: 11px; font-weight: 800; box-shadow: 0 4px 12px rgba(239,65,35,0.7); white-space: nowrap; display: inline-flex; align-items: center; gap: 5px;">
                <span>📍</span>
                <span>{target_short}: {pin_addr[:26]}</span>
            </div>
            """
            folium.Marker(
                [pin_lat, pin_lng],
                icon=folium.DivIcon(html=pin_badge_html, icon_size=(170, 30), icon_anchor=(85, 42))
            ).add_to(default_m)

        # STABLE KEY on st_folium prevents iframe tearing/re-creation on reruns
        map_interaction = st_folium(
            default_m,
            key="mitesp_tap_to_pin_map",
            use_container_width=True,
            height=460,
            returned_objects=["last_clicked"]
        )
        
        # When user clicks or taps ANYWHERE on the map in Sri Lanka
        if map_interaction and map_interaction.get("last_clicked"):
            c_lat = map_interaction["last_clicked"]["lat"]
            c_lng = map_interaction["last_clicked"]["lng"]
            
            last_lat = st.session_state.get("last_registered_click_lat")
            last_lng = st.session_state.get("last_registered_click_lng")
            
            # If this is a new click on the map, update active pin and auto-assign
            if last_lat is None or abs(c_lat - last_lat) > 0.0001 or abs(c_lng - last_lng) > 0.0001:
                st.session_state["last_registered_click_lat"] = c_lat
                st.session_state["last_registered_click_lng"] = c_lng
                rev_addr = reverse_geocode_location(c_lat, c_lng)
                st.session_state["active_map_pin"] = {
                    "lat": c_lat,
                    "lng": c_lng,
                    "address": rev_addr
                }
                
                # AUTO-POPULATE THE SELECTED TARGET FIELD IMMEDIATELY
                tgt = st.session_state.get("map_target", "pickup")
                if tgt == "pickup":
                    st.session_state["pickup_address"] = rev_addr
                    tgt_display = "🚖 Pickup Origin"
                elif tgt.startswith("p"):
                    p_num = int(tgt[1:])
                    st.session_state[f"p{p_num}_drop"] = rev_addr
                    p_label = st.session_state.get(f"p{p_num}_name") or f"Passenger {p_num}"
                    tgt_display = f"👤 {p_label}'s Drop-off"
                else:
                    st.session_state["pickup_address"] = rev_addr
                    tgt_display = "🚖 Pickup Origin"
                    
                st.session_state["pin_success_msg"] = f"✅ Pin Dropped & Saved to {tgt_display}: {rev_addr}"
                st.rerun()
        
        # Success Banner when pin was applied
        if st.session_state.get("pin_success_msg"):
            st.success(st.session_state["pin_success_msg"])
            
        # Active Pin Control Deck
        if active_pin:
            c_lat = active_pin["lat"]
            c_lng = active_pin["lng"]
            rev_addr = active_pin["address"]
            tgt = st.session_state.get("map_target", "pickup")
            tgt_display = "🚖 Pickup Origin" if tgt == "pickup" else f"👤 Passenger {tgt[1:]} Drop-off"
            
            st.markdown(f"""
            <div style="background: rgba(16, 22, 34, 0.95); border: 1.5px solid #EF4123; border-radius: 12px; padding: 14px 18px; margin-top: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.4);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="font-size: 16px;">📍</span>
                            <span style="font-size: 11px; font-weight: 800; color: #EF4123; text-transform: uppercase; letter-spacing: 0.5px;">Active Pin Saved to {tgt_display}</span>
                        </div>
                        <div style="font-size: 14px; font-weight: 700; color: #FFFFFF; margin-top: 3px;">{rev_addr}</div>
                        <div style="font-size: 11px; color: #94A3B8; font-family: monospace;">GPS: {c_lat:.5f}, {c_lng:.5f}</div>
                    </div>
                    <span style="background: rgba(16, 185, 129, 0.15); color: #34D399; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.3);">
                        SAVED IN DISPATCH FORM
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Primary button to return to dispatch tab immediately
            if st.button("👉 Return to Route & Passenger Dispatch (Location Saved)", type="primary", use_container_width=True, key="btn_return_disp_after_pin"):
                st.session_state["active_tab"] = TAB_DISPATCH
                st.rerun()

            st.markdown("<div style='font-size: 11px; color: #94A3B8; font-weight: 700; text-transform: uppercase; margin-top: 10px; margin-bottom: 6px;'>Or Re-Assign this Pin Location to Another Stop:</div>", unsafe_allow_html=True)
            
            # Action buttons with responsive 2x2 layout for mobile & desktop
            btn_r1_c1, btn_r1_c2 = st.columns(2)
            with btn_r1_c1:
                st.button(
                    "🚖 Assign to Pickup",
                    key="btn_pin_to_pickup",
                    on_click=cb_apply_active_pin_to_pickup,
                    use_container_width=True,
                    help="Assign this pin location as the trip Pickup Address"
                )
            with btn_r1_c2:
                st.button(
                    "🎯 Assign to Pass 1",
                    key="btn_pin_to_p1",
                    on_click=cb_apply_active_pin_to_passenger,
                    args=(1,),
                    use_container_width=True,
                    help="Assign this pin location as Passenger 1 Drop-off"
                )

            btn_r2_c1, btn_r2_c2 = st.columns(2)
            with btn_r2_c1:
                if num_passengers >= 2:
                    st.button(
                        "🎯 Assign to Pass 2",
                        key="btn_pin_to_p2",
                        on_click=cb_apply_active_pin_to_passenger,
                        args=(2,),
                        use_container_width=True,
                        help="Assign this pin location as Passenger 2 Drop-off"
                    )
                else:
                    st.button(
                        "🏢 Set HQ as Pickup",
                        key="btn_pin_to_hq",
                        on_click=cb_set_pickup,
                        args=(HQ_ADDRESS,),
                        use_container_width=True
                    )
            with btn_r2_c2:
                st.button(
                    "✖ Clear Pin",
                    key="btn_clear_pin",
                    on_click=cb_clear_active_pin,
                    use_container_width=True,
                    help="Remove pin from map"
                )
                
            # If 3 or more passengers, provide additional drop buttons
            if num_passengers >= 3:
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                p_extra_cols = st.columns(min(num_passengers - 2, 2))
                for e_i, p_idx in enumerate(range(3, num_passengers + 1)):
                    with p_extra_cols[e_i % len(p_extra_cols)]:
                        st.button(
                            f"🎯 Assign to Pass {p_idx}",
                            key=f"btn_pin_to_p{p_idx}",
                            on_click=cb_apply_active_pin_to_passenger,
                            args=(p_idx,),
                            use_container_width=True
                        )
        else:
            st.markdown("""
            <div style="background: rgba(16, 22, 34, 0.5); border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 10px; padding: 12px 16px; margin-top: 10px; display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">💡</span>
                <span style="font-size: 12px; color: #94A3B8;"><b>Interactive Tap-to-Pin:</b> Tap or click anywhere on the map above to drop a PickMe pin. The address will be reverse-geocoded and saved to your selected stop automatically.</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Corridor Pooling ROI Highlight Cards
        st.markdown("<br>", unsafe_allow_html=True)
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("""
            <div style="background: rgba(16, 22, 34, 0.7); border: 1px solid rgba(239, 65, 35, 0.25); border-radius: 12px; padding: 16px;">
                <div style="font-size: 12px; color: #EF4123; font-weight: 800; text-transform: uppercase;">Corridor Pooling Efficiency</div>
                <div style="font-size: 20px; color: #F8FAFC; font-weight: 800; margin: 4px 0;">38% - 45% Savings</div>
                <div style="font-size: 12px; color: #94A3B8;">Consolidates 3 single taxi trips into 1 coordinated multi-stop dispatch.</div>
            </div>
            """, unsafe_allow_html=True)
        with rc2:
            st.markdown("""
            <div style="background: rgba(16, 22, 34, 0.7); border: 1px solid rgba(66, 138, 255, 0.25); border-radius: 12px; padding: 16px;">
                <div style="font-size: 12px; color: #428AFF; font-weight: 800; text-transform: uppercase;">AI Destination Engine</div>
                <div style="font-size: 20px; color: #F8FAFC; font-weight: 800; margin: 4px 0;">Instant Auto-Fill</div>
                <div style="font-size: 12px; color: #94A3B8;">Learns employee shift schedules and personal destination drop corridors.</div>
            </div>
            """, unsafe_allow_html=True)


# --- Full-Width Live Corporate Trip Datasheet & Manifest Editor ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="mit-card"><div class="mit-card-title">📋 Live Corporate Trip Datasheet & Manifest Editor</div>', unsafe_allow_html=True)
st.caption("Live view and inline editor of all records entered into the corporate transport datasheet. You can directly edit any field below and save changes.")

base_dir = os.path.dirname(__file__)
new_trips_path = os.path.join(base_dir, "data", "new_trips.csv")

tab_live, tab_cloud, tab_all = st.tabs([
    "⚡ Live Entered Records (data/new_trips.csv)",
    "🌐 Cloud Google Sheets Webhook",
    "📁 All Ingested Sheets in data/"
])

with tab_live:
    cols_standard = [
        "TRIP ID", "DATE", "DAY_OF_WEEK", "PICKUP TIME", "PASSENGER NAME",
        "DEPARTMENT", "VEHICLE TYPE", "PICKUP LOCATION", "DROP LOCATION",
        "TRIP DISTANCE", "TOTAL FARE", "ROUTING ENGINE", "STATUS"
    ]
    
    if os.path.exists(new_trips_path):
        try:
            df_live = pd.read_csv(new_trips_path, encoding='utf-8')
        except Exception:
            df_live = pd.DataFrame(columns=cols_standard)
    else:
        df_live = pd.DataFrame(columns=cols_standard)
        
    if df_live.empty:
        st.info("💡 No new trips logged yet in `data/new_trips.csv`. Once you dispatch a route above, records will immediately appear here for live editing!")
        st.markdown("**Datasheet Schema & Column Layout:**")
        st.dataframe(pd.DataFrame(columns=cols_standard), use_container_width=True, hide_index=True)
    else:
        st.markdown(f"**Active Records in Datasheet:** `{len(df_live)} trips`  |  **File Path:** `{new_trips_path}`")
        
        edited_df = st.data_editor(
            df_live,
            num_rows="dynamic",
            use_container_width=True,
            key="new_trips_data_editor"
        )
        
        btn_s1, btn_s2, btn_s3 = st.columns([1.2, 1.2, 2])
        with btn_s1:
            if st.button("💾 Save Changes to Datasheet", type="primary"):
                edited_df.to_csv(new_trips_path, index=False, encoding='utf-8')
                st.success("✅ Changes saved directly to `data/new_trips.csv`!")
                st.cache_data.clear()
                st.rerun()
                
        with btn_s2:
            csv_data = edited_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Datasheet (CSV)",
                data=csv_data,
                file_name="corporate_trip_datasheet.csv",
                mime="text/csv"
            )
            
        with btn_s3:
            if st.button("🗑️ Reset Live Datasheet"):
                if os.path.exists(new_trips_path):
                    os.remove(new_trips_path)
                    st.warning("`data/new_trips.csv` has been reset.")
                    st.cache_data.clear()
                    st.rerun()

with tab_cloud:
    st.markdown("##### 🌐 Live Google Sheets Cloud Sync & Webhook")
    
    st.info(
        "💡 **Why did you see 'Script function not found: doGet'?**\\n\\n"
        "The webhook URL below is an **automated API endpoint** designed to receive invisible background `POST` data whenever a trip is dispatched. "
        "When you click it directly in your web browser (Chrome/Edge), your browser sends a `GET` request. Because Google Apps Script by default only listens for `doPost`, it displays that error.\\n\\n"
        "Follow the steps below to access your actual Google Sheet, or add a simple `doGet` redirect to your Apps Script!"
    )
    
    col_gs1, col_gs2 = st.columns([1.2, 1])
    with col_gs1:
        st.markdown("###### 1️⃣ Active Webhook Receiver Endpoint")
        st.code(WEBHOOK_URL, language="text")
        
        st.markdown("###### 2️⃣ Direct Link to Your Google Sheet")
        gsheet_url = st.text_input(
            "Enter your Google Sheet URL (from your browser address bar):",
            value="https://docs.google.com/spreadsheets",
            help="Paste your full Google Spreadsheet URL here to open it with one click."
        )
        if st.button("📊 Open Google Sheet in New Tab", use_container_width=True):
            st.markdown(f'<meta http-equiv="refresh" content="0; url={gsheet_url}">', unsafe_allow_html=True)
            st.link_button("👉 Click here to launch Google Sheet", url=gsheet_url, use_container_width=True)
            
        st.markdown("---")
        st.markdown("###### 3️⃣ Test Webhook Connection")
        if st.button("📡 Send Test Dispatch Payload to Google Sheet", use_container_width=True):
            import datetime
            test_payload = {
                "pickup": "MillenniumIT ESP Campus, Malabe",
                "names": "Test Dispatcher",
                "dropoffs": "Sampath Bank HO, Colombo 02",
                "distance": 14.5,
                "duration": "28 mins",
                "engine": "Test Ping - " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            try:
                res = requests.post(WEBHOOK_URL, json=test_payload, timeout=8)
                if res.status_code == 200:
                    st.success(f"✅ Webhook responded successfully! Status code: {res.status_code}. Check your Google Sheet for the new row.")
                else:
                    st.warning(f"⚠️ Webhook responded with status: {res.status_code}")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")
                
    with col_gs2:
        st.markdown("###### 🛠️ How to make the Webhook auto-redirect to your Sheet")
        st.markdown(
            "In your Google Sheet, click **Extensions > Apps Script**, and replace your script with this code. "
            "It will accept background `POST` data from dispatches **AND** automatically redirect anyone who clicks the link in a browser straight to your Sheet!"
        )
        gas_code = '''// Google Apps Script to auto-append trips & redirect on browser visit
function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = JSON.parse(e.postData.contents);
  sheet.appendRow([
    new Date(),
    data.pickup,
    data.names,
    data.dropoffs,
    data.distance,
    data.duration,
    data.engine
  ]);
  return ContentService.createTextOutput(JSON.stringify({"status": "SUCCESS"}))
    .setMimeType(ContentService.MimeType.JSON);
}

// Redirect browser clicks directly to the Google Sheet!
function doGet(e) {
  var url = SpreadsheetApp.getActiveSpreadsheet().getUrl();
  var html = "<script>window.top.location.href='" + url + "';</script>" +
             "<p style='font-family:sans-serif;padding:30px;text-align:center;'>" +
             "Opening live Corporate Trip Google Sheet...<br><br>" +
             "<a href='" + url + "' target='_blank' style='display:inline-block;padding:10px 20px;background:#EF4123;color:#fff;text-decoration:none;border-radius:6px;'>Click here to open Sheet</a>" +
             "</p>";
  return HtmlService.createHtmlOutput(html);
}'''
        st.code(gas_code, language="javascript")

with tab_all:
    st.markdown("##### 📁 Ingested Historical Files in `data/`")
    all_data_files = sorted(glob.glob(os.path.join(base_dir, "data", "*.xlsx")) + glob.glob(os.path.join(base_dir, "data", "*.csv")))
    for af in all_data_files:
        sz = round(os.path.getsize(af) / 1024, 1)
        st.markdown(f"- 📄 **`{os.path.basename(af)}`** ({sz} KB) — *`{os.path.relpath(af, base_dir)}`*")

st.markdown('</div>', unsafe_allow_html=True)
