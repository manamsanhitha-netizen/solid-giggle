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

# --- FREE PUBLIC API INTEGRATIONS ---
@st.cache_data(ttl=3600)
def get_live_exchange_rates():
    try:
        url = "https://api.frankfurter.app/latest?from=INR&to=USD,EUR,GBP"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get("rates", {})
        return None
    except Exception:
        return None

@st.cache_data(ttl=600)
def get_crypto_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=inr"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

@st.cache_data(ttl=86400)
def get_daily_motivation():
    try:
        url = "https://zenquotes.io/api/today"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return f'"{data[0]["q"]}" — {data[0]["a"]}'
        return "Small daily savings compound into massive future freedom! ✨"
    except Exception:
        return "Small daily savings compound into massive future freedom! ✨"

# --- THE FINORA MINIMALIST AESTHETIC THEME ---
st.set_page_config(page_title="Finora", page_icon="🟢", layout="wide")

st.markdown("""
    <style>
    /* Reset & Deep Clean Layout Base */
    [data-testid="stHeader"] {background: transparent; height: 0rem;}
    div.block-container {padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; padding-left: 2.5rem !important; padding-right: 2.5rem !important;}
    
    /* Modern Editorial Typography System */
    p, span, label, .stMarkdown {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 14.5px !important; 
        color: #3f3f46;
    }
    .main-header {
        font-size: 36px !important;
        font-weight: 800 !important;
        letter-spacing: -1.2px;
        color: #09090b;
        margin-bottom: 2px !important;
    }
    .section-header {
        font-size: 24px !important;
        font-weight: 700 !important;
        letter-spacing: -0.6px;
        color: #09090b;
        margin-top: 4px !important;
        margin-bottom: 12px !important;
    }
    
    /* Elegant Canvas Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e4e4e7;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 14px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        border-color: #d4d4d8;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
    }
    .stLessonCard {
        background: #ffffff;
        border-radius: 12px;
        padding: 28px;
        border: 1px solid #e4e4e7;
        margin-bottom: 14px;
    }
    .ledger-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 16px;
        background: #f4f4f5;
        border-radius: 8px;
        margin-bottom: 6px;
    }
    
    /* Sleek Sidebar Navigation Array */
    div.stButton > button:first-child {
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100%;
        border: 1px solid transparent;
        background-color: transparent;
        padding: 10px 14px;
        font-size: 14px;
        font-weight: 500;
        border-radius: 8px;
        margin-bottom: 4px;
        color: #71717a;
    }
    div.stButton > button:first-child:hover {
        border-color: #e4e4e7;
        color: #09090b;
        background-color: #f4f4f5;
    }
    div.stButton > button:first-child:focus {
        border-color: #e4e4e7 !important;
        background-color: #f4f4f5 !important;
        color: #09090b !important;
    }
    
    /* Form & Tab Inputs Clean Controls */
    div[data-testid="stForm"] {
        border: 1px solid #e4e4e7 !important;
        background: #ffffff !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: none !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        padding-top: 0px;
        padding-bottom: 0px;
        border-radius: 6px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# --- SECURITY ENGINE ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def fetch_user_profile(username):
    try:
        res = supabase.table("profiles").select("*").eq("username", username.strip().lower()).execute()
        return res.data[0] if res.data else None
    except APIError as e:
        st.error(f"Database Error: {e.message}")
        return None

# --- STATE MANAGEMENT ---
if "username" not in st.session_state:
    st.session_state.username = None
if "nav_selection" not in st.session_state:
    st.session_state.nav_selection = "📊 Dashboard"
if "course_idx" not in st.session_state:
    st.session_state.course_idx = 0
if "page_idx" not in st.session_state:
    st.session_state.page_idx = 1

# --- LOGIN SCREEN ---
def login_page():
    st.markdown("<div style='text-align: center; margin-top: 40px; margin-bottom: 8px;'><span class='main-header'>Finora</span></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #71717a; font-size:15px; margin-top: -8px; margin-bottom: 32px;'>Intuitive capital mechanics, budget layers, and micro-insights for students.</p>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1.5, 1.2, 1.5])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Account Entry", "📝 Create Access"])
        with tab1:
            with st.form("login_form"):
                user_input = st.text_input("Username", placeholder="rahul_123").strip().lower()
                pass_input = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Access Desk", use_container_width=True):
                    profile = fetch_user_profile(user_input)
                    if profile and profile['password_hash'] == hash_password(pass_input):
                        st.session_state.username = user_input
                        st.rerun()
                    else:
                        st.error("Invalid credentials profile allocation.")
        with tab2:
            with st.form("reg_form"):
                new_user = st.text_input("Preferred Username").strip().lower()
                new_pass = st.text_input("Secure Password", type="password")
                occ = st.selectbox("Current Path Focus", ["College Student", "Freelancer", "School Student", "Self-Employed / Founder"])
                if st.form_submit_button("Generate Account Profile", use_container_width=True):
                    if new_user and new_pass:
                        try:
                            supabase.table("profiles").insert({
                                "username": new_user, "password_hash": hash_password(new_pass),
                                "age": 19, "occupation": occ, "points": 0
                            }).execute()
                            st.success("Profile created! Please proceed to the authentication log.")
                        except APIError: st.error("Identifier configuration already registered.")

# --- WORKSPACE PANELS ---

def show_finance_desk(profile, username):
    st.markdown("<p class='section-header'>📊 Financial Overview</p>", unsafe_allow_html=True)
    left_panel, right_panel = st.columns([1.6, 1.4])
    
    res = supabase.table("expenses").select("*").eq("username", username).execute()
    total_spent = sum([float(i['amount']) for i in res.data]) if res.data else 0.0
    budget_max = 25000.0

    with left_panel:
        standing = profile['occupation'] if profile else "Student"
        points = profile['points'] if profile else 0
        level = "Beginner Saver" if points < 150 else "Smart Investor" if points < 400 else "Money Master"

        st.markdown(f"""
        <div class="metric-card" style="border-top: 2px solid #18181b;">
            <span style="font-size:11px; color:#71717a; font-weight:700; letter-spacing:0.5px; text-transform: uppercase;">Profile Matrix</span><br/>
            <table style="width:100%; border:none; margin-top:8px; line-height: 1.6;">
                <tr><td style="padding:4px 0; font-size:14px; color:#71717a;">Focus Vector:</td><td style="padding:4px 0; font-size:14px; font-weight:600; text-align:right; color:#09090b;">{standing}</td></tr>
                <tr><td style="padding:4px 0; font-size:14px; color:#71717a;">Academic Weight:</td><td style="padding:4px 0; font-size:14px; font-weight:600; text-align:right; color:#09090b;">🏅 {points} XP</td></tr>
                <tr><td style="padding:4px 0; font-size:14px; color:#71717a;">Finora Tier:</td><td style="padding:4px 0; font-size:14px; font-weight:600; text-align:right; color:#10b981;">{level}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        rem_pct = max(((budget_max - total_spent) / budget_max) * 100, 0.0)
        health_color = "#10b981" if rem_pct > 40 else "#f59e0b" if rem_pct > 15 else "#ef4444"
        health_label = "Capital structures optimal." if rem_pct > 40 else "Velocity requires stabilization metrics." if rem_pct > 15 else "Critical threshold depletion."
        
        st.markdown(f"""
        <div class="metric-card" style="border-left: 3px solid {health_color};">
            <span style="font-size:11px; color:#71717a; font-weight:700; letter-spacing:0.5px; text-transform: uppercase;">Capital Variance Index</span><br/>
            <span style="font-size:15px; color:#09090b; display:inline-block; margin-top:4px;">Available Safety Allocation Reserve: <b>{rem_pct:.1f}%</b></span><br/>
            <span style="font-size:13px; color:{health_color}; font-weight:600; display:inline-block; margin-top:2px;">Insight: {health_label}</span>
        </div>
        """, unsafe_allow_html=True)

        rates = get_live_exchange_rates()
        if rates:
            usd_val = rates.get("USD", 0.012)
            gbp_val = rates.get("GBP", 0.009)
            st.markdown(f"""
            <div class="metric-card" style="background-color: #fafafa; border: 1px solid #e4e4e7;">
                <span style="font-size:11px; color:#71717a; font-weight:700; letter-spacing:0.5px; text-transform: uppercase;">Cross-Border Parity Convertor</span><br/>
                <span style="font-size:14px; color:#3f3f46; display:inline-block; margin-top:4px;">Baseline safety limit equals approximately <b>${25000 * usd_val:,.2f} USD</b> or <b>£{25000 * gbp_val:,.2f} GBP</b>.</span>
            </div>
            """, unsafe_allow_html=True)

        daily_allowance = max((budget_max - total_spent) / 30, 0.0)
        st.markdown(f"""
        <div class="metric-card" style="background-color: #fafafa; border: 1px solid #e4e4e7;">
            <span style="font-size:11px; color:#71717a; font-weight:700; letter-spacing:0.5px; text-transform: uppercase;">Diurnal Burn Allowance</span><br/>
            <span style="font-size:14px; color:#09090b; display:inline-block; margin-top:4px;">Target velocity ceiling: <b>₹{daily_allowance:,.2f} per diem</b> to maintain baseline horizons.</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size: 15px; font-weight: 700; color:#09090b; margin-bottom:6px; margin-top:16px;'>⚡ Instant Ledger Entry</p>", unsafe_allow_html=True)
        with st.form("quick_log_form", clear_on_submit=True):
            q_col1, q_col2, q_col3 = st.columns([1.5, 1.1, 1.1])
            with q_col1: q_cat = st.selectbox("Allocation Category", ["Food & Dining", "Education & Books", "Rent & Bills", "Entertainment & Leisure", "Mutual Funds & Investments"], key="q_cat")
            with q_col2: q_amt = st.number_input("Value (₹)", min_value=1.0, value=100.0, step=10.0, key="q_amt")
            with q_col3: 
                st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                q_sub = st.form_submit_button("Record Velocity", use_container_width=True)
            if q_sub:
                supabase.table("expenses").insert({"username": username, "category": q_cat, "amount": q_amt}).execute()
                st.toast("Entry logged to secure cloud matrix.", icon="✅")
                st.rerun()

    with right_panel:
        st.markdown("<p style='font-size: 15px; font-weight: 700; color:#09090b; margin-bottom:8px;'>📊 Distribution Vector</p>", unsafe_allow_html=True)
        if res.data:
            df = pd.DataFrame(res.data)
            df['amount'] = df['amount'].astype(float)
            fig = px.pie(df, values='amount', names='category', hole=0.70, color_discrete_sequence=px.colors.qualitative.Muted)
            fig.update_layout(height=260, margin=dict(t=10, b=10, l=10, r=10), showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div style='height:240px; display:flex; align-items:center; justify-content:center; background:#fafafa; border: 1px dashed #e4e4e7; border-radius:12px; color:#a1a1aa; font-size:13.5px; text-align:center; padding:24px;'>Distribution rendering requires baseline historical data input.</div>", unsafe_allow_html=True)

def show_micro_courses(profile, username):
    courses = [
        "Course 1: The Magic of Compounding",
        "Course 2: Simple Budgeting Rules (50/30/20)",
        "Course 3: How Credit Scores Work",
        "Course 4: Index Funds & Passive Investing",
        "Course 5: Mutual Funds & Monthly Savings Plans (SIP)",
        "Course 6: Demystifying Health & Life Insurance",
        "Course 7: Crypto, Blockchain & Digital Assets",
        "Course 8: Avoiding the Credit Card Debt Trap"
    ]
    
    h_col1, h_col2 = st.columns([2.0, 2.0])
    with h_col1: st.markdown("<p class='section-header'>📚 Micro-Insights Lab</p>", unsafe_allow_html=True)
    with h_col2:
        sel_course = st.selectbox("Topic Selector", courses, index=st.session_state.course_idx, label_visibility="collapsed")
        new_course_idx = courses.index(sel_course)
        if new_course_idx != st.session_state.course_idx:
            st.session_state.course_idx = new_course_idx
            st.session_state.page_idx = 1
            st.rerun()

    current_points = profile['points'] if profile else 0
    c_idx = st.session_state.course_idx
    p_idx = st.session_state.page_idx

    total_steps = 32
    current_step = (c_idx * 4) + p_idx
    st.progress(current_step / total_steps, text=f"Academic Track Completion: {int((current_step/total_steps)*100)}%")
    
    st.markdown(f"<div class='stLessonCard'><span style='color:#a1a1aa; font-weight:700; font-size:11px; letter-spacing:0.5px;'>LAB ANALYSIS • ARCHIVE {p_idx} / 4</span>", unsafe_allow_html=True)

    if c_idx == 0:
        if p_idx == 1:
            st.markdown("### Exponential Growth Mechanics")
            st.write("Compounding operates as an iterative feedback loop where interest distributions generate trailing yields alongside original underlying capital.")
            st.write("**Real World Translation:** Early capital locks yield margins that quietly multiply over multi-decade runways, lowering late-stage resource generation demand significantly.")
        elif p_idx == 2:
            st.markdown("### Horizon Estimation: Rule of 72")
            st.write("To rapidly determine capital baseline doubling horizons without executing complex log operations, divide 72 by the net performance yield.")
            st.latex(r"Years\ to\ Double\ Your\ Money = \frac{72}{Yearly\ Growth\ Rate}")
            st.write("**Yield Matrices:**\n* A steady 6% yield baseline doubles in 12 fiscal cycles ($72 / 6 = 12$).\n* Market-optimized 12% models double allocations within 6 intervals ($72 / 12 = 6$).")
        elif p_idx == 3:
            st.markdown("### The Structural Equations")
            st.write("The underlying mathematical algorithm powering modern asset velocity expansion is formalized below:")
            st.latex(r"A = P\left(1 + \frac{r}{n}\right)^{nt}")
            st.write("**Variable Manifest:**\n* **A**: Terminating gross capital yield balance.\n* **P**: Base input principal injection.\n* **r**: Nominal baseline distribution percentage.\n* **t**: Total structural layout runway duration.")
        elif p_idx == 4:
            st.markdown("### 🎯 Verification Audit")
            ans = st.radio("If you save ₹1,000 at a 10% interest rate that builds on itself every year, how much total money do you have after 2 years?", ["₹1,200.00", "₹1,210.00", "₹1,100.00"])
            if st.button("Submit Assessment Data"):
                if ans == "₹1,210.00": st.success("Verification confirmed. +25 Finora XP added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()
                else: st.error("Variance error detected. Review feedback parameters and resubmit.")

    else:
        if p_idx < 4:
            st.markdown(f"### {courses[c_idx]} (Module {p_idx})")
            st.write("Finora conceptual nodes detail practical asset habits systematically. Harness structural clarity to safely isolate capital structures, suppress liability exposure, and generate defensive reserves.")
        else:
            st.markdown("### 🎯 Comprehensive Phase Assessment")
            ans = st.radio("What is the best everyday framework to build reliable personal wealth?", ["Keep all extra money sitting in a zero-interest wallet", "Pay off expensive debt, keep a small cash safety cushion, and invest monthly in simple index funds", "Day-trade random digital coins with borrowed money"])
            if st.button("Submit Assessment Data"):
                if "Pay off expensive debt" in ans: st.success("Assessment criteria optimized. +25 Finora XP logged to database profile."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    nav_col1, _, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if p_idx > 1:
            if st.button("⏮️ Return Step", use_container_width=True): st.session_state.page_idx -= 1; st.rerun()
    with nav_col3:
        if p_idx < 4:
            if st.button("Advance Node ⏭️", use_container_width=True): st.session_state.page_idx += 1; st.rerun()

def show_budgeting(username):
    st.markdown("<p class='section-header'>📉 Envelope Budgets & Expense Matrices</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        with st.form("exp_form", clear_on_submit=True):
            st.markdown("<p style='font-size:14px; font-weight:700; margin:0; color:#09090b;'>Log Allocation Outflow</p>", unsafe_allow_html=True)
            cat = st.selectbox("Structural Allocation Bucket", ["Food & Dining", "Education & Books", "Rent & Bills", "Entertainment & Leisure", "Mutual Funds & Investments"])
            amt = st.number_input("Value Transferred (₹)", min_value=1.0, value=500.0, step=50.0)
            if st.form_submit_button("Commit Outflow Entry", use_container_width=True):
                supabase.table("expenses").insert({"username": username, "category": cat, "amount": amt}).execute()
                st.rerun()
                
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        res_p = supabase.table("profiles").select("occupation").eq("username", username).execute()
        track = res_p.data[0]['occupation'] if res_p.data else "Student"
        months_needed = 6 if "Freelancer" in track or "Founder" in track else 4
        safety_total = 8000.0 * months_needed
        st.markdown(f"""
        <div class="metric-card" style="background:#fafafa; border: 1px solid #e4e4e7; margin-top:12px;">
            <span style="font-size:11px; color:#71717a; font-weight:700; letter-spacing:0.5px; text-transform: uppercase;">🛡️ Defensive Reserve Guardrail</span><br/>
            <span style="font-size:13.5px; color:#27272a; display:inline-block; margin-top:4px;">Profile matrix classification [<b>{track}</b>] requests a structural <b>{months_needed}-Month Emergency Foundation</b> scaled to <b>₹{safety_total:,.2f}</b> minimum liquidity reserves.</span>
        </div>
        """, unsafe_allow_html=True)
                
    with col2:
        res = supabase.table("expenses").select("*").eq("username", username).execute()
        total = sum([float(i['amount']) for i in res.data]) if res.data else 0.0
        
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 0px; border-left: 3px solid #27272a;">
            <span style="font-size:11px; color:#71717a; font-weight:700; letter-spacing:0.5px; text-transform: uppercase;">Outflow Tracker Core</span><br/>
            <span style="font-size:20px; font-weight:700; color:#09090b; display:inline-block; margin-top:4px;">₹{total:,.2f} Disbursed / ₹25,000 Velocity Cap</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(total/25000, 1.0))
        
        st.markdown("<p style='font-size:14px; font-weight:700; color:#09090b; margin-bottom:6px; margin-top:16px;'>📜 Historical Ledger Stream</p>", unsafe_allow_html=True)
        if res.data:
            for item in res.data[-4:]:
                st.markdown(f"""
                <div class="ledger-row">
                    <span style="font-weight:500; color:#27272a;">{item['category']}</span>
                    <span style="font-weight:600; color:#09090b;">- ₹{float(item['amount']):,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:13px; color:#a1a1aa; font-style:italic;'>No data elements stream logged currently.</p>", unsafe_allow_html=True)

def show_savings():
    st.markdown("<p class='section-header'>🟢 Capital Multiplier & Milestone Engine</p>", unsafe_allow_html=True)
    st.write("Finora reframes asset conservation away from restriction models into future freedom procurement paradigms. Monitor behavioral scaling thresholds below.")

    st.markdown("<p style='font-size: 15px; font-weight: 700; color:#09090b; margin-bottom:8px;'>⚙️ Step 1: Initialize Baseline Parameters</p>", unsafe_allow_html=True)
    
    in_col1, in_col2, in_col3 = st.columns([1, 1, 1])
    with in_col1:
        starting_cash = st.number_input("Liquid Capital Starting Point (₹)", min_value=0, value=5000, step=1000)
    with in_col2:
        monthly_stash = st.number_input("Recurrent Monthly Injection Capacity (₹)", min_value=0, value=1500, step=250)
    with in_col3:
        years_horizon = st.slider("Target Allocation Runways (Years)", min_value=1, max_value=10, value=3)

    months_total = years_horizon * 12
    rate_savings, rate_fd, rate_index, rate_inflation = 0.035, 0.071, 0.120, 0.060
    
    final_savings = starting_cash * ((1 + rate_savings/12) ** months_total) + sum([monthly_stash * ((1 + rate_savings/12) ** (months_total - i)) for i in range(1, months_total + 1)])
    final_fd = starting_cash * ((1 + rate_fd/12) ** months_total) + sum([monthly_stash * ((1 + rate_fd/12) ** (months_total - i)) for i in range(1, months_total + 1)])
    final_index = starting_cash * ((1 + rate_index/12) ** months_total) + sum([monthly_stash * ((1 + rate_index/12) ** (months_total - i)) for i in range(1, months_total + 1)])
    
    out_of_pocket = starting_cash + (monthly_stash * months_total)
    lost_buying_power = out_of_pocket - (out_of_pocket / ((1 + rate_inflation) ** years_horizon))

    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 15px; font-weight: 700; color:#09090b; margin-bottom:4px;'>🔮 Step 2: Compare Trajectory Models</p>", unsafe_allow_html=True)
    st.caption(f"Gross unadjusted capital principal outlay: ₹{out_of_pocket:,.2f}")
    
    card1, card2, card3 = st.columns([1, 1, 1])
    
    with card1:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 2px solid #71717a; height: 100%;">
            <span style="font-size:11px; color:#71717a; font-weight:700; letter-spacing:0.5px; text-transform: uppercase;">Standard Liquidity Account</span><br/>
            <span style="font-size:22px; font-weight:700; color:#27272a; display:inline-block; margin-top:4px;">₹{final_savings:,.2f}</span><br/>
            <span style="font-size:12.5px; color:#71717a;">Yield baseline (~3.5%). Structurally stable but exhibits structural purchase parity degradation over time.</span>
        </div>
        """, unsafe_allow_html=True)
        
    with card2:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 2px solid #27272a; height: 100%;">
            <span style="font-size:11px; color:#27272a; font-weight:700; letter-spacing:0.5px; text-transform: uppercase;">Guaranteed Yield Contract</span><br/>
            <span style="font-size:22px; font-weight:700; color:#09090b; display:inline-block; margin-top:4px;">₹{final_fd:,.2f}</span><br/>
            <span style="font-size:12.5px; color:#52525b;">Fixed baseline protections (~7.1%). Immunizes capital assets safely against normal cyclical index shifts.</span>
        </div>
        """, unsafe_allow_html=True)
        
    with card3:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 2px solid #10b981; height: 100%;">
            <span style="font-size:11px; color:#10b981; font-weight:700; letter-spacing:0.5px; text-transform: uppercase;">Diversified Index Proxy</span><br/>
            <span style="font-size:22px; font-weight:700; color:#0f766e; display:inline-block; margin-top:4px;">₹{final_index:,.2f}</span><br/>
            <span style="font-size:12.5px; color:#115e59;">Equity core tracker (~12% historical baseline). Ideal target path for aggressive asset volume generation.</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background-color: #fafafa; color: #71717a; padding: 12px 16px; border-radius: 8px; border: 1px solid #e4e4e7; margin-top: 14px; font-size: 13.5px;">
        ⚠️ <b>Parity Warning Metric:</b> Maintaining raw zero-yield cash positioning exposes assets to an estimated 6% standard inflationary burn, reducing raw acquisition scale capacity by <b>₹{lost_buying_power:,.2f}</b> relative to current horizons.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    
    layout_col, crypto_col = st.columns([2.1, 0.9])
    
    with layout_col:
        st.markdown("<p style='font-size: 15px; font-weight: 700; color:#09090b; margin-bottom:4px;'>☕ Step 3: Habit Substitution Mechanics</p>", unsafe_allow_html=True)
        st.write("Swapping marginal micro-transactions for stable portfolio investments over 5-year tracking phases yields significant structural results:")
        
        habit1, habit2, habit3 = st.columns([1, 1, 1])
        with habit1:
            stash_tea = sum([(40 * 30) * ((1 + rate_index/12) ** (60 - i)) for i in range(1, 61)])
            st.markdown(f"""
            <div class="metric-card" style="background-color: #fafafa; height:100%; padding:16px;">
                <span style="font-size:11px; font-weight:700; color:#71717a; text-transform: uppercase;">☕ Micro Beverage Delta</span><br/>
                <span style="font-size:18px; font-weight:700; color:#09090b; display:inline-block; margin-top:4px;">₹{stash_tea:,.2f}</span><br/>
                <span style="font-size:12.5px; color:#71717a;">Redirecting <b>₹40/day</b> structural capital allocations toward market trackers.</span>
            </div>
            """, unsafe_allow_html=True)
        with habit2:
            stash_food = sum([(160 * 30) * ((1 + rate_index/12) ** (60 - i)) for i in range(1, 61)])
            st.markdown(f"""
            <div class="metric-card" style="background-color: #fafafa; height:100%; padding:16px;">
                <span style="font-size:11px; font-weight:700; color:#71717a; text-transform: uppercase;">🍔 Delivery Application Bypass</span><br/>
                <span style="font-size:18px; font-weight:700; color:#09090b; display:inline-block; margin-top:4px;">₹{stash_food:,.2f}</span><br/>
                <span style="font-size:12.5px; color:#71717a;">Consolidating nutrition logistics to log savings of <b>₹160/day</b>.</span>
            </div>
            """, unsafe_allow_html=True)
        with habit3:
            stash_sub = sum([(350 * 30) * ((1 + rate_index/12) ** (60 - i)) for i in range(1, 61)])
            st.markdown(f"""
            <div class="metric-card" style="background-color: #fafafa; height:100%; padding:16px;">
                <span style="font-size:11px; font-weight:700; color:#71717a; text-transform: uppercase;">👟 Impulse Intercept Filter</span><br/>
                <span style="font-size:18px; font-weight:700; color:#09090b; display:inline-block; margin-top:4px;">₹{stash_sub:,.2f}</span><br/>
                <span style="font-size:12.5px; color:#71717a;">Imposing 24-hour verification cooling protocols on tech/retail spending (Saves <b>₹350/day</b>).</span>
            </div>
            """, unsafe_allow_html=True)
            
    with crypto_col:
        st.markdown("<p style='font-size:15px; font-weight:700; color:#09090b; margin-bottom:4px;'>⚡ Global Asset Feeds</p>", unsafe_allow_html=True)
        crypto = get_crypto_prices()
        if crypto:
            btc_inr = crypto.get("bitcoin", {}).get("inr", 0)
            eth_inr = crypto.get("ethereum", {}).get("inr", 0)
            st.markdown(f"""
            <div class="metric-card" style="padding: 12px; margin-bottom:8px;">
                <span style="font-size:10px; color:#71717a; font-weight:bold; letter-spacing:0.5px;">BTC / INR</span><br/>
                <span style="font-size:14px; font-weight:600; color:#27272a;">₹{btc_inr:,.2f}</span>
            </div>
            <div class="metric-card" style="padding: 12px; margin-bottom:8px;">
                <span style="font-size:10px; color:#71717a; font-weight:bold; letter-spacing:0.5px;">ETH / INR</span><br/>
                <span style="font-size:14px; font-weight:600; color:#27272a;">₹{eth_inr:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.caption("Feeds isolated or down.")

    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 15px; font-weight: 700; color:#09090b; margin-bottom:4px;'>🎯 Step 4: Reverse Horizon Architecture</p>", unsafe_allow_html=True)
    
    plan_left, plan_right = st.columns([1.2, 1.8])
    with plan_left:
        with st.form("dynamic_goal_engine"):
            st.markdown("<p style='font-size:13px; font-weight:700; margin:0 0 6px 0; color:#71717a; text-transform:uppercase;'>Milestone Target Coordinates</p>", unsafe_allow_html=True)
            milestone_label = st.text_input("Target Objective Label", value="Developer Workstation Upgrade")
            milestone_target = st.number_input("Target Required Liquidity (₹)", min_value=2000, value=75000, step=5000)
            monthly_capacity = st.number_input("Sustainable Monthly Allocation Speed (₹)", min_value=250, value=3500, step=250)
            st.form_submit_button("Map Target Timeline")
            
    with plan_right:
        if monthly_capacity > 0:
            total_months_needed = int(milestone_target / monthly_capacity) if milestone_target > monthly_capacity else 1
            years_part = total_months_needed // 12
            months_part = total_months_needed % 12
            
            duration_readout = f"{years_part} Year{'s' if years_part > 1 else ''} " if years_part > 0 else ""
            if months_part > 0 or years_part == 0:
                duration_readout += f"{months_part} Month{'s' if months_part != 1 else ''}"
                
            st.markdown(f"""
            <div class="metric-card" style="background-color: #ffffff; border-left: 3px solid #09090b; padding: 24px; height: 100%;">
                <span style="font-size:11px; color:#71717a; font-weight:700; letter-spacing:0.5px; text-transform: uppercase;">Calculated Horizon Matrix: {milestone_label.upper()}</span><br/>
                <span style="font-size:30px; font-weight:800; color:#09090b; line-height:1.2; display:inline-block; margin-top:4px;">{duration_readout}</span><br/>
                <p style="font-size:14px; color:#3f3f46; margin-top:8px; line-height:1.5;">
                    Maintaining an unyielding allocation structure of <b>₹{monthly_capacity:,.2f} per month</b> achieves the necessary <b>₹{milestone_target:,.2f}</b> baseline in exactly <b>{total_months_needed} months</b>.
                </p>
                <div style="font-size:12px; color:#27272a; font-weight:600; background-color:#f4f4f5; padding:8px 12px; border-radius:6px; display:inline-block; margin-top:2px;">
                    ⚡ Automation Directive: Configure auto-sweeps on receipt cycles to strip behavior barriers from target goals.
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_splitting():
    st.markdown("<p class='section-header'>👥 Liability Fragmentation & Payment Gateways</p>", unsafe_allow_html=True)
    st.write("Distribute collective expense parameters accurately across profile networks while generating payment pathways.")
    
    col1, col2 = st.columns([1.4, 1.6])
    with col1:
        bill = st.number_input("Gross Shared Cost Package (₹)", value=1500.0, step=100.0)
        people = st.slider("Network Participant Nodes", 2, 12, 3)
        vpa = st.text_input("Target UPI VPA Handle Identifier (Optional)", placeholder="identifier@upi").strip()
    with col2:
        per_person = round(bill/people, 2) if people > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:22px 18px; border-left: 3px solid #10b981; background: #ffffff; margin-top:10px;">
            <span style="font-size:12px; color:#71717a; font-weight:600; letter-spacing:0.5px; text-transform: uppercase;">Per-Node Liabilities</span><br/>
            <span style="font-size:36px; font-weight:800; color:#09090b; line-height:1.2; display:inline-block; margin-top:4px;">₹{per_person:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if vpa:
            st.markdown("<span style='font-size:12px; color:#71717a; font-weight:700; text-transform: uppercase;'>Deep Link String Engine Output:</span>", unsafe_allow_html=True)
            upi_link = f"upi://pay?pa={vpa}&pn=FinoraSplit&am={per_person}&cu=INR"
            st.code(upi_link, language="markdown")
            
            message_text = f"Finora Notification: Fragmented liability calculation processed. Your shared obligation footprint is ₹{per_person:,.2f}. Instant transfer route link: {upi_link}"
            encoded_message = message_text.replace(" ", "%20")
            whatsapp_url = f"https://wa.me/?text={encoded_message}"
            
            st.markdown(f"""
            <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #09090b; color: white; text-align: center; padding: 12px; border-radius: 8px; font-weight: 600; font-size: 13.5px; margin-top: 12px; letter-spacing:0.3px;">
                    Transmit To Network via WhatsApp
                </div>
            </a>
            """, unsafe_allow_html=True)

# --- CORE APPLICATION MASTER SKELETON ---
if st.session_state.username is None:
    login_page()
else:
    profile = fetch_user_profile(st.session_state.username)
    
    with st.sidebar:
        st.markdown("<p class='main-header' style='font-size: 32px !important; margin-bottom:0px; margin-top: 10px;'>Finora</p>", unsafe_allow_html=True)
        st.caption(f"Profile: {st.session_state.username.lower()}")
        
        quote = get_daily_motivation()
        st.markdown(f"""
        <div style="background: #ffffff; padding: 14px; border-radius: 8px; border: 1px solid #e4e4e7; margin: 12px 0;">
            <p style="font-size: 12px !important; color: #71717a; margin:0; line-height:1.4;">{quote}</p>
        </div>
        """, unsafe_allow_html=True)
        
        user_points = profile['points'] if profile else 0
        st.markdown(f"🏅 Academic Mass: **{user_points} XP**")
        st.markdown("<hr style='margin: 12px 0; border-color:#e4e4e7;'/>", unsafe_allow_html=True)
        
        if st.sidebar.button("📊 Overview Control"): st.session_state.nav_selection = "📊 Dashboard"; st.rerun()
        if st.sidebar.button("📚 Insights Laboratory"): st.session_state.nav_selection = "📚 Micro-Courses"; st.rerun()
        if st.sidebar.button("📉 Outflow Ledger Matrix"): st.session_state.nav_selection = "📉 Expense Tracker"; st.rerun()
        if st.sidebar.button("🟢 Horizon Multiplier"): st.session_state.nav_selection = "🐷 Savings Calculator"; st.rerun()
        if st.sidebar.button("👥 Network Split Tools"): st.session_state.nav_selection = "👥 Split Bills"; st.rerun()
        
        st.markdown("<hr style='margin: 16px 0; border-color:#e4e4e7;'/>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Terminate Session Profile"):
            st.session_state.username = None
            st.session_state.nav_selection = "📊 Dashboard"
            st.rerun()

    # Layout Router Matrix
    if st.session_state.nav_selection == "📊 Dashboard": 
        show_finance_desk(profile, st.session_state.username)
    elif st.session_state.nav_selection == "📚 Micro-Courses": 
        show_micro_courses(profile, st.session_state.username)
    elif st.session_state.nav_selection == "📉 Expense Tracker": 
        show_budgeting(st.session_state.username)
    elif st.session_state.nav_selection == "🐷 Savings Calculator": 
        show_savings()
    elif st.session_state.nav_selection == "👥 Split Bills": 
        show_splitting()
