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

# --- THE FINORA MODERN COLOR & LAYOUT OVERHAUL ---
st.set_page_config(page_title="Finora | Smart Student Wealth Hub", page_icon="💳", layout="wide")

st.markdown("""
    <style>
    /* Absolute Structural Clean-up to Prevent Header Clipping & Drop Blank Space */
    [data-testid="stHeader"] {background: transparent; height: 0rem;}
    div.block-container {padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important;}
    #root > div:nth-child(1) > div > div > div {padding-top: 0px !important;}
    
    /* Premium Typography Scale */
    p, span, label, .stMarkdown {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 15px !important; 
        line-height: 1.6 !important;
        color: #334155;
    }
    .main-header {
        font-size: 28px !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        color: #0f172a;
    }
    .section-header {
        font-size: 21px !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
        color: #1e293b;
        margin-top: 2px !important;
        margin-bottom: 8px !important;
    }
    
    /* Re-Engineered Dashboard Cards (Slate & Emerald Theme) */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.04), 0 2px 4px -2px rgba(15, 23, 42, 0.04);
        margin-bottom: 12px;
    }
    .stLessonCard {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.01);
        margin-bottom: 14px;
    }
    
    /* Fully Polished Premium Sidebar Buttons */
    div.stButton > button:first-child {
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100%;
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
        padding: 10px 14px;
        font-size: 14px;
        font-weight: 600;
        border-radius: 8px;
        margin-bottom: 4px;
        color: #475569;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        border-color: #10b981;
        color: #10b981;
        background-color: #f0fdf4;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.06);
    }
    
    /* Align Form Inputs and Eliminate Structural Margins */
    [data-testid="stVerticalBlock"] {gap: 0.6rem !important;}
    .element-container {margin-bottom: 0rem !important;}
    div[data-testid="stForm"] {
        border: 1px solid #e2e8f0 !important;
        background: #ffffff !important;
        border-radius: 12px !important;
        padding: 16px !important;
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
    st.markdown("<p class='main-header' style='text-align: center; color: #10b981;'>✨ Finora</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size:15px; margin-top: -12px; margin-bottom: 24px;'>Smart Tools & Gamified Wealth Learning for Students</p>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1.4, 1.2, 1.4])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Secure Login", "📝 Create Finora Account"])
        with tab1:
            with st.form("login_form"):
                user_input = st.text_input("Username", placeholder="e.g. rahul_123").strip().lower()
                pass_input = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Log In To Dashboard", use_container_width=True):
                    profile = fetch_user_profile(user_input)
                    if profile and profile['password_hash'] == hash_password(pass_input):
                        st.session_state.username = user_input
                        st.rerun()
                    else:
                        st.error("Incorrect username or password.")
        with tab2:
            with st.form("reg_form"):
                new_user = st.text_input("Choose Unique Username").strip().lower()
                new_pass = st.text_input("Choose Strong Password", type="password")
                occ = st.selectbox("Current Track:", ["Undergraduate Student", "Freelancer", "High School Student", "Self-Employed / Founder"])
                if st.form_submit_button("Launch Finora Journey", use_container_width=True):
                    if new_user and new_pass:
                        try:
                            supabase.table("profiles").insert({
                                "username": new_user, "password_hash": hash_password(new_pass),
                                "age": 19, "occupation": occ, "points": 0
                            }).execute()
                            st.success("Account constructed! Please switch to the login tab.")
                        except APIError: st.error("Username is already taken.")

# --- WORKSPACE PANELS ---

def show_finance_desk(profile, username):
    st.markdown("<p class='section-header'>📊 Control Center Analytics</p>", unsafe_allow_html=True)
    left_panel, right_panel = st.columns([1.6, 1.4])
    
    res = supabase.table("expenses").select("*").eq("username", username).execute()
    total_spent = sum([float(i['amount']) for i in res.data]) if res.data else 0.0

    with left_panel:
        standing = profile['occupation'] if profile else "Student"
        points = profile['points'] if profile else 0
        level = "Beginner Saver" if points < 150 else "Smart Investor" if points < 400 else "Money Master"

        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #10b981;">
            <table style="width:100%; border:none; margin:0; line-height: 1.6;">
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b; font-weight:500;">Profile Track</td><td style="padding:4px; font-size:14.5px; font-weight:700; text-align:right; color:#0f172a;">{standing}</td></tr>
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b; font-weight:500;">Learning Points</td><td style="padding:4px; font-size:14.5px; font-weight:700; text-align:right; color:#0284c7;">🏅 {points} XP</td></tr>
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b; font-weight:500;">Finora Ranking</td><td style="padding:4px; font-size:14.5px; font-weight:700; text-align:right; color:#10b981;">{level}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        predicted_annual = total_spent * 12
        if predicted_annual > 0:
            status_color = "#ef4444" if predicted_annual > 150000 else "#10b981"
            status_text = "Critical Outflows" if predicted_annual > 150000 else "Optimal Allocation Profile"
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {status_color}; background: #fafafa;">
                <span style="font-size:12px; color:#64748b; font-weight:700; letter-spacing:0.5px;">🔮 INTELLIGENT CASH BURN PREDICTOR</span><br/>
                <span style="font-size:15px; color:#1e293b;">Estimated Annualized Burn Rate: <b>₹{predicted_annual:,.2f}</b></span><br/>
                <span style="font-size:13px; color:{status_color}; font-weight:700; margin-top:2px; display:inline-block;">System Health: {status_text}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<p style='font-size: 16px; font-weight: 700; color:#334155; margin-bottom:4px;'>⚡ Instant Expense Entry</p>", unsafe_allow_html=True)
        with st.form("quick_log_form", clear_on_submit=True):
            q_col1, q_col2, q_col3 = st.columns([1.5, 1.1, 1.1])
            with q_col1: q_cat = st.selectbox("Category", ["Food & Dining", "Education & Books", "Rent & Bills", "Entertainment & Leisure", "Mutual Funds & SIPs"], key="q_cat")
            with q_col2: q_amt = st.number_input("Amount (₹)", min_value=1.0, value=100.0, step=10.0, key="q_amt")
            with q_col3: 
                st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                q_sub = st.form_submit_button("Log Transaction", use_container_width=True)
            if q_sub:
                supabase.table("expenses").insert({"username": username, "category": q_cat, "amount": q_amt}).execute()
                st.toast("Expense logged!", icon="✅")
                st.rerun()

    with right_panel:
        if res.data:
            df = pd.DataFrame(res.data)
            df['amount'] = df['amount'].astype(float)
            fig = px.pie(df, values='amount', names='category', hole=0.6, color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(height=240, margin=dict(t=10, b=10, l=10, r=10), showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div style='height:210px; display:flex; align-items:center; justify-content:center; background:#f8fafc; border: 1px dashed #cbd5e1; border-radius:12px; color:#64748b; font-size:14px; margin-top:4px;'>Your asset breakdown graph will render here once you record an entry.</div>", unsafe_allow_html=True)

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
    with h_col1: st.markdown("<p class='section-header'>📚 Gamified Academy Lessons</p>", unsafe_allow_html=True)
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
    st.progress(current_step / total_steps, text=f"Academy Milestones: {int((current_step/total_steps)*100)}% Verified Track (Page {current_step}/{total_steps})")
    
    st.markdown(f"<div class='stLessonCard'><span style='color:#10b981; font-weight:800; font-size:11.5px; letter-spacing:0.8px;'>SECTION PROGRESS TRACKER • UNIT {p_idx} OF 4</span>", unsafe_allow_html=True)

    if c_idx == 0:
        if p_idx == 1:
            st.markdown("### The Mechanics of Compounding")
            st.write("Compounding functions as standard interest generation mapped over previously accrued rewards. When you automatically reinvest asset returns back into the core pool, your principal curves begin to grow exponentially faster.")
        elif p_idx == 2:
            st.markdown("### Structural Metrics: The Rule of 72")
            st.write("Divide your targeted constant index value of **72** by any annual percentage return metric to uncover the timeline scale needed to double your principal base values.")
            st.latex(r"Years\ to\ Double = \frac{72}{Interest\ Rate}")
        elif p_idx == 3:
            st.markdown("### The Core Balance Formula")
            st.write("The exact mathematical model that handles exponential growth configurations across global liquid investment vectors:")
            st.latex(r"A = P\left(1 + \frac{r}{n}\right)^{nt}")
        elif p_idx == 4:
            st.markdown("### 🎯 Knowledge Check Quiz")
            ans = st.radio("If you deploy ₹1,000 at a fixed 10% annual compounding rate, what is the asset value matrix after year two?", ["₹1,200.00", "₹1,210.00", "₹1,100.00"])
            if st.button("Submit Verified Answer"):
                if ans == "₹1,210.00": st.success("Correct Answer Architecture! +25 Finora XP."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()
                else: st.error("Incorrect. Remember, the second year's calculation metrics are run against the year-one ending balance value (₹1,100).")

    elif c_idx == 4:
        if p_idx == 1:
            st.markdown("### Mutual Funds & Diversification Architecture")
            st.write("A Mutual Fund consolidates capital from thousands of retail participants to purchase a highly diversified allocation portfolio of stocks and bonds. This acts as a shield against individual asset volatility.")
        elif p_idx == 2:
            st.markdown("### Systemic Investment Plans (SIP)")
            st.write("An SIP deploys fixed recurring capital (e.g., ₹500/month) into your selected mutual fund automatically. This maximizes **Rupee Cost Averaging**, protecting you from buying when the market is overly expensive.")
        elif p_idx == 3:
            st.markdown("### Expense Ratios & Distribution Vectoring")
            st.write("Pay close attention to the **Expense Ratio** (the management overhead percentage fee). Direct funds completely cut out intermediate fund brokers, maximizing your real yield returns over long timelines.")
        elif p_idx == 4:
            st.markdown("### 🎯 Knowledge Check Quiz")
            ans = st.radio("Which execution pathway utilizes automated averaging to safely accumulate mutual fund balances?", ["Market Timing Speculation", "Systematic Investment Plan (SIP) Averaging", "Day Trading Options"])
            if st.button("Submit Verified Answer"):
                if "SIP" in ans: st.success("Correct! +25 Finora XP."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    elif c_idx == 7:
        if p_idx == 1:
            st.markdown("### Credit Card Structural Infrastructures")
            st.write("Credit cards are excellent for building reliable credit ratings and collecting cash rebates. However, they are short-term loans, not extra income. Treating them carelessly can quickly damage your financial health.")
        elif p_idx == 2:
            st.markdown("### The Minimum Balance Mirage")
            st.write("Clearing only the 'Minimum Balance Due' helps you avoid flat late penalties, but allows credit companies to compound high-cost interest rates (**36% to 45%+ annually**) on the remaining debt.")
        elif p_idx == 3:
            st.markdown("### Golden Guardrails for Swiping")
            st.write("1. Match every card transaction against real liquid deposits. If your checking balance cannot support it right now, **do not swipe.**\n2. Configure automated settings to pay off the **Total Statement Balance** in full every month.")
        elif p_idx == 4:
            st.markdown("### 🎯 Knowledge Check Quiz")
            ans = st.radio("What happens if you clear only the 'Minimum Balance Due' on your credit card bill?", ["The remaining balance is forgiven", "The financial institution compounds high interest rates (up to 40%+) on your remaining debt", "Your credit rating spikes automatically"])
            if st.button("Submit Verified Answer"):
                if "compounds high interest" in ans: st.success("Correct! +25 Finora XP."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    else:
        if p_idx < 4:
            st.markdown(f"### {courses[c_idx]} (Section {p_idx})")
            st.write("This Finora module outlines specific wealth frameworks designed to help you streamline your budget tracking, build an emergency cushion, and master smart investing habits.")
        else:
            st.markdown("### 🎯 Comprehensive Track Quiz")
            ans = st.radio("Identify the optimized framework to achieve financial independence:", ["Keep extra cash liquid in checking portfolios", "Pay down high-interest debt, build an emergency cushion, and set up automated monthly index fund investments", "Trade volatile digital currencies on leverage margins"])
            if st.button("Submit Verified Answer"):
                if "Pay down high-interest" in ans: st.success("Correct! +25 Finora XP."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    nav_col1, _, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if p_idx > 1:
            if st.button("⬅️ Back", use_container_width=True): st.session_state.page_idx -= 1; st.rerun()
    with nav_col3:
        if p_idx < 4:
            if st.button("Next Lesson ➡️", use_container_width=True): st.session_state.page_idx += 1; st.rerun()

def show_budgeting(username):
    st.markdown("<p class='section-header'>📉 Expense Envelopes & Target Allocation</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        with st.form("exp_form", clear_on_submit=True):
            cat = st.selectbox("Budget Target Bucket", ["Food & Dining", "Education & Books", "Rent & Bills", "Entertainment & Leisure", "Mutual Funds & SIPs"])
            amt = st.number_input("Transaction Value (₹)", min_value=1.0, value=500.0, step=50.0)
            if st.form_submit_button("Log Transaction", use_container_width=True):
                supabase.table("expenses").insert({"username": username, "category": cat, "amount": amt}).execute()
                st.rerun()
    with col2:
        res = supabase.table("expenses").select("amount").eq("username", username).execute()
        total = sum([float(i['amount']) for i in res.data])
        
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 15px; border-left: 4px solid #0284c7;">
            <span style="font-size:12px; color:#64748b; font-weight:700; letter-spacing:0.5px;">BUDGET CAP UTILIZATION MATRIX</span><br/>
            <span style="font-size:22px; font-weight:800; color:#0284c7;">₹{total:,.2f} Used / ₹25,000 Target Threshold</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(total/25000, 1.0))

def show_savings():
    st.markdown("<p class='section-header'>🐷 Yield Multipliers & Inflation Risk Simulations</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        principal = st.number_input("Principal Capital (₹)", min_value=1000, value=10000, step=1000)
        tenure = st.slider("Time Period Horizon (Years)", 1, 10, 3)
    with col2:
        sav_rate, fd_rate, inf_rate = 0.035, 0.071, 0.060
        sav_final = principal * ((1 + sav_rate) ** tenure)
        fd_final = principal * ((1 + fd_rate) ** tenure)
        
        purchasing_power = principal / ((1 + inf_rate) ** tenure)
        loss_value = principal - purchasing_power
        
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:12px; color:#64748b; font-weight:700; letter-spacing:0.5px;">GROWTH VALUE COMPARISON MATRIX</span>
            <hr style="margin:8px 0; border-color:#e2e8f0;"/>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:5px 0;">
                <span style="color:#475569; font-weight:500;">Standard Savings Account Balance (~3.5%):</span>
                <span style="margin-left:auto; font-weight:700; color:#0f172a;">₹{sav_final:,.2f}</span>
            </div>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:6px 0; color:#10b981;">
                <span style="font-weight: 600;">Fixed Deposit Balance Value (~7.1% Yield):</span>
                <span style="margin-left:auto; font-weight:800;">₹{fd_final:,.2f}</span>
            </div>
            <hr style="margin:8px 0; border-color:#e2e8f0;"/>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:5px 0; color:#ef4444; background:#fef2f2; padding:8px 12px; border-radius:6px;">
                <span style="font-weight:500;">⚠️ Inflation Loss Simulation (~6% Inflation Drag):</span>
                <span style="margin-left:auto; font-weight:700;">-₹{loss_value:,.2f} Purchasing Power</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_splitting():
    st.markdown("<p class='section-header'>👥 Smart Bill Splitter & Shareable UPI Generation</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.4, 1.6])
    with col1:
        bill = st.number_input("Total Shared Bill Amount (₹)", value=1500.0, step=100.0)
        people = st.slider("Split Cohort Size (Number of Friends)", 2, 12, 3)
        vpa = st.text_input("Your UPI Address VPA (Optional)", placeholder="example@upi").strip()
    with col2:
        per_person = round(bill/people, 2) if people > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:20px 16px; border-left: 6px solid #10b981; background: #fafafa;">
            <span style="font-size:13.5px; color:#64748b; font-weight:600; letter-spacing:0.5px;">INDIVIDUAL SHARED REPAYMENT LIABILITY:</span><br/>
            <span style="font-size:38px; font-weight:900; color:#0f172a; line-height:1.2;">₹{per_person:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if vpa:
            st.markdown("<span style='font-size:13px; color:#475569; font-weight:700;'>⚡ COPY CHAT LINK ROUTE ENGINE:</span>", unsafe_allow_html=True)
            upi_link = f"upi://pay?pa={vpa}&pn=FinoraSplit&am={per_person}&cu=INR"
            st.code(upi_link, language="markdown")

# --- CORE APPLICATION MASTER SKELETON ---
if st.session_state.username is None:
    login_page()
else:
    profile = fetch_user_profile(st.session_state.username)
    
    with st.sidebar:
        st.markdown("<p class='main-header' style='color:#10b981; font-size: 26px !important;'>✨ Finora</p>", unsafe_allow_html=True)
        st.caption(f"Operator Account: {st.session_state.username.upper()}")
        
        user_points = profile['points'] if profile else 0
        st.markdown(f"🏆 Rewards: **{user_points} Finora XP**")
        st.markdown("<hr style='margin: 8px 0; border-color:#e2e8f0;'/>", unsafe_allow_html=True)
        
        if st.sidebar.button("📊 Analytics Dashboard"): st.session_state.nav_selection = "📊 Dashboard"; st.rerun()
        if st.sidebar.button("📚 Finora Academy"): st.session_state.nav_selection = "📚 Micro-Courses"; st.rerun()
        if st.sidebar.button("📉 Expense Envelopes"): st.session_state.nav_selection = "📉 Expense Tracker"; st.rerun()
        if st.sidebar.button("🐷 Savings Multiplier"): st.session_state.nav_selection = "🐷 Savings Calculator"; st.rerun()
        if st.sidebar.button("👥 Split Peer Expenses"): st.session_state.nav_selection = "👥 Split Bills"; st.rerun()
        
        st.markdown("<hr style='margin: 12px 0; border-color:#e2e8f0;'/>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Close Account Session"):
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
