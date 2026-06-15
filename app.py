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

# --- CONFIG & STYLING GRID ---
st.set_page_config(page_title="FinSmart App", page_icon="💳", layout="wide")

st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem;}
    .stCard {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 24px;
        border-left: 6px solid #4A90E2;
        margin-bottom: 20px;
    }
    .stLessonCard {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE HELPER FUNCTIONS ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def fetch_user_profile(username):
    try:
        res = supabase.table("profiles").select("*").eq("username", username.strip().lower()).execute()
        return res.data[0] if res.data else None
    except APIError as e:
        st.error(f"Database Error: {e.message}")
        return None

if "username" not in st.session_state:
    st.session_state.username = None

# --- AUTHENTICATION SCREEN ---
def login_page():
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🎓 FinSmart Platform</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>The All-in-One Interactive Financial Hub for Students</p>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1, 1.8, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Account Login", "📝 New Registration"])
        
        with tab1:
            with st.form("login_form"):
                user_input = st.text_input("Username").strip().lower()
                pass_input = st.text_input("Password", type="password")
                submit = st.form_submit_button("Launch Dashboard", use_container_width=True)
                
                if submit:
                    if user_input and pass_input:
                        profile = fetch_user_profile(user_input)
                        if profile and profile['password_hash'] == hash_password(pass_input):
                            st.session_state.username = user_input
                            st.success(f"Authenticated as {user_input}!")
                            st.rerun()
                        else:
                            st.error("Invalid structural username or account security passphrase confirmation.")
                    else:
                        st.warning("All verification text fields are mandatory inputs.")
                        
        with tab2:
            with st.form("reg_form"):
                new_user = st.text_input("Choose Username").strip().lower()
                new_pass = st.text_input("Choose Password", type="password")
                age = st.slider("Age Indicator", 15, 30, 19)
                occupation = st.selectbox("Current Activity Track", ["High School Student", "Undergraduate", "Freelancing Student", "Startup Operator"])
                register_submit = st.form_submit_button("Confirm & Generate Profile Ledger", use_container_width=True)
                
                if register_submit:
                    if new_user and new_pass:
                        if fetch_user_profile(new_user):
                            st.error("This individual identity record index already exists inside the cloud layer.")
                        else:
                            try:
                                supabase.table("profiles").insert({
                                    "username": new_user, "password_hash": hash_password(new_pass),
                                    "age": age, "occupation": occupation, "points": 0
                                }).execute()
                                st.success("Account provisioned! Proceed to the login portal tab.")
                            except APIError as e:
                                st.error(f"Write validation abort: {e.message}")
                    else:
                        st.warning("Input allocations require minimum profile identity strings.")

# --- APPLICATION DESK CORE INTERFACES ---
def application_shell():
    username = st.session_state.username
    profile = fetch_user_profile(username)
    
    # User Profile Top Belt Banner Layout
    st.markdown(f"### 👋 Student Station: {username.capitalize()} ({profile['occupation'] if profile else 'Student'}) | 🏅 **{profile['points'] if profile else 0} XP**")
    
    # TARGET TAB NAVIGATION MATRIX LAYOUT STRUCTURE
    t_course, t_finance, t_budgeting, t_savings, t_splitting = st.tabs([
        "📚 Micro-Courses", 
        "📊 Personal Finance Desk", 
        "📉 Budgeting Tracker", 
        "🐷 Savings Accelerator", 
        "👥 Friends Splitting Matrix"
    ])
    
    # ----------------------------------------------------
    # TAB 1: FULL INTERACTIVE ACADEMY MICRO-COURSES
    # ----------------------------------------------------
    with t_course:
        st.markdown("## 📚 Financial Literacy Micro-Academy")
        st.caption("Complete these interactive study frames to secure functional capability and earn profile experience milestones.")
        
        module = st.selectbox("Select Target Course Blueprint Module", [
            "Module 1: The Wealth Acceleration Engine (Compounding)",
            "Module 2: Tactical Capital Management (The 50/30/20 Framework)",
            "Module 3: Debt Arbitrage & Student Leverage Principles"
        ])
        
        st.markdown("<div class='stLessonCard'>", unsafe_allow_html=True)
        if "Module 1" in module:
            st.markdown("### 📈 The Velocity of Compound Growth Architecture")
            st.write("Compounding represents calculation architecture where yields generate additional subsequent returns over time. Rather than withdrawing asset gains, capital values reinvest continually, creating geometric, parabolic growth lines.")
            st.latex(r"A = P \left(1 + \frac{r}{n}\right)^{nt}")
            st.info("💡 **Core Lesson:** Time is your primary multiplier. Beginning small consistency vectors at age 20 creates exponentially more asset scale than chasing larger velocity vectors beginning late at age 35.")
            
            # Interactive Quiz Check
            st.markdown("---")
            q1 = st.radio("Quiz Assessment: If you deposit $1,000 compounding at an annual interest yield of 10%, what is the profile value tracking state at Year 2 conclusion?", ["$1,100.00", "$1,200.00", "$1,210.00 (Correct answer compounds Year 1 gains!)"])
            if st.button("Log Module Evaluation Answer", key="m1_check"):
                if "1,210.00" in q1:
                    st.success("🎉 Outstanding logic! Asset structures reinvested and generated additional compound dividends.")
                    if profile: supabase.table("profiles").update({"points": profile['points'] + 25}).eq("username", username).execute()
                else:
                    st.error("❌ Yield calculation misalignment. Remember that interest metrics apply directly onto fresh, modified base structures.")

        elif "Module 2" in module:
            st.markdown("### 🎛️ Dynamic 50/30/20 Structural Capital Management")
            st.write("Budget engineering fails when rules are too strict. The absolute industry gold standard method divides post-tax metrics into clear structural categories:")
            st.markdown("- **50% Fixed Absolute Commitments:** Housing structures, standard transportation, utility lines, basic fuel food targets.")
            st.markdown("- **30% Discretionary Welfare:** Entertainment, streaming pipelines, high-tier apparel alternatives.")
            st.markdown("- **20% Forward Asset Acceleration:** Equities, retirement vectors, debt liquidation, cash reserves.")
            
            st.markdown("---")
            q2 = st.radio("Quiz Assessment: Under basic standard 50/30/20 criteria metrics, where should credit card payment clear downs balance into?", ["Discretionary Welfare Allocations (30%)", "Forward Asset Acceleration Vectors (20%)", "Fixed Structural Commitments (50%)"])
            if st.button("Log Module Evaluation Answer", key="m2_check"):
                if "Forward Asset" in q2:
                    st.success("🎉 Correct choice! Eliminating high-yield debt is structurally equivalent to investing into cash yielders.")
                    if profile: supabase.table("profiles").update({"points": profile['points'] + 25}).eq("username", username).execute()
                else:
                    st.error("❌ Optimization error. Debt resolution forms a critical element of forward balance sheet acceleration parameters.")

        else:
            st.markdown("### 🎓 Navigating Student Leverage & Credit Capital Profiles")
            st.write("Credit scores function as systematic evaluations determining interest pricing limits. Protecting your score requires maintaining utilization parameters under 30% of total revolving capital credit thresholds.")
            
            st.markdown("---")
            q3 = st.radio("Quiz Assessment: What calculation variable dominates your macro programmatic credit evaluation model matrix?", ["Total Number of Applied Credit Limits", "Historical payment performance timeline data", "The absolute currency scale inside checking lines"])
            if st.button("Log Module Evaluation Answer", key="m3_check"):
                if "Historical payment" in q3:
                    st.success("🎉 Correct execution! Consistent, on-time payment logs represent the most critical indicator of credit safety profiles.")
                    if profile: supabase.table("profiles").update({"points": profile['points'] + 25}).eq("username", username).execute()
                else:
                    st.error("❌ Evaluation disconnect. Payment reliability metrics form the foundation of institutional credit parameters.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 2: PERSONAL FINANCE DESK & SYSTEM ANALYTICS
    # ----------------------------------------------------
    with t_finance:
        st.markdown("## 📊 Personal Balance Sheet Control Center")
        st.caption("A birds-eye view of your financial health, asset health, and transaction summaries.")
        
        try:
            res = supabase.table("expenses").select("*").eq("username", username).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df['amount'] = df['amount'].astype(float)
                total_outflow = df['amount'].sum()
                
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("Total Documented Capital Outflow", f"${total_outflow:.2f}")
                kpi2.metric("Active Run-rate Status", "Within Safe Bounds" if total_outflow < 500 else "Over Limit Parameters")
                kpi3.metric("Platform Milestone Standing", "Bronze Tier Scholar" if total_outflow < 300 else "Elite Asset Controller")
                
                st.markdown("### 📈 Capital Distribution Profiles")
                fig = px.pie(df, values='amount', names='category', hole=0.45, color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_layout(height=350, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No tracking arrays mapped to your profile profile yet. Log your first expense object inside the Budgeting Tracker tab.")
        except APIError as e:
            st.error(f"Failed to fetch data logs: {e.message}")

    # ----------------------------------------------------
    # TAB 3: BUDGETING TRACKER (EXPENSE ENGINE)
    # ----------------------------------------------------
    with t_budgeting:
        st.markdown("## 📉 Real-time Budgeting Tracker Ledger")
        st.caption("Log items quickly to run live pattern processing filters against your expenditure limits.")
        
        col_input, col_alert = st.columns([1, 1.5])
        with col_input:
            st.markdown("<div class='stCard'>🔒 Log Transaction Entry</div>", unsafe_allow_html=True)
            with st.form("budget_form", clear_on_submit=True):
                cat = st.selectbox("Allocation Stream", ["Food & Routine Outlays", "Academic Materials", "Housing & Operational Utilities", "Leisure / Welfare Options", "Startup Portfolio Ventures"])
                cost = st.number_input("Currency Amount Value ($)", min_value=0.25, step=1.00)
                submit_expense = st.form_submit_button("Commit Expense Object to Ledger", use_container_width=True)
                
                if submit_expense:
                    try:
                        supabase.table("expenses").insert({"username": username, "category": cat, "amount": cost}).execute()
                        st.toast("Expense appended safely!", icon="📝")
                        st.rerun()
                    except APIError as e:
                        st.error(f"Failed to compile asset write protocols: {e.message}")
                        
        with col_alert:
            st.markdown("#### 🚨 System Threshold Safety Monitors")
            try:
                res = supabase.table("expenses").select("amount").eq("username", username).execute()
                costs = [float(item['amount']) for item in res.data] if res.data else []
                current_sum = sum(costs)
                cap = 500.00
                
                st.progress(min(current_sum / cap, 1.0), text=f"Limit Consumption Meter: ${current_sum:.2f} / ${cap:.2f}")
                
                if current_sum > cap:
                    st.error(f"🚨 BUDGET LIMIT VIOLATION: Current tracking bounds exceed your target thresholds by ${current_sum - cap:.2f}!")
                elif current_sum > (cap * 0.8):
                    st.warning("⚠️ PROXIMITY ALERT: Capital consumption levels have scaled past 80% of your maximum safe monthly parameters.")
                else:
                    st.success("🍏 OPERATIONAL COMFORT: Account processing values indicate safe structural run-rates.")
            except APIError as e:
                st.error(f"Could not load monitors: {e.message}")

    # ----------------------------------------------------
    # TAB 4: SAVINGS ACCELERATOR & GOAL ENGINE
    # ----------------------------------------------------
    with t_savings:
        st.markdown("## 🐷 High-Yield Savings Optimization Engine")
        st.caption("Simulate wealth preservation paths and configure compound growth milestone horizons.")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("<div class='stCard'>🎯 Savings Target Calculator</div>", unsafe_allow_html=True)
            goal_name = st.text_input("What are you saving for?", value="Emergency Reserve Fund")
            target_sum = st.number_input("Target Goal Sum ($)", min_value=100.0, value=2000.0, step=100.0)
            monthly_save = st.number_input("Monthly Contribution Capability ($)", min_value=10.0, value=150.0, step=10.0)
            
            months_required = ceil_months = int(-(-target_sum // monthly_save))
            st.info(f"⏱️ **Milestone Timeline:** You will achieve your **{goal_name}** target in approximately **{months_required} months** at this savings velocity.")
            
        with col_g2:
            st.markdown("<div class='stCard'>🏦 The Cost of Keeping Cash in Basic Checking</div>", unsafe_allow_html=True)
            st.write("Traditional student bank checking lines typically offer flat interest yields near **0.01%**. Modern online High-Yield Savings Accounts (HYSAs) consistently track around **4.50%**.")
            
            principal = st.slider("Simulated Cash Balance Value ($)", 500, 10000, 2500, step=500)
            checking_yield = principal * 0.0001
            hysa_yield = principal * 0.045
            
            st.metric("HYSA Annual Dividend Advantage", f"${hysa_yield:.2f}", delta=f"+${hysa_yield - checking_yield:.2f} vs Basic Bank")
            st.caption("Switching to high-yield storage channels lets your baseline cash safety nets outpace inflationary devaluation trends automatically.")

    # ----------------------------------------------------
    # TAB 5: FRIENDS SPLITTING MATRIX
    # ----------------------------------------------------
    with t_splitting:
        st.markdown("## 👥 Student Shared Expense Settlement Engine")
        st.caption("Instantly divide shared bills like dorm utility shares, textbook pools, or shared group project materials.")
        
        st.markdown("<div class='stCard'>", unsafe_allow_html=True)
        with st.form("split_ledger_form"):
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                invoice_val = st.number_input("Total Invoice Cost Matrix ($)", min_value=1.00, value=60.00, step=5.00)
                originator = st.text_input("Who paid the initial bill?", value="Myself")
            with s_col2:
                headcount = st.number_input("Headcount Splitting Share (Including Self)", min_value=2, value=3, step=1)
                item_desc = st.text_input("Shared Item/Project Description", value="Dorm Internet Subscription")
                
            execute_split = st.form_submit_button("Compute Group Balances", use_container_width=True)
            if execute_split:
                per_person_liability = invoice_val / headcount
                st.markdown(f"### 🎯 Allocation Target: **${per_person_liability:.2f} per person**")
                st.info(f"💡 **Actionable Split Nudge Triggered:** Send payment requests for **${per_person_liability:.2f}** to each peer group member to reimburse **{originator}** for '{item_desc}'.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- SYSTEM COMPONENT CONTROLLER ---
if st.session_state.username is None:
    login_page()
else:
    st.sidebar.markdown(f"👤 Active Session: **{st.session_state.username.upper()}**")
    if st.sidebar.button("🚪 Log Out of Platform Workspace", use_container_width=True):
        st.session_state.username = None
        st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.caption("FinSmart Studio v3.0\nSecure Multi-Tab Architecture Client")
    application_shell()
