import streamlit as st
from supabase import create_client, Client
from postgrest.exceptions import APIError
import hashlib
import pandas as pd
import plotly.express as px

# --- SUPABASE SECURE CONFIGURATION ---
raw_url = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SUPABASE_URL = raw_url.split("/rest/v1")[0].strip("/")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- CONFIG & DENSE UI STYLING ENGINE ---
st.set_page_config(page_title="FinSmart Academy India", page_icon="💳", layout="wide")

st.markdown("""
    <style>
    /* Global Compact Layout Optimizations */
    .block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 98%;}
    div.block-container {padding-left: 2rem; padding-right: 2rem;}
    
    /* Sleek Dashboard Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 12px;
    }
    .stLessonCard {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 24px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.01), 0 2px 4px -1px rgba(0,0,0,0.01);
    }
    
    /* Compact Sidebar Link Styling */
    div.stButton > button:first-child {
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100%;
        border: 1px solid #e5e7eb;
        background-color: #ffffff;
        padding: 8px 14px;
        font-size: 14px;
        border-radius: 6px;
        margin-bottom: -4px;
    }
    div.stButton > button:first-child:hover {
        border-color: #4A90E2;
        color: #4A90E2;
        background-color: #f0f7ff;
    }
    
    /* Tighten native spacing elements */
    [data-testid="stVerticalBlock"] {gap: 0.75rem !important;}
    h1 {margin-top: -10px; padding-bottom: 5px;}
    h2, h3, h4 {margin-top: 5px; margin-bottom: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- ENGINE HELPERS ---
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
    st.session_state.nav_selection = "📊 Personal Finance Desk"
if "course_idx" not in st.session_state:
    st.session_state.course_idx = 0
if "page_idx" not in st.session_state:
    st.session_state.page_idx = 1

# --- AUTHENTICATION SCREEN ---
def login_page():
    st.markdown("<h2 style='text-align: center; color: #4A90E2;'>🎓 FinSmart Studio India</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-top:-10px; font-size:14px;'>Rupee-Localized Student Intelligence Hub</p>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1.2, 1.5, 1.2])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Secure Login", "📝 Register Portfolio"])
        with tab1:
            with st.form("login_form"):
                user_input = st.text_input("Username", placeholder="e.g. sharmaji_student").strip().lower()
                pass_input = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Launch Workspace", use_container_width=True):
                    profile = fetch_user_profile(user_input)
                    if profile and profile['password_hash'] == hash_password(pass_input):
                        st.session_state.username = user_input
                        st.rerun()
                    else:
                        st.error("Invalid verification credentials.")
        with tab2:
            with st.form("reg_form"):
                new_user = st.text_input("Choose Unique Username").strip().lower()
                new_pass = st.text_input("Choose Security Password", type="password")
                occ = st.selectbox("Track Matrix", ["Undergraduate", "Freelancer", "High School", "Founder"])
                if st.form_submit_button("Provision Ledger Account", use_container_width=True):
                    if new_user and new_pass:
                        try:
                            supabase.table("profiles").insert({
                                "username": new_user, "password_hash": hash_password(new_pass),
                                "age": 19, "occupation": occ, "points": 0
                            }).execute()
                            st.success("Account initialized successfully!")
                        except APIError: st.error("Identity string allocation conflict.")

# --- CORE INTEGRATED APPLICATION PANELS ---

def show_finance_desk(profile, username):
    left_panel, right_panel = st.columns([1.8, 1.2])
    
    with left_panel:
        st.markdown("### 📊 Personal Balance Sheet Control Center")
        st.caption("Central dashboard for running metrics, rupee asset profiles, and system rankings.")
        
        standing = profile['occupation'] if profile else "Student"
        points = profile['points'] if profile else 0
        level = "Bronze Tier Asset Controller" if points < 150 else "Silver Tier Wealth Builder" if points < 400 else "Elite Financial Master"

        # Dense Layout Info Display Box
        st.markdown(f"""
        <div class="metric-card">
            <table style="width:100%; border:none; margin:0;">
                <tr>
                    <td style="padding:4px; font-size:14px; color:#6b7280;">Profile Track:</td>
                    <td style="padding:4px; font-size:14px; font-weight:600; text-align:right;">{standing}</td>
                </tr>
                <tr>
                    <td style="padding:4px; font-size:14px; color:#6b7280;">Earned Academy Milestones:</td>
                    <td style="padding:4px; font-size:14px; font-weight:600; text-align:right; color:#4A90E2;">🏅 {points} XP</td>
                </tr>
                <tr>
                    <td style="padding:4px; font-size:14px; color:#6b7280;">System Standing Rank:</td>
                    <td style="padding:4px; font-size:14px; font-weight:600; text-align:right; color:#10b981;">{level}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Transaction Injection
        st.markdown("##### ⚡ Quick Transaction Injection")
        with st.form("quick_log_form", clear_on_submit=True):
            q_col1, q_col2, q_col3 = st.columns([1.5, 1, 1])
            with q_col1: q_cat = st.selectbox("Stream Type", ["Food", "Academic", "Housing", "Leisure", "Investment"], key="q_cat")
            with q_col2: q_amt = st.number_input("Value (₹)", min_value=1.0, value=100.0, step=10.0, key="q_amt")
            with q_col3: q_sub = st.form_submit_button("Post Outlay", use_container_width=True)
            if q_sub:
                supabase.table("expenses").insert({"username": username, "category": q_cat, "amount": q_amt}).execute()
                st.toast("Transaction appended cleanly!", icon="⚡")
                st.rerun()

    with right_panel:
        res = supabase.table("expenses").select("*").eq("username", username).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['amount'] = df['amount'].astype(float)
            fig = px.pie(df, values='amount', names='category', hole=0.6, color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(height=180, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div style='height:160px; display:flex; align-items:center; justify-content:center; background:#f3f4f6; border-radius:10px; color:gray; font-size:13px;'>No logged expenses discovered.</div>", unsafe_allow_html=True)

def show_micro_courses(profile, username):
    courses = [
        "Course 1: The Velocity of Compounding",
        "Course 2: Tactical Capital Allocation (50/30/20)",
        "Course 3: Credit Architecture & Trust",
        "Course 4: Index Funds & Passive Capture",
        "Course 5: The Liquidity Safety Buffer",
        "Course 6: Taxes for Freelancers & Operators",
        "Course 7: Inflation Dynamics & Asset Erosion",
        "Course 8: High vs. Low Cost Debt Leverage"
    ]
    
    h_col1, h_col2 = st.columns([1.5, 2.5])
    with h_col1: st.markdown("### 📚 Foundational Learning Desk")
    with h_col2:
        sel_course = st.selectbox("Jump to Curriculum Module", courses, index=st.session_state.course_idx, label_visibility="collapsed")
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
    st.progress(current_step / total_steps, text=f"Curriculum Runway Progress: {int((current_step/total_steps)*100)}% Complete (Step {current_step}/{total_steps})")
    
    st.markdown(f"<div class='stLessonCard'><span style='color:#4A90E2; font-weight:600; font-size:12px;'>PAGE {p_idx} OF 4</span>", unsafe_allow_html=True)

    if c_idx == 0:
        if p_idx == 1:
            st.markdown("#### Course 1: The Mathematics of Compound Returns")
            st.write("Compounding operates as calculation architecture where your yields generate additional subsequent returns over time. Unlike simple interest, which only pays out returns on your original seed capital, compounding continually layers interest onto your historical gains.")
        elif p_idx == 2:
            st.markdown("#### Course 1: The Rule of 72 & The Cost of Waiting")
            st.write("To quickly calculate the velocity of compounding, professionals utilize the Rule of 72. By dividing 72 by your expected annual rate of return, you arrive at the exact number of years required to double your principal balance without adding another rupee.")
            st.latex(r"Years\ to\ Double = \frac{72}{Annual\ Interest\ Rate}")
        elif p_idx == 3:
            st.markdown("#### Course 1: Setting Up the Equation Variables")
            st.write("The underlying mathematical expression driving this phenomenon relies on exponential variables, where time ($t$) acts as the exponent raising the entire rate equation:")
            st.latex(r"A = P\left(1 + \frac{r}{n}\right)^{nt}")
        elif p_idx == 4:
            st.markdown("#### 🎯 Course 1 Validation Assessment")
            ans = st.radio("If you deposit ₹1,000 compounding at an annual interest yield of 10%, what is the profile value tracking state at Year 2 conclusion?", ["₹1,200.00", "₹1,210.00", "₹1,100.00"])
            if st.button("Commit Evaluation Check"):
                if ans == "₹1,210.00": st.success("Correct! +25 XP Secured."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()
                else: st.error("Incorrect vector calculation parameters.")

    elif c_idx == 1:
        if p_idx == 1:
            st.markdown("#### Course 2: Balanced Budget Engineering Frameworks")
            st.write("Budget models collapse in real-world scenarios when they are built with rigid restrictions. Denying all discretionary personal gratification leads to psychological burnout, causing students to abandon fiscal tracking software entirely.")
        elif p_idx == 2:
            st.markdown("#### Course 2: Dissecting Needs vs. Wants Parameters")
            st.write("The framework splits your net income cleanly: 50% forms structural Needs (rent, core groceries, medicine), while 30% feeds flexible personal Wants (entertainment packages, luxury options).")
        elif p_idx == 3:
            st.markdown("#### Course 2: Financing the Forward Asset Layer")
            st.write("The final 20% of your capital configuration must be strictly ring-fenced for your financial future. This bucket coordinates index acquisitions, long-term market access allocations, and credit balance pay downs.")
        elif p_idx == 4:
            st.markdown("#### 🎯 Course 2 Validation Assessment")
            ans = st.radio("Under proper 50/30/20 budget criteria, where does a premium streaming television package settle into?", ["Fixed Structural Needs (50%)", "Discretionary Wants Allocation (30%)", "Financial Future Acceleration (20%)"])
            if st.button("Commit Evaluation Check"):
                if ans == "Discretionary Wants Allocation (30%)": st.success("Correct! +25 XP Secured."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    else:
        if p_idx < 4:
            st.markdown(f"#### {courses[c_idx]} (Section Module {p_idx})")
            st.write("Advanced academic reading content block detailing systematic asset distribution principles, compliance methodologies, and historical financial performance frameworks. Ensure comprehensive analysis before proceeding to the operational validation track.")
        else:
            st.markdown("#### 🎯 Integrated Track Assessment Unit")
            ans = st.radio("Identify the statement that correctly represents optimal asset protection procedures outlined inside the study text:", ["Leave all excess liquidity inside traditional systems checking fields", "Deploy strategic assets into well-diversified vehicles while removing toxic card debt matrices", "Speculate on un-hedged technology equities using short-term lines"])
            if st.button("Commit Evaluation Check"):
                if "Deploy strategic assets" in ans: st.success("Correct! +25 XP Secured."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    nav_col1, _, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if p_idx > 1:
            if st.button("⬅️ Previous Screen", use_container_width=True): st.session_state.page_idx -= 1; st.rerun()
    with nav_col3:
        if p_idx < 4:
            if st.button("Next Screen ➡️", use_container_width=True): st.session_state.page_idx += 1; st.rerun()

def show_budgeting(username):
    st.markdown("### 📉 High-Density Budget Tracker")
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        with st.form("exp_form", clear_on_submit=True):
            cat = st.selectbox("Category Grouping", ["Food", "Academic", "Housing", "Leisure", "Investment"])
            amt = st.number_input("Absolute Value (₹)", min_value=1.0, value=500.0, step=50.0)
            if st.form_submit_button("Log Entry Object", use_container_width=True):
                supabase.table("expenses").insert({"username": username, "category": cat, "amount": amt}).execute()
                st.rerun()
    with col2:
        res = supabase.table("expenses").select("amount").eq("username", username).execute()
        total = sum([float(i['amount']) for i in res.data])
        
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:12px; color:gray;">Current Target Envelope Capacity</span><br/>
            <span style="font-size:20px; font-weight:700; color:#4A90E2;">₹{total:.2f} / ₹25,000.00</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(total/25000, 1.0))

def show_savings():
    st.markdown("### 🐷 Savings & FD Yield Simulator")
    col1, col2 = st.columns([1.3, 1.7])
    with col1:
        principal = st.number_input("Principal Deployment Amount (₹)", min_value=1000, value=10000, step=1000)
        tenure = st.slider("Horizon Investment Term (Years)", 1, 10, 3)
    with col2:
        # FEATURE ADDITION: Dynamic Comparison Matrix (Savings vs Bank FD)
        sav_rate = 0.035
        fd_rate = 0.071
        
        sav_final = principal * ((1 + sav_rate) ** tenure)
        fd_final = principal * ((1 + fd_rate) ** tenure)
        arbitrage = fd_final - sav_final
        
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:11px; color:gray; font-weight:bold; text-transform:uppercase;">Indian Arbitrage Outlook</span>
            <hr style="margin:6px 0; border-color:#eee;"/>
            <div style="display:flex; justify-content:between; font-size:13px; margin:4px 0;">
                <span>Standard Bank Return (~3.5%):</span>
                <span style="margin-left:auto; font-weight:600;">₹{sav_final:.2f}</span>
            </div>
            <div style="display:flex; justify-content:between; font-size:13px; margin:4px 0; color:#10b981;">
                <span>Fixed Deposit Return (~7.1%):</span>
                <span style="margin-left:auto; font-weight:600;">₹{fd_final:.2f}</span>
            </div>
            <hr style="margin:6px 0; border-color:#eee;"/>
            <span style="font-size:11px; color:#4A90E2; font-weight:700;">💡 Strategy Alpha Opportunity: Lock in an extra ₹{arbitrage:.2f} yield over cash holding erosion.</span>
        </div>
        """, unsafe_allow_html=True)

def show_splitting():
    st.markdown("### 👥 Peer Shared Split Hub & UPI Integration")
    col1, col2 = st.columns([1.4, 1.6])
    with col1:
        bill = st.number_input("Total Shared Invoice Bill (₹)", value=1500.0, step=100.0)
        people = st.slider("Total Headcount Division Share", 2, 12, 3)
        vpa = st.text_input("Your UPI ID (VPA Address)", placeholder="username@upi").strip()
    with col2:
        per_person = round(bill/people, 2) if people > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:18px 16px; border-left: 6px solid #10b981; margin-bottom: 8px;">
            <span style="font-size:13px; color:gray;">EACH INDIVIDUAL OWES:</span><br/>
            <span style="font-size:32px; font-weight:800; color:#111827;">₹{per_person:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # FEATURE ADDITION: Instant Real-time deep-link string assembler
        if vpa:
            upi_deep_link = f"upi://pay?pa={vpa}&pn=FinSmartSplit&am={per_person}&cu=INR"
            st.code(upi_deep_link, language="markdown")
            st.caption("📱 Copy this link code directly to push instant settlement deep links over chat networks.")

# --- MASTER NAVIGATION CONTROLLER HUB ---
if st.session_state.username is None:
    login_page()
else:
    profile = fetch_user_profile(st.session_state.username)
    
    with st.sidebar:
        st.markdown("<h3 style='color:#4A90E2; margin-bottom:0;'>💳 FinSmart Core</h3>", unsafe_allow_html=True)
        st.caption(f"Active Operator: {st.session_state.username.upper()}")
        
        user_points = profile['points'] if profile else 0
        st.markdown(f"🥇 Balance Level Balance: **{user_points} XP**")
        st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
        
        st.markdown("<span style='font-size:11px; font-weight:700; color:gray;'>WORKSPACE MODULES</span>", unsafe_allow_html=True)
        
        if st.sidebar.button("📊 Personal Finance Desk"): st.session_state.nav_selection = "📊 Personal Finance Desk"; st.rerun()
        if st.sidebar.button("📚 Micro-Courses"): st.session_state.nav_selection = "📚 Micro-Courses"; st.rerun()
        if st.sidebar.button("📉 Budgeting Tracker"): st.session_state.nav_selection = "📉 Budgeting Tracker"; st.rerun()
        if st.sidebar.button("🐷 Savings Accelerator"): st.session_state.nav_selection = "🐷 Savings Accelerator"; st.rerun()
        if st.sidebar.button("👥 Friends Splitting Matrix"): st.session_state.nav_selection = "👥 Friends Splitting Matrix"; st.rerun()
        
        st.markdown("<hr style='margin: 12px 0;'/>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Terminate Session Workspace"):
            st.session_state.username = None
            st.session_state.nav_selection = "📊 Personal Finance Desk"
            st.rerun()

    # Route Core View Panel Windows via State Indicators
    if st.session_state.nav_selection == "📊 Personal Finance Desk": 
        show_finance_desk(profile, st.session_state.username)
    elif st.session_state.nav_selection == "📚 Micro-Courses": 
        show_micro_courses(profile, st.session_state.username)
    elif st.session_state.nav_selection == "📉 Budgeting Tracker": 
        show_budgeting(st.session_state.username)
    elif st.session_state.nav_selection == "🐷 Savings Accelerator": 
        show_savings()
    elif st.session_state.nav_selection == "👥 Friends Splitting Matrix": 
        show_splitting()
