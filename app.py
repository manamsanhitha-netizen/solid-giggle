import streamlit as st
from supabase import create_client, Client
from postgrest.exceptions import APIError
import hashlib
import pandas as pd
import plotly.express as px

# --- SUPABASE CONFIGURATION ---
raw_url = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
SUPABASE_URL = raw_url.split("/rest/v1")[0].strip("/")

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- THE FINORA MASTER THEME OVERHAUL ---
st.set_page_config(page_title="Finora | Next-Gen Student Wealth Hub", page_icon="💳", layout="wide")

st.markdown("""
    <style>
    /* Absolute Structural Clean-up to Prevent Header Clipping & Drop Blank Space */
    [data-testid="stHeader"] {background: transparent; height: 0rem;}
    div.block-container {padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important;}
    #root > div:nth-child(1) > div > div > div {padding-top: 0px !important;}
    
    /* Premium Slate & Emerald Scale Typography */
    p, span, label, .stMarkdown {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 15px !important; 
        line-height: 1.6 !important;
        color: #334155;
    }
    .main-header {
        font-size: 30px !important;
        font-weight: 800 !important;
        letter-spacing: -0.8px;
        background: linear-gradient(135deg, #10b981 0%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .section-header {
        font-size: 22px !important;
        font-weight: 700 !important;
        letter-spacing: -0.4px;
        color: #0f172a;
        margin-top: 2px !important;
        margin-bottom: 10px !important;
    }
    
    /* Re-Engineered Component Cards with Soft Gradients and Drop Shadows */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 22px;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.03), 0 2px 4px rgba(15, 23, 42, 0.02);
        margin-bottom: 14px;
    }
    .stLessonCard {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 14px;
        padding: 26px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.01);
        margin-bottom: 14px;
    }
    .ledger-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 12px;
        background: #f8fafc;
        border-radius: 6px;
        margin-bottom: 6px;
        border-left: 3px solid #cbd5e1;
    }
    
    /* Fully Polished Interactive Sidebar Control Array */
    div.stButton > button:first-child {
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100%;
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
        padding: 12px 16px;
        font-size: 14.5px;
        font-weight: 600;
        border-radius: 10px;
        margin-bottom: 5px;
        color: #475569;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div.stButton > button:first-child:hover {
        border-color: #10b981;
        color: #10b981;
        background: linear-gradient(90deg, #f0fdf4 0%, #ffffff 100%);
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.05);
        transform: translateX(2px);
    }
    
    /* Forms and Input Baseline Cleanups */
    [data-testid="stVerticalBlock"] {gap: 0.6rem !important;}
    .element-container {margin-bottom: 0rem !important;}
    div[data-testid="stForm"] {
        border: 1px solid #e2e8f0 !important;
        background: #ffffff !important;
        border-radius: 14px !important;
        padding: 18px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
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
    st.markdown("<div style='text-align: center; margin-bottom: 10px;'><span class='main-header'>✨ Finora Hub</span></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size:15px; margin-top: -12px; margin-bottom: 24px;'>Automated Budget Envelopes, Real-time Splitters & Gamified Wealth Architecture</p>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1.4, 1.2, 1.4])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Account Login", "📝 Create Finora Profile"])
        with tab1:
            with st.form("login_form"):
                user_input = st.text_input("Username Ident", placeholder="e.g. rahul_123").strip().lower()
                pass_input = st.text_input("Password Ident", type="password", placeholder="••••••••")
                if st.form_submit_button("Launch Dashboard Panel", use_container_width=True):
                    profile = fetch_user_profile(user_input)
                    if profile and profile['password_hash'] == hash_password(pass_input):
                        st.session_state.username = user_input
                        st.rerun()
                    else:
                        st.error("Incorrect username or security password pattern.")
        with tab2:
            with st.form("reg_form"):
                new_user = st.text_input("Choose Public Username").strip().lower()
                new_pass = st.text_input("Choose Master Password", type="password")
                occ = st.selectbox("Track Matrix Selection:", ["Undergraduate Student", "Freelancer Track", "High School Student", "Self-Employed Founder"])
                if st.form_submit_button("Deploy My Account Structure", use_container_width=True):
                    if new_user and new_pass:
                        try:
                            supabase.table("profiles").insert({
                                "username": new_user, "password_hash": hash_password(new_pass),
                                "age": 19, "occupation": occ, "points": 0
                            }).execute()
                            st.success("Finora pipeline initialized! Please switch tabs to login.")
                        except APIError: st.error("Username index registry collision.")

# --- WORKSPACE PANELS ---

def show_finance_desk(profile, username):
    st.markdown("<p class='section-header'>📊 Control Center Dashboard Analytics</p>", unsafe_allow_html=True)
    left_panel, right_panel = st.columns([1.6, 1.4])
    
    res = supabase.table("expenses").select("*").eq("username", username).execute()
    total_spent = sum([float(i['amount']) for i in res.data]) if res.data else 0.0
    budget_max = 25000.0

    with left_panel:
        standing = profile['occupation'] if profile else "Student"
        points = profile['points'] if profile else 0
        level = "Beginner Saver" if points < 150 else "Smart Investor" if points < 400 else "Money Master"

        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #10b981; background: linear-gradient(180deg, #ffffff 0%, #fdfdfd 100%);">
            <table style="width:100%; border:none; margin:0; line-height: 1.6;">
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b; font-weight:500;">Profile Track Model</td><td style="padding:4px; font-size:14.5px; font-weight:700; text-align:right; color:#0f172a;">{standing}</td></tr>
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b; font-weight:500;">Learning Progression</td><td style="padding:4px; font-size:14.5px; font-weight:700; text-align:right; color:#0284c7;">🏅 {points} XP Available</td></tr>
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b; font-weight:500;">Academy Standing Tier</td><td style="padding:4px; font-size:14.5px; font-weight:700; text-align:right; color:#10b981;">{level}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # FEATURE ADDITION: Dynamic Financial Health Radar Engine
        rem_pct = max(((budget_max - total_spent) / budget_max) * 100, 0.0)
        health_color = "#10b981" if rem_pct > 40 else "#f59e0b" if rem_pct > 15 else "#ef4444"
        health_label = "Optimal Status (Excellent)" if rem_pct > 40 else "Warning Profile (Caution)" if rem_pct > 15 else "Critical Violation (Danger)"
        
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid {health_color};">
            <span style="font-size:12px; color:#64748b; font-weight:700; letter-spacing:0.5px;">❤️ DYNAMIC FINANCIAL HEALTH RADAR</span><br/>
            <span style="font-size:15px; color:#1e293b;">Projected Safe Capital Buffer Rate: <b>{rem_pct:.1f}% Remaining</b></span><br/>
            <span style="font-size:13px; color:{health_color}; font-weight:700;">System Diagnostic: {health_label}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size: 16px; font-weight: 700; color:#1e293b; margin-bottom:4px;'>⚡ Instant Outflow Pipeline</p>", unsafe_allow_html=True)
        with st.form("quick_log_form", clear_on_submit=True):
            q_col1, q_col2, q_col3 = st.columns([1.5, 1.1, 1.1])
            with q_col1: q_cat = st.selectbox("Asset Class Bucket", ["Food & Dining", "Education & Books", "Rent & Bills", "Entertainment & Leisure", "Mutual Funds & SIPs"], key="q_cat")
            with q_col2: q_amt = st.number_input("Value Scale (₹)", min_value=1.0, value=100.0, step=10.0, key="q_amt")
            with q_col3: 
                st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                q_sub = st.form_submit_button("Log To Cloud Ledger", use_container_width=True)
            if q_sub:
                supabase.table("expenses").insert({"username": username, "category": q_cat, "amount": q_amt}).execute()
                st.toast("Expense synced successfully!", icon="✅")
                st.rerun()

    with right_panel:
        if res.data:
            df = pd.DataFrame(res.data)
            df['amount'] = df['amount'].astype(float)
            fig = px.pie(df, values='amount', names='category', hole=0.62, color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(height=250, margin=dict(t=15, b=15, l=15, r=15), showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div style='height:240px; display:flex; align-items:center; justify-content:center; background:#f8fafc; border: 1px dashed #cbd5e1; border-radius:14px; color:#64748b; font-size:14px; margin-top:4px;'>Allocation tracking metrics will automatically render visual graphs once an item is logged.</div>", unsafe_allow_html=True)

def show_micro_courses(profile, username):
    courses = [
        "Course 1: The Power of Compounding",
        "Course 2: Simple Budgeting Rules (50/30/20)",
        "Course 3: How Credit Scores Work",
        "Course 4: Index Funds & Passive Investing",
        "Course 5: Mutual Funds & SIP Mechanics",
        "Course 6: Demystifying Health & Life Insurance",
        "Course 7: Crypto, Blockchain & Digital Assets",
        "Course 8: Avoiding the Credit Card Debt Trap"
    ]
    
    h_col1, h_col2 = st.columns([1.8, 2.2])
    with h_col1: st.markdown("<p class='section-header'>📚 Interactive Gamified Academy Runway</p>", unsafe_allow_html=True)
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
    st.progress(current_step / total_steps, text=f"Academy Profile Tracking Matrix: {int((current_step/total_steps)*100)}% Complete (Module Page {current_step}/{total_steps})")
    
    st.markdown(f"<div class='stLessonCard'><span style='color:#10b981; font-weight:800; font-size:11.5px; letter-spacing:1px;'>CURRICULUM NODE • UNIT {p_idx} OF 4</span>", unsafe_allow_html=True)

    if c_idx == 0:
        if p_idx == 1:
            st.markdown("### The Structural Mechanics of Compounding")
            st.write("Compounding operates as a cumulative reward architecture where your yields earn independent yields. Reinvesting asset returns instead of liquidating them triggers an exponential wealth curve.")
        elif p_idx == 2:
            st.markdown("### Predictive Rule Models: The Framework of 72")
            st.write("Divide the standard baseline constant score of **72** by your expected constant annualized rate of return to reveal exactly how many years it takes your asset base to double.")
            st.latex(r"Years\ to\ Double = \frac{72}{Interest\ Rate}")
        elif p_idx == 3:
            st.markdown("### Exponential Mathematical Equations")
            st.write("The underlying algebraic projection engine utilized globally to run mathematical compound tracking arrays across retail markets:")
            st.latex(r"A = P\left(1 + \frac{r}{n}\right)^{nt}")
        elif p_idx == 4:
            st.markdown("### 🎯 Automated Validation Assessment")
            ans = st.radio("If you deploy ₹1,000 at a fixed 10% annual compounding velocity model, what is the exact cash profile value tracking at the end of Year Two?", ["₹1,200.00", "₹1,210.00", "₹1,100.00"])
            if st.button("Submit Profile Answer"):
                if ans == "₹1,210.00": st.success("Excellent Engineering Evaluation! +25 Finora XP Synced."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()
                else: st.error("Calculation mismatch. Remember that Year Two calculates yield parameters off the Year One exit valuation matrix (₹1,100).")

    elif c_idx == 4:
        if p_idx == 1:
            st.markdown("### Mutual Funds & Diversification Layouts")
            st.write("Mutual Funds mathematically combine investment structures from retail accounts to source highly diversified baskets of debt instruments and underlying stocks, decreasing unique single-asset downside traps.")
        elif p_idx == 2:
            st.markdown("### Systematic Investment Architectures (SIP)")
            st.write("SIP setups deploy small structured allocations automatically month over month. This locks in **Rupee Cost Averaging**, naturally buying fewer total fund shares when prices climb and more when values decline.")
        elif p_idx == 3:
            st.markdown("### Internal Management Overhead: Expense Ratios")
            st.write("Keep a sharp eye on the **Expense Ratio** metrics (the flat fee charged by portfolio management teams). Choosing Direct fund routes removes middlemen brokers and preserves significant capital gains long-term.")
        elif p_idx == 4:
            st.markdown("### 🎯 Automated Validation Assessment")
            ans = st.radio("Which deployment protocol utilizes systematic dollar/rupee cost averaging mechanics across volatile markets?", ["Market Timing Speculation", "Systematic Investment Plan (SIP) Averaging", "Leveraged Margin Swaps"])
            if st.button("Submit Profile Answer"):
                if "SIP" in ans: st.success("Correct! +25 Finora XP Synced."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    elif c_idx == 7:
        if p_idx == 1:
            st.markdown("### Credit Instruments & Consumer Ratings")
            st.write("Credit card options are valuable tools for stabilizing consumer metrics and earning purchase rebates, but they function strictly as high-cost short term lines of liability—not free supplemental income.")
        elif p_idx == 2:
            st.markdown("### The Minimum Balance Target Trap")
            st.write("Clearing only the 'Minimum Balance Due' protects you from fixed penalty markers but allows banks to charge high-cost interest rates (**36% to 45%+ annualized**) on your remaining balance.")
        elif p_idx == 3:
            st.markdown("### System Operational Guardrails")
            st.write("1. Check card transactions against real liquid deposits. If your checking balance cannot support it right now, **do not swipe.**\n2. Configure automated settings to pay off the **Total Statement Balance** in full every month.")
        elif p_idx == 4:
            st.markdown("### 🎯 Automated Validation Assessment")
            ans = st.radio("What happens if an account updates only the 'Minimum Balance Due' on standard statement loops?", ["The leftover principal debt is automatically erased", "The credit line compounds brutal interest rates (up to 40%+) against the remaining base debt", "Your profile rating increases instantly"])
            if st.button("Submit Profile Answer"):
                if "compounds high interest" in ans: st.success("Correct System Determination! +25 Finora XP Synced."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    else:
        if p_idx < 4:
            st.markdown(f"### {courses[c_idx]} (Section {p_idx})")
            st.write("This Finora academy learning block details optimization frameworks regarding compliance targets, personal tax paths, emergency buffer reserves, and portfolio allocations.")
        else:
            st.markdown("### 🎯 Comprehensive Track Quiz")
            ans = st.radio("Identify the optimized framework to achieve financial independence:", ["Keep extra cash liquid in checking portfolios", "Pay down high-interest debt, build an emergency cushion, and set up automated monthly index fund investments", "Trade volatile digital currencies on leverage margins"])
            if st.button("Submit Profile Answer"):
                if "Pay down high-interest" in ans: st.success("Correct Tracking! +25 Finora XP Synced."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    nav_col1, _, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if p_idx > 1:
            if st.button("⬅️ Previous Node", use_container_width=True): st.session_state.page_idx -= 1; st.rerun()
    with nav_col3:
        if p_idx < 4:
            if st.button("Advance Node ➡️", use_container_width=True): st.session_state.page_idx += 1; st.rerun()

def show_budgeting(username):
    st.markdown("<p class='section-header'>📉 Envelope Budgets & Real-time Cloud Ledger</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        with st.form("exp_form", clear_on_submit=True):
            cat = st.selectbox("Allocation Envelope Group", ["Food & Dining", "Education & Books", "Rent & Bills", "Entertainment & Leisure", "Mutual Funds & SIPs"])
            amt = st.number_input("Transaction Value Amount (₹)", min_value=1.0, value=500.0, step=50.0)
            if st.form_submit_button("Record Transaction Entry", use_container_width=True):
                supabase.table("expenses").insert({"username": username, "category": cat, "amount": amt}).execute()
                st.rerun()
                
        # FEATURE ADDITION: Dynamic Personalized Emergency Runway Calculator
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        res_p = supabase.table("profiles").select("occupation").eq("username", username).execute()
        track = res_p.data[0]['occupation'] if res_p.data else "Student"
        months_recommended = 6 if "Freelancer" in track or "Founder" in track else 4
        target_reserve = 8000.0 * months_recommended
        st.markdown(f"""
        <div class="metric-card" style="background:#f0fdfa; border: 1px solid #ccfbf1;">
            <span style="font-size:11.5px; color:#0f766e; font-weight:700; letter-spacing:0.5px;">🛡️ DEFENSIVE RUNWAY ARCHITECT</span><br/>
            <span style="font-size:13.5px; color:#115e59;">Based on your <b>{track}</b> track, you require a <b>{months_recommended}-Month</b> emergency cushion. Target Target Reserve: <b>₹{target_reserve:,.2f}</b></span>
        </div>
        """, unsafe_allow_html=True)
                
    with col2:
        res = supabase.table("expenses").select("*").eq("username", username).execute()
        total = sum([float(i['amount']) for i in res.data]) if res.data else 0.0
        
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 0px; border-left: 4px solid #0284c7;">
            <span style="font-size:12px; color:#64748b; font-weight:700; letter-spacing:0.5px;">BUDGET CAP UTILIZATION MATRIX</span><br/>
            <span style="font-size:22px; font-weight:800; color:#0284c7;">₹{total:,.2f} Used / ₹25,000 Target Threshold</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(total/25000, 1.0))
        
        # FEATURE ADDITION: Live Itemized Item List View Ledger
        st.markdown("<p style='font-size:14px; font-weight:700; color:#475569; margin-bottom:6px;'>📜 Itemized Transactions (Cloud Mirror)</p>", unsafe_allow_html=True)
        if res.data:
            for item in res.data[-4:]: # Show last 4 entries for space efficiency
                st.markdown(f"""
                <div class="ledger-row">
                    <span style="font-weight:600; color:#1e293b;">{item['category']}</span>
                    <span style="font-weight:700; color:#ef4444;">- ₹{float(item['amount']):,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:13px; color:gray; font-style:italic;'>No real-time transactions detected.</p>", unsafe_allow_html=True)

def show_savings():
    st.markdown("<p class='section-header'>🐷 Capital Yield Optimizers & SIP Calculators</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        principal = st.number_input("Principal Capital (₹)", min_value=1000, value=10000, step=1000)
        tenure = st.slider("Time Horizon Scope (Years)", 1, 10, 3)
    with col2:
        sav_rate, fd_rate, inf_rate, sip_rate = 0.035, 0.071, 0.060, 0.120
        sav_final = principal * ((1 + sav_rate) ** tenure)
        fd_final = principal * ((1 + fd_rate) ** tenure)
        
        # FEATURE ADDITION: Equity Index / SIP Compounding Yield Track Projection
        sip_final = principal * ((1 + sip_rate) ** tenure)
        
        purchasing_power = principal / ((1 + inf_rate) ** tenure)
        loss_value = principal - purchasing_power
        
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:12px; color:#64748b; font-weight:700; letter-spacing:0.5px;">GROWTH VALUE MATRIX FORECAST</span>
            <hr style="margin:8px 0; border-color:#e2e8f0;"/>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:5px 0;">
                <span style="color:#475569; font-weight:500;">Standard Savings Bank Account (~3.5%):</span>
                <span style="margin-left:auto; font-weight:700; color:#0f172a;">₹{sav_final:,.2f}</span>
            </div>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:5px 0; color:#0284c7;">
                <span style="font-weight: 600;">Fixed Deposit Standard Lockup (~7.1%):</span>
                <span style="margin-left:auto; font-weight:800;">₹{fd_final:,.2f}</span>
            </div>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:5px 0; color:#10b981;">
                <span style="font-weight: 600;">🚀 Finora Diversified SIP Target (~12.0%):</span>
                <span style="margin-left:auto; font-weight:800;">₹{sip_final:,.2f}</span>
            </div>
            <hr style="margin:8px 0; border-color:#e2e8f0;"/>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:5px 0; color:#ef4444; background:#fef2f2; padding:8px 12px; border-radius:8px;">
                <span style="font-weight:500;">⚠️ Mattress Cash Cash Devaluation Profile (~6% Inflation):</span>
                <span style="margin-left:auto; font-weight:700;">-₹{loss_value:,.2f} Buying Power Loss</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_splitting():
    st.markdown("<p class='section-header'>👥 peer-to-peer Settlement Engine & UPI Direct Links</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.4, 1.6])
    with col1:
        bill = st.number_input("Total Shared Bill Matrix (₹)", value=1500.0, step=100.0)
        people = st.slider("Split Cohort Size (Count)", 2, 12, 3)
        vpa = st.text_input("Your UPI Address Identifier VPA (Optional)", placeholder="example@upi").strip()
    with col2:
        per_person = round(bill/people, 2) if people > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:22px 18px; border-left: 6px solid #10b981; background: linear-gradient(180deg, #ffffff 0%, #f9fbf9 100%);">
            <span style="font-size:13.5px; color:#64748b; font-weight:600; letter-spacing:0.5px;">INDIVIDUAL ACCOUNT LIABILITY:</span><br/>
            <span style="font-size:40px; font-weight:900; color:#0f172a; line-height:1.2;">₹{per_person:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if vpa:
            st.markdown("<span style='font-size:13px; color:#475569; font-weight:700;'>⚡ GENERATED LINK PATTERN FOR MESSENGER SHARING:</span>", unsafe_allow_html=True)
            upi_link = f"upi://pay?pa={vpa}&pn=FinoraSplit&am={per_person}&cu=INR"
            st.code(upi_link, language="markdown")

# --- CORE APPLICATION MASTER SKELETON ---
if st.session_state.username is None:
    login_page()
else:
    profile = fetch_user_profile(st.session_state.username)
    
    with st.sidebar:
        st.markdown("<p class='main-header' style='font-size: 28px !important; margin-bottom:0px;'>✨ Finora</p>", unsafe_allow_html=True)
        st.caption(f"Operator Security Handle: {st.session_state.username.upper()}")
        
        user_points = profile['points'] if profile else 0
        st.markdown(f"🏆 Rewards: **{user_points} Finora XP**")
        st.markdown("<hr style='margin: 8px 0; border-color:#e2e8f0;'/>", unsafe_allow_html=True)
        
        if st.sidebar.button("📊 Analytics Control"): st.session_state.nav_selection = "📊 Dashboard"; st.rerun()
        if st.sidebar.button("📚 Finora Academy"): st.session_state.nav_selection = "📚 Micro-Courses"; st.rerun()
        if st.sidebar.button("📉 Budget Envelopes"): st.session_state.nav_selection = "📉 Expense Tracker"; st.rerun()
        if st.sidebar.button("🐷 Savings Multipliers"): st.session_state.nav_selection = "🐷 Savings Calculator"; st.rerun()
        if st.sidebar.button("👥 Split Peer Liabilities"): st.session_state.nav_selection = "👥 Split Bills"; st.rerun()
        
        st.markdown("<hr style='margin: 12px 0; border-color:#e2e8f0;'/>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Terminate App Session"):
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
