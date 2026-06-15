import streamlit as st
from supabase import create_client, Client
from postgrest.exceptions import APIError
import hashlib
import pandas as pd
import plotly.express as px
import requests

# --- SUPABASE CONFIGURATION ---
raw_url = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SUPABASE_URL = raw_url.split("/rest/v1")[0].strip("/")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- API INTEGRATIONS ---
@st.cache_data(ttl=3600)
def get_live_exchange_rates():
    try:
        url = "https://api.frankfurter.app/latest?from=INR&to=USD,EUR,GBP"
        response = requests.get(url, timeout=5)
        return response.json().get("rates", {}) if response.status_code == 200 else None
    except Exception: return None

@st.cache_data(ttl=600)
def get_crypto_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=inr"
        response = requests.get(url, timeout=5)
        return response.json() if response.status_code == 200 else None
    except Exception: return None

@st.cache_data(ttl=86400)
def get_daily_motivation():
    try:
        url = "https://zenquotes.io/api/today"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return f'"{data[0]["q"]}" — {data[0]["a"]}'
        return "Small daily savings compound into massive future freedom! ✨"
    except Exception: return "Small daily savings compound into massive future freedom! ✨"

# --- THE FINORA CLEAN UI THEME ---
st.set_page_config(page_title="Finora", page_icon="💳", layout="wide")

st.markdown("""
    <style>
    [data-testid="stHeader"] {background: transparent; height: 0rem;}
    div.block-container {padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important;}
    .main-header {font-size: 30px !important; font-weight: 800 !important; letter-spacing: -0.8px; background: linear-gradient(135deg, #10b981 0%, #0284c7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .section-header {font-size: 22px !important; font-weight: 700 !important; letter-spacing: -0.4px; color: #0f172a; margin-top: 2px !important; margin-bottom: 10px !important;}
    .metric-card {background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px 22px; box-shadow: 0 4px 15px rgba(15, 23, 42, 0.03); margin-bottom: 14px;}
    div.stButton > button:first-child {text-align: left !important; width: 100%; border: 1px solid #e2e8f0; background-color: #ffffff; padding: 12px 16px; font-weight: 600; border-radius: 10px; margin-bottom: 5px; color: #475569;}
    div.stButton > button:first-child:hover {border-color: #10b981; color: #10b981; background: linear-gradient(90deg, #f0fdf4 0%, #ffffff 100%);}
    </style>
""", unsafe_allow_html=True)

# --- APP LOGIC ---
if "username" not in st.session_state: st.session_state.username = None
if "nav_selection" not in st.session_state: st.session_state.nav_selection = "Dashboard"

def login_page():
    st.markdown("<div style='text-align: center;'><span class='main-header'>Finora</span></div>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1.4, 1.2, 1.4])
    with col2:
        with st.form("login_form"):
            user_input = st.text_input("Username").strip().lower()
            pass_input = st.text_input("Password", type="password")
            if st.form_submit_button("Enter Finora", use_container_width=True):
                # Add your Auth check logic here
                st.session_state.username = user_input
                st.rerun()

def show_dashboard(username):
    st.markdown("<p class='section-header'>Dashboard</p>", unsafe_allow_html=True)
    st.write(f"Welcome back, {username.upper()}.")

def show_savings():
    st.markdown("<p class='section-header'>Savings Multiplier</p>", unsafe_allow_html=True)
    # Savings calculator logic remains here as previously defined...
    st.info("Finora's core multiplier engine is active.")

# --- NAVIGATION ---
if st.session_state.username is None:
    login_page()
else:
    with st.sidebar:
        st.markdown("<p class='main-header'>Finora</p>", unsafe_allow_html=True)
        if st.button("Dashboard"): st.session_state.nav_selection = "Dashboard"; st.rerun()
        if st.button("Savings Multiplier"): st.session_state.nav_selection = "Savings"; st.rerun()
        if st.button("Log Out"): st.session_state.username = None; st.rerun()

    if st.session_state.nav_selection == "Dashboard": show_dashboard(st.session_state.username)
    elif st.session_state.nav_selection == "Savings": show_savings()
