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
        margin-bottom: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #eee;
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

if "username" not in st.session_state:
    st.session_state.username = None

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
    
    # KPI metrics
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Current Standing", profile['occupation'])
    with m2: st.metric("Platform XP", f"🏅 {profile['points']}")
    with m3: st.metric("Level", "Beginner" if profile['points'] < 100 else "Intermediate")

    st.markdown("---")
    res = supabase.table("expenses").select("*").eq("username", username).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df['amount'] = df['amount'].astype(float)
        fig = px.pie(df, values='amount', names='category', hole=0.5, title="Expense Allocation")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet. Log expenses in the 'Budgeting Tracker'.")

def show_micro_courses(profile, username):
    st.markdown("## 📚 Financial Intelligence Academy")
    st.caption("Complete interactive modules to master your money and earn +25 XP per quiz.")
    
    course_list = {
        "1. Velocity of Compounding": "Learn how time turns small savings into massive assets.",
        "2. The 50/30/20 Rule": "Master the ultimate budgeting framework for students.",
        "3. Credit Score Secrets": "How to build institutional trust before you graduate.",
        "4. Index Funds & ETFs": "Investing in the whole market vs picking stocks.",
        "5. The Emergency Fund": "Building a 3-6 month cash safety net.",
        "6. Taxes for Side-Hustles": "Navigating 1099 and self-employment taxes."
    }
    
    selected_course = st.selectbox("Select a Learning Module", list(course_list.keys()))
    st.markdown(f"<div class='stLessonCard'>", unsafe_allow_html=True)
    
    if "1." in selected_course:
        st.markdown("### 📈 Compounding Logic")
        st.write("Interest on interest. It converts linear growth into parabolic wealth.")
        st.latex(r"A = P(1 + r/n)^{nt}")
        ans = st.radio("Year 1: $100 + 10% = $110. What is the value after Year 2?", ["$120", "$121", "$111"])
        if st.button("Submit Quiz"): 
            if ans == "$121": st.success("Correct! +25 XP"); supabase.table("profiles").update({"points": profile['points']+25}).eq("username", username).execute()
            else: st.error("Incorrect. Remember the 10% applies to the $110, not the $100.")

    elif "2." in selected_course:
        st.markdown("### 🎛️ 50/30/20 Framework")
        st.write("50% Needs, 30% Wants, 20% Savings/Debt.")
        ans = st.radio("A new Netflix subscription falls under which category?", ["Needs", "Wants", "Savings"])
        if st.button("Submit Quiz"): 
            if ans == "Wants": st.success("Correct! +25 XP"); supabase.table("profiles").update({"points": profile['points']+25}).eq("username", username).execute()

    elif "3." in selected_course:
        st.markdown("### 💳 Credit Mastery")
        st.write("Credit utilization (how much of your limit you use) should stay under 30%.")
        ans = st.radio("What is the biggest factor in your credit score?", ["Payment History", "Total Income", "Number of Cards"])
        if st.button("Submit Quiz"): 
            if ans == "Payment History": st.success("Correct! +25 XP"); supabase.table("profiles").update({"points": profile['points']+25}).eq("username", username).execute()

    elif "4." in selected_course:
        st.markdown("### 🏛️ Index Funds & ETFs")
        st.write("Instead of buying one stock like Apple, you buy a 'basket' of the 500 biggest companies (S&P 500). This lowers risk.")
        st.info("💡 **Key Fact:** Over 90% of professional stock pickers fail to beat a simple S&P 500 Index Fund over 10 years.")
        ans = st.radio("What is a major benefit of an Index ETF?", ["Instant Diversification", "Guaranteed 100% returns", "No risk of losing money"])
        if st.button("Submit Quiz"):
            if ans == "Instant Diversification": st.success("Correct! +25 XP"); supabase.table("profiles").update({"points": profile['points']+25}).eq("username", username).execute()

    elif "5." in selected_course:
        st.markdown("### 🛡️ The Emergency Fund")
        st.write("Before investing, you need cash to cover 'Broken Phone' or 'Car Repair' moments. The goal is 3-6 months of basic living expenses.")
        ans = st.radio("Where should an Emergency Fund be kept?", ["Crypto Wallet", "High-Yield Savings Account", "In a safe at home"])
        if st.button("Submit Quiz"):
            if ans == "High-Yield Savings Account": st.success("Correct! +25 XP"); supabase.table("profiles").update({"points": profile['points']+25}).eq("username", username).execute()

    elif "6." in selected_course:
        st.markdown("### 🧾 Taxes for Side-Hustles")
        st.write("If you earn over $400 via freelancing (DoorDash, Upwork, Etsy), you are a business owner in the eyes of the IRS.")
        st.warning("⚠️ You must set aside roughly 25-30% of your earnings for taxes, as no boss is withholding them for you.")
        ans = st.radio("What tax form do freelancers usually receive?", ["W-2", "1099-NEC", "1040-EZ"])
        if st.button("Submit Quiz"):
            if ans == "1099-NEC": st.success("Correct! +25 XP"); supabase.table("profiles").update({"points": profile['points']+25}).eq("username", username).execute()

    st.markdown("</div>", unsafe_allow_html=True)

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

# --- APP NAVIGATION ---
if st.session_state.username is None:
    login_page()
else:
    profile = fetch_user_profile(st.session_state.username)
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("FinSmart Nav")
        st.markdown(f"**User:** {st.session_state.username.upper()}")
        st.markdown(f"**XP:** 🏅 {profile['points']}")
        st.markdown("---")
        
        nav = st.radio("Go To:", [
            "📊 Personal Finance Desk",
            "📚 Micro-Courses",
            "📉 Budgeting Tracker",
            "🐷 Savings Accelerator",
            "👥 Friends Splitting Matrix"
        ])
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.username = None
            st.rerun()

    # Page Routing
    if nav == "📊 Personal Finance Desk": show_finance_desk(profile, st.session_state.username)
    elif nav == "📚 Micro-Courses": show_micro_courses(profile, st.session_state.username)
    elif nav == "📉 Budgeting Tracker": show_budgeting(st.session_state.username)
    elif nav == "🐷 Savings Accelerator": show_savings()
    elif nav == "👥 Friends Splitting Matrix": show_splitting()
