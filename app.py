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

# --- CONFIG & STYLING ---
st.set_page_config(page_title="FinSmart Academy", page_icon="💳", layout="wide")

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
        padding: 25px;
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.02);
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #eee;
    }
    /* Style sidebar buttons to look like custom nav links */
    div.stButton > button:first-child {
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100%;
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
        padding: 10px 15px;
    }
    div.stButton > button:first-child:hover {
        border-color: #4A90E2;
        color: #4A90E2;
    }
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

# --- AUTHENTICATION ---
def login_page():
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🎓 FinSmart Studio</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Secure Student Financial Intelligence Hub</p>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1, 1.8, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Account Login", "📝 New Registration"])
        with tab1:
            with st.form("login_form"):
                user_input = st.text_input("Username").strip().lower()
                pass_input = st.text_input("Password", type="password")
                submit = st.form_submit_button("Launch Dashboard", use_container_width=True)
                if submit:
                    profile = fetch_user_profile(user_input)
                    if profile and profile['password_hash'] == hash_password(pass_input):
                        st.session_state.username = user_input
                        st.rerun()
                    else:
                        st.error("Invalid credentials provided.")
        with tab2:
            with st.form("reg_form"):
                new_user = st.text_input("Choose Username").strip().lower()
                new_pass = st.text_input("Choose Password", type="password")
                occ = st.selectbox("Current Track", ["Undergraduate", "Freelancer", "High School", "Founder"])
                if st.form_submit_button("Create Account", use_container_width=True):
                    if new_user and new_pass:
                        try:
                            supabase.table("profiles").insert({
                                "username": new_user, "password_hash": hash_password(new_pass),
                                "age": 19, "occupation": occ, "points": 0
                            }).execute()
                            st.success("Account created! Go to Login.")
                        except APIError: st.error("Username already taken.")

# --- MAIN APP PAGES ---

def show_finance_desk(profile, username):
    st.markdown("## 📊 Personal Finance Desk")
    st.caption("Real-time summary of your account standing and XP growth.")
    
    standing = profile['occupation'] if profile else "Student"
    points = profile['points'] if profile else 0
    level = "Beginner" if points < 150 else "Intermediate" if points < 300 else "Financial Master"

    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Current Standing", standing)
    with m2: st.metric("Platform XP", f"🏅 {points}")
    with m3: st.metric("Academic Rank", level)

    st.markdown("---")
    res = supabase.table("expenses").select("*").eq("username", username).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['amount'] = df['amount'].astype(float)
        fig = px.pie(df, values='amount', names='category', hole=0.5, title="Expense Allocation Breakdown")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data tracking entries discovered. Log expenses inside the 'Budgeting Tracker' module.")

def show_micro_courses(profile, username):
    st.markdown("## 📚 Financial Intelligence Academy")
    st.caption("Review the complete 8-course foundational blueprint text below. Complete the Master Quiz at the bottom to lock in +100 XP.")
    
    current_points = profile['points'] if profile else 0

    # 1. COMPOUNDING
    st.markdown("<div class='stLessonCard'>", unsafe_allow_html=True)
    st.markdown("### 📈 Course 1: The Velocity of Compounding Architecture")
    st.write("Compounding functions as calculation architecture where your yields generate additional subsequent returns over time. Rather than withdrawing asset gains, capital values reinvest continually, creating geometric growth lines.")
    st.latex(r"A = P(1 + r/n)^{nt}")
    st.write("Starting early is a massive multiplier. Investing a small amount at age 20 creates exponentially more asset scale than chasing larger contributions starting at age 35 due to the runway available for interest to multiply.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. 50/30/20 RULE
    st.markdown("<div class='stLessonCard'>", unsafe_allow_html=True)
    st.markdown("### 🎛️ Course 2: Tactical Capital Allocation (The 50/30/20 Rule)")
    st.write("Budget engineering fails when rules are too strict. The industry standard allocation divides post-tax metrics into clear structural categories:")
    st.markdown("- **50% Needs:** Housing, fixed transportation, utilities, and raw grocery baselines.")
    st.markdown("- **30% Wants:** Entertainment channels, streaming networks, luxury dining, and hobbies.")
    st.markdown("- **20% Financial Future:** Equities portfolios, index funds, retirement accounts, and debt clear downs.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. CREDIT SCORES
    st.markdown("<div class='stLessonCard'>", unsafe_allow_html=True)
    st.markdown("### 💳 Course 3: Credit Architecture & Institutional Trust")
    st.write("Credit scores operate as algorithmic measures determining borrowing risks. Your payment history accounts for 35% of this calculation score, while credit utilization makes up 30%.")
    st.write("To establish clean, scalable ratings before graduation, keep rolling balances strictly below 30% of total available revolving limits and avoid missed payment windows completely.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. INDEX FUNDS & ETFS
    st.markdown("<div class='stLessonCard'>", unsafe_allow_html=True)
    st.markdown("### 🏛️ Course 4: Index Funds & Passive Market Capture")
    st.write("Instead of risking your capital picking single individual company stocks (like Apple or Tesla), index funds purchase tiny fractions of the entire market simultaneously (e.g., the S&P 500 basket).")
    st.write("This structure offers built-in diversification. Historically, broad market indexes average an annual return of roughly 7-10% over long horizons, outperforming more than 90% of actively managed professional funds.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 5. EMERGENCY FUNDS
    st.markdown("<div class='stLessonCard'>", unsafe_allow_html=True)
    st.markdown("### 🛡️ Course 5: The Liquidity Safety Buffer (Emergency Funds)")
    st.write("An emergency fund acts as an insulation layer between unexpected real-world shocks (medical needs, automotive repairs, or job transitions) and your investment assets.")
    st.write("Financial security standards dictate maintaining 3 to 6 months of baseline living expenses entirely in liquid assets. This capital should remain accessible inside non-volatile checking or specialized High-Yield Savings Accounts (HYSAs).")
    st.markdown("</div>", unsafe_allow_html=True)

    # 6. SIDE-HUSTLE TAXES
    st.markdown("<div class='stLessonCard'>", unsafe_allow_html=True)
    st.markdown("### 🧾 Course 6: Taxation Dynamics for Freelancers & Operators")
    st.write("Generating income outside a traditional employee paycheck (e.g., freelancing, independent design contracts, content creation) subjects your capital to self-employment tax criteria.")
    st.write("Because independent contractors do not have tax withholding subtracted automatically from their payments, you must proactively reserve roughly 25-30% of gross independent income streams to cover regular quarterly tax submissions.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 7. INFLATION ARBITRAGE
    st.markdown("<div class='stLessonCard'>", unsafe_allow_html=True)
    st.markdown("### 💸 Course 7: Inflation Dynamics & Asset Erosion")
    st.write("Inflation is the steady drop in a currency's purchasing power over time. When inflation tracks at 3% annually, a basket of goods costing $100 this year will command $103 next year.")
    st.write("Leaving long-term cash sitting idle in traditional checking accounts yielding 0.01% guarantees real wealth loss. To maintain and grow your wealth, your capital must be deployed into assets that yield returns higher than the baseline rate of inflation.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 8. DEBT LEVERAGE
    st.markdown("<div class='stLessonCard'>", unsafe_allow_html=True)
    st.markdown("### ⚖️ Course 8: Evaluating High vs. Low Cost Debt Leverage")
    st.write("Not all debt liabilities carry the same structural impact. High-cost debt—like credit cards averaging 20-30% interest rates—drains your cash flow and must be paid down immediately.")
    st.write("Conversely, low-cost debt, such as subsidized student loans or mortgages under 4-5%, can be managed systematically. This allows you to route extra savings into investments that generate higher average returns.")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- UNIFIED ACADEMY GRADUATION QUIZ ---
    st.markdown("### 🎯 Master Comprehensive Academy Quiz")
    st.write("Answer the foundational multi-variable question below based on the 8 core modules above to graduate the track.")
    
    quiz_choice = st.radio(
        "Based on the curriculum guidelines, which option outlines the ideal path for a student with $1,000 in a credit card balance (24% interest), an un-diversified portfolio, and no emergency reserves?",
        [
            "Ignore the credit card balance, maximize exposure to one high-volatility stock, and open a traditional checking account.",
            "Use available cash to immediately pay off the 24% credit card balance (high-cost debt), build a 3-6 month cash emergency fund in a HYSA, and then invest long-term cash into diversified Index Funds.",
            "Keep all assets liquid inside a safe at home to avoid inflation effects entirely, and pay only the minimum balance required on the credit card statement."
        ]
    )
    
    if st.button("Submit Comprehensive Assessment Summary", use_container_width=True):
        if "immediately pay off" in quiz_choice:
            st.success("🎉 Exceptional! You have accurately synchronized all 8 foundational courses. +100 XP added directly to your profile database!")
            try:
                supabase.table("profiles").update({"points": current_points + 100}).eq("username", username).execute()
                st.rerun()
            except Exception: pass
        else:
            st.error("❌ Evaluation misalignment. Review the high-cost debt clearance parameters and broad diversification rules above before resubmitting.")

def show_budgeting(username):
    st.markdown("## 📉 Budgeting Tracker")
    col1, col2 = st.columns([1, 1.5])
    with col1:
        with st.form("exp_form", clear_on_submit=True):
            cat = st.selectbox("Category", ["Food", "Academic", "Housing", "Leisure", "Investment"])
            amt = st.number_input("Amount ($)", min_value=1.0)
            if st.form_submit_button("Log Expense"):
                supabase.table("expenses").insert({"username": username, "category": cat, "amount": amt}).execute()
                st.rerun()
    with col2:
        res = supabase.table("expenses").select("amount").eq("username", username).execute()
        total = sum([float(i['amount']) for i in res.data])
        st.progress(min(total/1000, 1.0), text=f"Monthly Spend: ${total} / $1000")

def show_savings():
    st.markdown("## 🐷 Savings Accelerator")
    st.write("Calculate your timeline to freedom.")
    target = st.number_input("Target Goal ($)", value=5000)
    monthly = st.number_input("Monthly Contribution ($)", value=200)
    st.info(f"You will hit your goal in **{round(target/monthly, 1)} months**.")

def show_splitting():
    st.markdown("## 👥 Friends Splitting Matrix")
    bill = st.number_input("Total Bill ($)", value=100.0)
    people = st.slider("Number of People", 2, 10, 3)
    st.success(f"Each person owes: **${round(bill/people, 2)}**")

# --- APP NAVIGATION HUB ---
if st.session_state.username is None:
    login_page()
else:
    profile = fetch_user_profile(st.session_state.username)
    
    # Custom Sidebar Navigation layout (No round check-boxes)
    with st.sidebar:
        st.title("FinSmart Nav")
        st.markdown(f"**User:** {st.session_state.username.upper()}")
        user_points = profile['points'] if profile else 0
        st.markdown(f"**XP:** 🏅 {user_points}")
        st.markdown("---")
        
        st.markdown("#### Navigation Links")
        if st.button("📊 Personal Finance Desk"):
            st.session_state.nav_selection = "📊 Personal Finance Desk"
            st.rerun()
        if st.button("📚 Micro-Courses"):
            st.session_state.nav_selection = "📚 Micro-Courses"
            st.rerun()
        if st.button("📉 Budgeting Tracker"):
            st.session_state.nav_selection = "📉 Budgeting Tracker"
            st.rerun()
        if st.button("🐷 Savings Accelerator"):
            st.session_state.nav_selection = "🐷 Savings Accelerator"
            st.rerun()
        if st.button("👥 Friends Splitting Matrix"):
            st.session_state.nav_selection = "👥 Friends Splitting Matrix"
            st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.username = None
            st.session_state.nav_selection = "📊 Personal Finance Desk"
            st.rerun()

    # Route to page via saved session selection metrics
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
