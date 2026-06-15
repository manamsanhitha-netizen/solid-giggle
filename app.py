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

# --- RE-ENGINEERED COMPACT UI STYLING ---
st.set_page_config(page_title="FinSmart Academy", page_icon="💳", layout="wide")

st.markdown("""
    <style>
    /* Absolute Reset of Top Padding & Header Spacing to Fix Clipping */
    [data-testid="stHeader"] {background: transparent; height: 0rem;}
    div.block-container {padding-top: 0.5rem !important; padding-bottom: 0.5rem !important; padding-left: 1.5rem !important; padding-right: 1.5rem !important;}
    #root > div:nth-child(1) > div > div > div {padding-top: 0px !important;}
    
    /* Compact Card Layouts to Drop Negative Space */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 10px 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        margin-bottom: 8px;
    }
    .stLessonCard {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e5e7eb;
        margin-bottom: 10px;
    }
    
    /* Low-Padding Navigation Deck */
    div.stButton > button:first-child {
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100%;
        border: 1px solid #e5e7eb;
        background-color: #ffffff;
        padding: 6px 10px;
        font-size: 13px;
        border-radius: 5px;
        margin-bottom: 2px;
    }
    div.stButton > button:first-child:hover {
        border-color: #4A90E2;
        color: #4A90E2;
        background-color: #f0f7ff;
    }
    
    /* Collapse Blank Spacers Globally */
    [data-testid="stVerticalBlock"] {gap: 0.4rem !important;}
    .element-container {margin-bottom: 0rem !important;}
    h1, h2, h3, h4 {margin-top: 0px !important; margin-bottom: 4px !important; padding: 0px !important;}
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
    st.markdown("<h3 style='text-align: center; color: #4A90E2;'>🎓 FinSmart Academy</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; font-size:13px; margin-bottom: 15px;'>Simple Financial Tools for Students</p>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1.5, 1.2, 1.5])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Login", "📝 Create Account"])
        with tab1:
            with st.form("login_form"):
                user_input = st.text_input("Username", placeholder="e.g. rahul_123").strip().lower()
                pass_input = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Log In", use_container_width=True):
                    profile = fetch_user_profile(user_input)
                    if profile and profile['password_hash'] == hash_password(pass_input):
                        st.session_state.username = user_input
                        st.rerun()
                    else:
                        st.error("Incorrect username or password.")
        with tab2:
            with st.form("reg_form"):
                new_user = st.text_input("Choose Username").strip().lower()
                new_pass = st.text_input("Choose Password", type="password")
                occ = st.selectbox("I am a:", ["Undergraduate", "Freelancer", "High School Student", "Self-Employed"])
                if st.form_submit_button("Sign Up", use_container_width=True):
                    if new_user and new_pass:
                        try:
                            supabase.table("profiles").insert({
                                "username": new_user, "password_hash": hash_password(new_pass),
                                "age": 19, "occupation": occ, "points": 0
                            }).execute()
                            st.success("Account created! Please log in above.")
                        except APIError: st.error("Username is already taken.")

# --- WORKSPACE PANELS ---

def show_finance_desk(profile, username):
    left_panel, right_panel = st.columns([1.8, 1.2])
    
    with left_panel:
        st.markdown("### 📊 My Financial Dashboard")
        
        standing = profile['occupation'] if profile else "Student"
        points = profile['points'] if profile else 0
        level = "Beginner Saver" if points < 150 else "Smart Investor" if points < 400 else "Money Master"

        st.markdown(f"""
        <div class="metric-card">
            <table style="width:100%; border:none; margin:0; line-height: 1.2;">
                <tr><td style="padding:2px; font-size:13px; color:#6b7280;">Profile Type:</td><td style="padding:2px; font-size:13px; font-weight:600; text-align:right;">{standing}</td></tr>
                <tr><td style="padding:2px; font-size:13px; color:#6b7280;">Learning Points:</td><td style="padding:2px; font-size:13px; font-weight:600; text-align:right; color:#4A90E2;">🏅 {points} XP</td></tr>
                <tr><td style="padding:2px; font-size:13px; color:#6b7280;">Academy Rank:</td><td style="padding:2px; font-size:13px; font-weight:600; text-align:right; color:#10b981;">{level}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("##### ⚡ Quick Expense Logger")
        with st.form("quick_log_form", clear_on_submit=True):
            q_col1, q_col2, q_col3 = st.columns([1.6, 1, 1])
            with q_col1: q_cat = st.selectbox("Category", ["Food", "Education", "Rent/Housing", "Entertainment", "Investments"], key="q_cat")
            with q_col2: q_amt = st.number_input("Amount (₹)", min_value=1.0, value=100.0, step=10.0, key="q_amt")
            with q_col3: q_sub = st.form_submit_button("Add Expense", use_container_width=True)
            if q_sub:
                supabase.table("expenses").insert({"username": username, "category": q_cat, "amount": q_amt}).execute()
                st.toast("Expense added!", icon="✅")
                st.rerun()

    with right_panel:
        res = supabase.table("expenses").select("*").eq("username", username).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['amount'] = df['amount'].astype(float)
            fig = px.pie(df, values='amount', names='category', hole=0.6, color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(height=140, margin=dict(t=5, b=5, l=5, r=5), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div style='height:130px; display:flex; align-items:center; justify-content:center; background:#f3f4f6; border-radius:8px; color:gray; font-size:12px;'>No expenses logged yet.</div>", unsafe_allow_html=True)

def show_micro_courses(profile, username):
    courses = [
        "Course 1: The Power of Compounding",
        "Course 2: Simple Budgeting Rules (50/30/20)",
        "Course 3: How Credit Scores Work",
        "Course 4: Index Funds & Passive Investing",
        "Course 5: Building an Emergency Fund",
        "Course 6: Freelancer & Side-Hustle Taxes",
        "Course 7: Understanding Inflation",
        "Course 8: Good Debt vs. Bad Debt"
    ]
    
    h_col1, h_col2 = st.columns([1.8, 2.2])
    with h_col1: st.markdown("### 📚 Finance Courses")
    with h_col2:
        sel_course = st.selectbox("Topic", courses, index=st.session_state.course_idx, label_visibility="collapsed")
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
    st.progress(current_step / total_steps, text=f"Progress: {int((current_step/total_steps)*100)}% (Page {current_step}/{total_steps})")
    
    st.markdown(f"<div class='stLessonCard'><span style='color:#4A90E2; font-weight:600; font-size:11px;'>PAGE {p_idx} OF 4</span>", unsafe_allow_html=True)

    if c_idx == 0:
        if p_idx == 1:
            st.markdown("#### Course 1: The Basics of Compounding")
            st.write("Compounding is simply earning interest on top of interest. When you reinvest the returns your money makes, your portfolio begins to grow exponentially faster over time.")
        elif p_idx == 2:
            st.markdown("#### Course 1: The Rule of 72")
            st.write("Divide 72 by your expected yearly interest rate to find out how quickly your principal investment balances will double.")
            st.latex(r"Years\ to\ Double = \frac{72}{Interest\ Rate}")
        elif p_idx == 3:
            st.markdown("#### Course 1: The Formula")
            st.write("The fundamental exponential mathematical curve governing financial markets:")
            st.latex(r"A = P\left(1 + \frac{r}{n}\right)^{nt}")
        elif p_idx == 4:
            st.markdown("#### 🎯 Course 1 Quiz")
            ans = st.radio("If you invest ₹1,000 at a 10% interest rate, how much money do you have after 2 years?", ["₹1,200.00", "₹1,210.00", "₹1,100.00"])
            if st.button("Submit Quiz Answer"):
                if ans == "₹1,210.00": st.success("Correct! +25 XP."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()
                else: st.error("Incorrect. Remember, the second year's interest builds on top of your year one balance (₹1,100).")

    elif c_idx == 1:
        if p_idx == 1:
            st.markdown("#### Course 2: The 50/30/20 Budget Rule")
            st.write("The 50/30/20 rule is a simple guide to split your take-home check cleanly into three functional categories without feeling restricted.")
        elif p_idx == 2:
            st.markdown("#### Course 2: Needs vs. Wants")
            st.write("Allocate **50%** of your money to **Needs** (rent, bills, groceries) and **30%** to **Wants** (eating out, movies, shopping).")
        elif p_idx == 3:
            st.markdown("#### Course 2: Saving for Tomorrow")
            st.write("The remaining **20%** must go directly into savings, emergency funds, or investments to grow your future net worth.")
        elif p_idx == 4:
            st.markdown("#### 🎯 Course 2 Quiz")
            ans = st.radio("Where does a Netflix subscription fit in a 50/30/20 budget?", ["Needs (50%)", "Wants (30%)", "Savings (20%)"])
            if st.button("Submit Quiz Answer"):
                if ans == "Wants (30%)": st.success("Correct! +25 XP."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    else:
        if p_idx < 4:
            st.markdown(f"#### {courses[c_idx]} (Section {p_idx})")
            st.write("This lesson covers essential topics on how to properly distribute your savings, minimize investment risks, and build long-term wealth step-by-step.")
        else:
            st.markdown("#### 🎯 Course Quiz")
            ans = st.radio("What is the recommended path to build personal wealth safely?", ["Keep all savings in cash at home", "Pay off expensive debts first, save an emergency fund, and invest in diversified index funds", "Buy high-risk single stocks with short-term money"])
            if st.button("Submit Quiz Answer"):
                if "Pay off expensive debts" in ans: st.success("Correct! +25 XP."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    nav_col1, _, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if p_idx > 1:
            if st.button("⬅️ Previous", use_container_width=True): st.session_state.page_idx -= 1; st.rerun()
    with nav_col3:
        if p_idx < 4:
            if st.button("Next ➡️", use_container_width=True): st.session_state.page_idx += 1; st.rerun()

def show_budgeting(username):
    st.markdown("### 📉 Budget Tracker")
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        with st.form("exp_form", clear_on_submit=True):
            cat = st.selectbox("Category", ["Food", "Education", "Rent/Housing", "Entertainment", "Investments"])
            amt = st.number_input("Amount (₹)", min_value=1.0, value=500.0, step=50.0)
            if st.form_submit_button("Save Expense", use_container_width=True):
                supabase.table("expenses").insert({"username": username, "category": cat, "amount": amt}).execute()
                st.rerun()
    with col2:
        res = supabase.table("expenses").select("amount").eq("username", username).execute()
        total = sum([float(i['amount']) for i in res.data])
        
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:12px; color:gray;">Monthly Budget Status</span><br/>
            <span style="font-size:18px; font-weight:700; color:#4A90E2;">₹{total:.2f} Used / ₹25,000 Target</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(total/25000, 1.0))

def show_savings():
    st.markdown("### 🐷 Savings & Fixed Deposit (FD) Calculator")
    col1, col2 = st.columns([1.3, 1.7])
    with col1:
        principal = st.number_input("Investment Amount (₹)", min_value=1000, value=10000, step=1000)
        tenure = st.slider("Time Period (Years)", 1, 10, 3)
    with col2:
        sav_rate, fd_rate = 0.035, 0.071
        sav_final = principal * ((1 + sav_rate) ** tenure)
        fd_final = principal * ((1 + fd_rate) ** tenure)
        difference = fd_final - sav_final
        
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:11px; color:gray; font-weight:bold;">GROWTH MATRIX</span>
            <hr style="margin:4px 0; border-color:#eee;"/>
            <div style="display:flex; justify-content:between; font-size:12px; margin:2px 0;">
                <span>Savings Account (~3.5%):</span>
                <span style="margin-left:auto; font-weight:600;">₹{sav_final:.2f}</span>
            </div>
            <div style="display:flex; justify-content:between; font-size:12px; margin:2px 0; color:#10b981;">
                <span>Fixed Deposit (~7.1%):</span>
                <span style="margin-left:auto; font-weight:600;">₹{fd_final:.2f}</span>
            </div>
            <hr style="margin:4px 0; border-color:#eee;"/>
            <span style="font-size:11px; color:#4A90E2; font-weight:700;">💡 Tip: FDs earn you ₹{difference:.2f} more than a plain savings account.</span>
        </div>
        """, unsafe_allow_html=True)

def show_splitting():
    st.markdown("### 👥 Bill Splitter & UPI Generator")
    col1, col2 = st.columns([1.4, 1.6])
    with col1:
        bill = st.number_input("Total Bill Amount (₹)", value=1500.0, step=100.0)
        people = st.slider("Split Between", 2, 12, 3)
        vpa = st.text_input("Your UPI ID (Optional)", placeholder="example@upi").strip()
    with col2:
        per_person = round(bill/people, 2) if people > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:12px; border-left: 5px solid #10b981;">
            <span style="font-size:12px; color:gray;">EACH PERSON OWES:</span><br/>
            <span style="font-size:26px; font-weight:800; color:#111827;">₹{per_person:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if vpa:
            upi_link = f"upi://pay?pa={vpa}&pn=FinSmart&am={per_person}&cu=INR"
            st.code(upi_link, language="markdown")

# --- CORE APPLICATION MASTER SKELETON ---
if st.session_state.username is None:
    login_page()
else:
    profile = fetch_user_profile(st.session_state.username)
    
    with st.sidebar:
        st.markdown("<h3 style='color:#4A90E2; margin-bottom:0;'>💳 FinSmart</h3>", unsafe_allow_html=True)
        st.caption(f"Operator: {st.session_state.username.upper()}")
        
        user_points = profile['points'] if profile else 0
        st.markdown(f"🏆 Balance: **{user_points} XP**")
        st.markdown("<hr style='margin: 4px 0;'/>", unsafe_allow_html=True)
        
        if st.sidebar.button("📊 Dashboard"): st.session_state.nav_selection = "📊 Dashboard"; st.rerun()
        if st.sidebar.button("📚 Micro-Courses"): st.session_state.nav_selection = "📚 Micro-Courses"; st.rerun()
        if st.sidebar.button("📉 Expense Tracker"): st.session_state.nav_selection = "📉 Expense Tracker"; st.rerun()
        if st.sidebar.button("🐷 Savings Calculator"): st.session_state.nav_selection = "🐷 Savings Calculator"; st.rerun()
        if st.sidebar.button("👥 Split Bills"): st.session_state.nav_selection = "👥 Split Bills"; st.rerun()
        
        st.markdown("<hr style='margin: 8px 0;'/>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Log Out"):
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
