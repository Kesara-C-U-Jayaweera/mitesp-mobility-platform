import streamlit as st
import pandas as pd
import os
import re
import glob
import sys

# Ensure root dir is on path for brand imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brand import get_favicon, render_brand_header, render_sidebar_logo

st.set_page_config(
    page_title="MIT ESP | Transport Analytics Dashboard",
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
        margin-bottom: 18px;
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
        margin-bottom: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Metric cards */
    .mit-stat-card {
        background: rgba(16, 22, 34, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 14px;
        padding: 18px 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .mit-stat-card:hover {
        transform: translateY(-2px);
    }

    .mit-stat-label {
        font-size: 11px;
        font-weight: 700;
        color: #CBD5E1 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }

    .mit-stat-value {
        font-size: 26px;
        font-weight: 800;
        color: #FFFFFF !important;
        line-height: 1.1;
        margin-bottom: 4px;
    }

    .mit-stat-sub {
        font-size: 12px;
        font-weight: 600;
        color: #94A3B8 !important;
    }

    /* Inputs & Select */
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

    /* Primary buttons */
    button[kind="primary"], .stButton > button[type="primary"] {
        background: linear-gradient(135deg, #EF4123 0%, #F97316 45%, #428AFF 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 18px rgba(239, 65, 35, 0.35) !important;
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
            font-size: 16px !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 18px !important;
        }
    }

    /* Route list item */
    .route-row {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s ease;
    }
    .route-row:hover {
        background: rgba(66, 138, 255, 0.10);
        border-color: rgba(66, 138, 255, 0.35);
    }
</style>
""", unsafe_allow_html=True)

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from auth import init_auth_state, render_user_sidebar
    init_auth_state()
    with st.sidebar:
        st.markdown(render_sidebar_logo(), unsafe_allow_html=True)
        render_user_sidebar()
except Exception:
    pass

# Excel file fallback
EXCEL_FILENAME = "Pickme cost - Apr-Aug 2026 (Test) (2).xlsx"
EXCEL_SHEET = "Individual Trips Summary"


def _parse_hour(val):
    """Extract hour (0-23) from time strings."""
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
def load_data():
    """Load trip data from all files in data/ directory (primary) or root files (fallback)."""
    base = os.path.dirname(os.path.dirname(__file__))
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
        'Trip ID': 'TRIP ID',
    }

    dfs = []

    if os.path.exists(data_dir):
        xlsx_files = sorted(glob.glob(os.path.join(data_dir, "*.xlsx")))
        csv_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))

        for fpath in xlsx_files:
            try:
                df_f = None
                for sheet in [EXCEL_SHEET, 'Sheet1', 0]:
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

    # Normalize Trip ID and strictly deduplicate to guarantee 100% data fidelity
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
        df['hour'] = df['PICKUP TIME'].apply(_parse_hour)
    else:
        df['hour'] = None

    if 'DAY_OF_WEEK' in df.columns:
        df['day_of_week'] = df['DAY_OF_WEEK']
    else:
        df['day_of_week'] = pd.Series(dtype=str)

    return df


df_raw = load_data()
if df_raw.empty:
    st.error("No trip data found! Place Excel/CSV files in the data/ folder.")
    st.stop()

# Physical spacer to guarantee complete clearance under Streamlit Cloud fixed header bar
st.markdown('<div class="header-clearance-spacer" style="height: 56px; width: 100%; display: block;"></div>', unsafe_allow_html=True)

# --- MillenniumIT ESP Corporate Header Banner ---
total_trips = len(df_raw)
total_spend = df_raw['fare_num'].sum()
total_dist = df_raw['distance_num'].sum()
unique_emp = df_raw['PASSENGER NAME'].nunique()
unique_depts = df_raw['DEPARTMENT'].nunique() if 'DEPARTMENT' in df_raw.columns else 1

dash_header_html = f"""<div style="background: linear-gradient(135deg, rgba(16, 22, 34, 0.95) 0%, rgba(11, 15, 23, 0.95) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-top: 3px solid #EF4123; border-radius: 16px; padding: 22px 28px; margin-bottom: 24px; box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45); backdrop-filter: blur(16px);">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
<div>
{render_brand_header("ENTERPRISE ANALYTICS", height_px=34)}
<h1 style="margin: 0; font-size: 26px; font-weight: 800; background: linear-gradient(135deg, #FFFFFF 30%, #E2E8F0 60%, #94A3B8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px;">Transport Spend & Fleet Intelligence</h1>
<p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 13px;">Corporate mobility performance, expenditure trends, peak transit corridors, and employee usage metrics.</p>
</div>
<div style="display: flex; gap: 10px; flex-wrap: wrap;">
<div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 8px 14px; text-align: center;">
<div style="font-size: 10px; color: #64748B; font-weight: 700; text-transform: uppercase;">Total Trips</div>
<div style="font-size: 14px; color: #F8FAFC; font-weight: 800;">{total_trips:,}</div>
</div>
<div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 8px 14px; text-align: center;">
<div style="font-size: 10px; color: #64748B; font-weight: 700; text-transform: uppercase;">Total Spend</div>
<div style="font-size: 14px; color: #EF4123; font-weight: 800;">LKR {total_spend/1_000_000:.2f}M</div>
</div>
<div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 8px 14px; text-align: center;">
<div style="font-size: 10px; color: #64748B; font-weight: 700; text-transform: uppercase;">Employees</div>
<div style="font-size: 14px; color: #428AFF; font-weight: 800;">{unique_emp}</div>
</div>
<div style="background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 8px 14px; text-align: center;">
<div style="font-size: 10px; color: #64748B; font-weight: 700; text-transform: uppercase;">Departments</div>
<div style="font-size: 14px; color: #10B981; font-weight: 800;">{unique_depts} LOBs</div>
</div>
</div>
</div>
</div>"""
st.markdown(dash_header_html, unsafe_allow_html=True)

# --- Interactive Filter Bar ---
with st.container():
    st.markdown('<div class="mit-card"><div class="mit-card-title">🔍 Interactive Filters & Cohort Analysis</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    
    with f1:
        depts = ["All Departments"] + sorted([str(d) for d in df_raw['DEPARTMENT'].dropna().unique()]) if 'DEPARTMENT' in df_raw.columns else ["All Departments"]
        sel_dept = st.selectbox("Filter by Department (LOB)", depts, index=0)
        
    with f2:
        vtypes = ["All Vehicles"] + sorted([str(v) for v in df_raw['VEHICLE TYPE'].dropna().unique()]) if 'VEHICLE TYPE' in df_raw.columns else ["All Vehicles"]
        sel_vtype = st.selectbox("Filter by Vehicle Type", vtypes, index=0)

    with f3:
        shift_opts = ["All Shift Windows", "Night Shift (8 PM - 5 AM)", "Morning (6 AM - 11 AM)", "Afternoon (12 PM - 7 PM)"]
        sel_shift = st.selectbox("Time Window", shift_opts, index=0)

    with f4:
        emp_search = st.text_input("Search Employee Name", placeholder="e.g. Priyantha, Dilshan...")

    st.markdown('</div>', unsafe_allow_html=True)

# Apply filters
df = df_raw.copy()
if sel_dept != "All Departments" and 'DEPARTMENT' in df.columns:
    df = df[df['DEPARTMENT'] == sel_dept]
if sel_vtype != "All Vehicles" and 'VEHICLE TYPE' in df.columns:
    df = df[df['VEHICLE TYPE'] == sel_vtype]
if sel_shift == "Night Shift (8 PM - 5 AM)":
    df = df[df['hour'].apply(lambda h: h is not None and (h >= 20 or h <= 5))]
elif sel_shift == "Morning (6 AM - 11 AM)":
    df = df[df['hour'].apply(lambda h: h is not None and (6 <= h <= 11))]
elif sel_shift == "Afternoon (12 PM - 7 PM)":
    df = df[df['hour'].apply(lambda h: h is not None and (12 <= h <= 19))]

if emp_search.strip():
    df = df[df['PASSENGER NAME'].str.contains(emp_search.strip(), case=False, na=False)]

if df.empty:
    st.warning("⚠️ No trips match the selected filters. Please broaden your selection.")
    st.stop()

# --- Summary KPI Cards (Custom Glassmorphism) ---
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""
    <div class="mit-stat-card" style="border-left: 3px solid #EF4123;">
        <div class="mit-stat-label">🚕 Filtered Trips</div>
        <div class="mit-stat-value">{len(df):,}</div>
        <div class="mit-stat-sub">{(len(df)/len(df_raw)*100):.1f}% of total</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="mit-stat-card" style="border-left: 3px solid #428AFF;">
        <div class="mit-stat-label">💰 Filtered Spend</div>
        <div class="mit-stat-value">LKR {df['fare_num'].sum():,.0f}</div>
        <div class="mit-stat-sub">Avg LKR {df['fare_num'].mean():,.0f} / trip</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="mit-stat-card" style="border-left: 3px solid #10B981;">
        <div class="mit-stat-label">📏 Fleet Distance</div>
        <div class="mit-stat-value">{df['distance_num'].sum():,.1f} km</div>
        <div class="mit-stat-sub">Avg {df['distance_num'].mean():,.1f} km / trip</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="mit-stat-card" style="border-left: 3px solid #F59E0B;">
        <div class="mit-stat-label">👥 Active Travelers</div>
        <div class="mit-stat-value">{df['PASSENGER NAME'].nunique()}</div>
        <div class="mit-stat-sub">{(len(df)/max(1, df['PASSENGER NAME'].nunique())):.1f} trips / person</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    fuel_est = df['distance_num'].sum() * 0.085  # ~8.5 L per 100km
    st.markdown(f"""
    <div class="mit-stat-card" style="border-left: 3px solid #8B5CF6;">
        <div class="mit-stat-label">⛽ Est. Fuel Used</div>
        <div class="mit-stat-value">{fuel_est:,.0f} L</div>
        <div class="mit-stat-sub">~{(fuel_est*2.31/1000):.1f} T CO₂</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Charts Row 1 ---
c_r1_1, c_r1_2 = st.columns(2)

with c_r1_1:
    st.markdown('<div class="mit-card"><div class="mit-card-title">🏆 Top 15 Employees by Total Spend</div>', unsafe_allow_html=True)
    top_emp = df.groupby('PASSENGER NAME')['fare_num'].sum().nlargest(15).sort_values(ascending=True)
    st.bar_chart(top_emp, horizontal=True, color="#EF4123")
    st.markdown('</div>', unsafe_allow_html=True)

with c_r1_2:
    st.markdown('<div class="mit-card"><div class="mit-card-title">🚗 Vehicle Type Fleet Distribution</div>', unsafe_allow_html=True)
    vtype = df['VEHICLE TYPE'].value_counts()
    st.bar_chart(vtype, color="#428AFF")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Charts Row 2 ---
c_r2_1, c_r2_2 = st.columns(2)

with c_r2_1:
    st.markdown('<div class="mit-card"><div class="mit-card-title">🕐 Peak Dispatch Hours (00:00 - 23:00)</div>', unsafe_allow_html=True)
    hour_data = df['hour'].dropna().astype(int)
    hour_counts = hour_data.value_counts().reindex(range(24), fill_value=0).sort_index()
    hour_counts.index = [f"{h:02d}:00" for h in hour_counts.index]
    st.bar_chart(hour_counts, color="#10B981")
    st.markdown('</div>', unsafe_allow_html=True)

with c_r2_2:
    st.markdown('<div class="mit-card"><div class="mit-card-title">📅 Trip Volume by Day of Week</div>', unsafe_allow_html=True)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df['day_of_week'].value_counts().reindex(day_order, fill_value=0)
    st.bar_chart(day_counts, color="#F59E0B")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Department Breakdown ---
if 'DEPARTMENT' in df.columns and df['DEPARTMENT'].nunique() > 1:
    st.markdown('<div class="mit-card"><div class="mit-card-title">🏢 Departmental Budget & Trip Load Allocation</div>', unsafe_allow_html=True)
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.markdown("<p style='font-size: 13px; color: #94A3B8;'>Trips Dispatched by Department</p>", unsafe_allow_html=True)
        dept_trips = df['DEPARTMENT'].value_counts().head(12).sort_values(ascending=True)
        st.bar_chart(dept_trips, horizontal=True, color="#428AFF")
    with d_col2:
        st.markdown("<p style='font-size: 13px; color: #94A3B8;'>Total Spend (LKR) by Department</p>", unsafe_allow_html=True)
        dept_spend = df.groupby('DEPARTMENT')['fare_num'].sum().nlargest(12).sort_values(ascending=True)
        st.bar_chart(dept_spend, horizontal=True, color="#EF4123")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Distance Distribution & Stats ---
st.markdown('<div class="mit-card"><div class="mit-card-title">📏 Trip Distance Distribution & Statistics</div>', unsafe_allow_html=True)
dist_col1, dist_col2 = st.columns([2, 1])
with dist_col1:
    bins = [0, 5, 10, 20, 30, 50, 100, 500]
    labels = ['0-5 km', '5-10 km', '10-20 km', '20-30 km', '30-50 km', '50-100 km', '100+ km']
    dist_bins = pd.cut(df['distance_num'], bins=bins, labels=labels, right=True)
    dist_chart = dist_bins.value_counts().reindex(labels, fill_value=0)
    st.bar_chart(dist_chart, color="#8B5CF6")

with dist_col2:
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px;">
        <div style="font-size: 13px; font-weight: 700; color: #F8FAFC; margin-bottom: 10px;">Distance Telemetry</div>
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #94A3B8; font-size: 12px;">Minimum</span>
            <span style="color: #FFFFFF; font-weight: 700; font-size: 12px;">{df['distance_num'].min():.1f} km</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #94A3B8; font-size: 12px;">Median (50th %)</span>
            <span style="color: #FFFFFF; font-weight: 700; font-size: 12px;">{df['distance_num'].median():.1f} km</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #94A3B8; font-size: 12px;">Average (Mean)</span>
            <span style="color: #428AFF; font-weight: 700; font-size: 12px;">{df['distance_num'].mean():.1f} km</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #94A3B8; font-size: 12px;">Maximum</span>
            <span style="color: #EF4123; font-weight: 700; font-size: 12px;">{df['distance_num'].max():.1f} km</span>
        </div>
        <div style="display: flex; justify-content: space-between; padding: 6px 0;">
            <span style="color: #94A3B8; font-size: 12px;">Std. Deviation</span>
            <span style="color: #94A3B8; font-weight: 700; font-size: 12px;">±{df['distance_num'].std():.1f} km</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Top High-Frequency Corridors ---
st.markdown('<div class="mit-card"><div class="mit-card-title">🔝 Top High-Frequency Corridors (Ideal for Carpooling)</div>', unsafe_allow_html=True)
df_routes = df.copy()
df_routes['pickup_short'] = df_routes['PICKUP LOCATION'].astype(str).str[:40]
df_routes['drop_short'] = df_routes['DROP LOCATION'].astype(str).str[:40]
df_routes['route'] = df_routes['pickup_short'] + '  ➔  ' + df_routes['drop_short']
top_routes = df_routes['route'].value_counts().head(10)

route_c1, route_c2 = st.columns(2)
for rank, (route, count) in enumerate(top_routes.items(), 1):
    target_col = route_c1 if rank <= 5 else route_c2
    with target_col:
        st.markdown(f"""
        <div class="route-row">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="background: rgba(66, 138, 255, 0.15); border: 1px solid rgba(66, 138, 255, 0.3); color: #82B1FF; font-weight: 800; font-size: 11px; padding: 2px 8px; border-radius: 6px;">#{rank}</span>
                <span style="color: #F8FAFC; font-size: 12px; font-weight: 600;">{route}</span>
            </div>
            <span style="background: rgba(239, 65, 35, 0.15); color: #FF7043; font-weight: 800; font-size: 12px; padding: 3px 10px; border-radius: 12px; white-space: nowrap;">
                {count} trips
            </span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Rate per KM by Vehicle Type ---
st.markdown('<div class="mit-card"><div class="mit-card-title">💰 Fare Per KM Rate Benchmark by Fleet Type</div>', unsafe_allow_html=True)
fare_analysis = df[df['distance_num'] > 0].copy()
fare_analysis['fare_per_km'] = fare_analysis['fare_num'] / fare_analysis['distance_num']
fare_by_vehicle = fare_analysis.groupby('VEHICLE TYPE')['fare_per_km'].agg(['mean', 'min', 'max', 'count']).round(1)
fare_by_vehicle.columns = ['Avg LKR/km', 'Min LKR/km', 'Max LKR/km', 'Trip Count']
st.dataframe(fare_by_vehicle, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Employee Summary Table ---
st.markdown('<div class="mit-card"><div class="mit-card-title">👤 Employee Trip & Spend Ledger</div>', unsafe_allow_html=True)
emp_summary = df.groupby('PASSENGER NAME').agg(
    Trips=('TRIP ID', 'count'),
    Total_Distance_km=('distance_num', 'sum'),
    Total_Fare_LKR=('fare_num', 'sum'),
    Avg_Fare_LKR=('fare_num', 'mean'),
).round(1).sort_values('Total_Fare_LKR', ascending=False)

fav_vehicle = df.groupby('PASSENGER NAME')['VEHICLE TYPE'].agg(
    lambda x: x.mode().iloc[0] if not x.mode().empty else 'N/A'
)
emp_summary['Fav_Vehicle'] = fav_vehicle

if 'DEPARTMENT' in df.columns:
    dept_info = df.groupby('PASSENGER NAME')['DEPARTMENT'].first()
    emp_summary['Department'] = dept_info

st.dataframe(emp_summary, use_container_width=True, height=500)
st.markdown(f"<p style='color: #64748B; font-size: 11px; margin-top: 8px;'>Active records: {len(df):,} trips | {df['PASSENGER NAME'].nunique()} employees</p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
