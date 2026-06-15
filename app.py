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
    
    /* Typography & Font Formatting Adjustments */
    p, span, label, .stMarkdown {
        font-size: 15.5px !important; 
        line-height: 1.6 !important;
    }
    .main-header {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #1e293b;
    }
    .section-header {
        font-size: 20px !important;
        font-weight: 600 !important;
        color: #334155;
        margin-top: 5px !important;
    }
    
    /* Premium Dashboard Component Layouts */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .stLessonCard {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        margin-bottom: 12px;
    }
    
    /* Low-Padding Navigation Sidebar */
    div.stButton > button:first-child {
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100%;
        border: 1px solid #e2e8f0;
        background-color: #ffffff;
        padding: 10px 14px;
        font-size: 14px;
        font-weight: 500;
        border-radius: 6px;
        margin-bottom: 4px;
        color: #475569;
    }
    div.stButton > button:first-child:hover {
        border-color: #4A90E2;
        color: #4A90E2;
        background-color: #f0f7ff;
    }
    
    /* Collapse Blank Spacers Globally */
    [data-testid="stVerticalBlock"] {gap: 0.5rem !important;}
    .element-container {margin-bottom: 0rem !important;}
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
    st.markdown("<p class='main-header' style='text-align: center; color: #4A90E2;'>🎓 FinSmart Academy</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size:15px; margin-top: -10px; margin-bottom: 20px;'>Simple Financial Tools for Students</p>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1.4, 1.2, 1.4])
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
    left_panel, right_panel = st.columns([1.7, 1.3])
    
    with left_panel:
        st.markdown("<p class='section-header'>📊 My Financial Dashboard</p>", unsafe_allow_html=True)
        
        standing = profile['occupation'] if profile else "Student"
        points = profile['points'] if profile else 0
        level = "Beginner Saver" if points < 150 else "Smart Investor" if points < 400 else "Money Master"

        st.markdown(f"""
        <div class="metric-card">
            <table style="width:100%; border:none; margin:0; line-height: 1.5;">
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b;">Profile Type:</td><td style="padding:4px; font-size:14.5px; font-weight:600; text-align:right; color:#1e293b;">{standing}</td></tr>
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b;">Learning Points:</td><td style="padding:4px; font-size:14.5px; font-weight:600; text-align:right; color:#4A90E2;">🏅 {points} XP</td></tr>
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b;">Academy Rank:</td><td style="padding:4px; font-size:14.5px; font-weight:600; text-align:right; color:#10b981;">{level}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("##### ⚡ Quick Expense Logger")
        with st.form("quick_log_form", clear_on_submit=True):
            q_col1, q_col2, q_col3 = st.columns([1.5, 1.1, 1.1])
            with q_col1: q_cat = st.selectbox("Category", ["Food", "Education", "Rent/Housing", "Entertainment", "Investments"], key="q_cat")
            with q_col2: q_amt = st.number_input("Amount (₹)", min_value=1.0, value=100.0, step=10.0, key="q_amt")
            with q_col3: 
                st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
                q_sub = st.form_submit_button("Add Expense", use_container_width=True)
            if q_sub:
                supabase.table("expenses").insert({"username": username, "category": q_cat, "amount": q_amt}).execute()
                st.toast("Expense added!", icon="✅")
                st.rerun()

    with right_panel:
        res = supabase.table("expenses").select("*").eq("username", username).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['amount'] = df['amount'].astype(float)
            fig = px.pie(df, values='amount', names='category', hole=0.55, color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(height=190, margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div style='height:160px; display:flex; align-items:center; justify-content:center; background:#f8fafc; border: 1px dashed #cbd5e1; border-radius:10px; color:#64748b; font-size:14px; margin-top:35px;'>No expenses logged yet. Add your first transaction on the left panel!</div>", unsafe_allow_html=True)

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
    with h_col1: st.markdown("<p class='section-header'>📚 Academy Finance Lessons</p>", unsafe_allow_html=True)
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
    st.progress(current_step / total_steps, text=f"Overall Course Progress: {int((current_step/total_steps)*100)}% Completed (Page {current_step}/{total_steps})")
    
    st.markdown(f"<div class='stLessonCard'><span style='color:#4A90E2; font-weight:700; font-size:12px; letter-spacing:0.5px;'>PAGE {p_idx} OF 4</span>", unsafe_allow_html=True)

    if c_idx == 0:
        if p_idx == 1:
            st.markdown("#### Course 1: The Basics of Compounding")
            st.write("Compounding is simply earning interest on top of interest. When you reinvest the returns your money makes instead of spending them, your overall investment balance begins to grow exponentially faster over time.")
        elif p_idx == 2:
            st.markdown("#### Course 1: The Rule of 72")
            st.write("Divide **72** by your expected yearly interest rate to find out exactly how quickly your investment balance will take to double itself.")
            st.latex(r"Years\ to\ Double = \frac{72}{Interest\ Rate}")
        elif p_idx == 3:
            st.markdown("#### Course 1: The Formula")
            st.write("The fundamental exponential balance equation governing traditional asset markets and calculation models:")
            st.latex(r"A = P\left(1 + \frac{r}{n}\right)^{nt}")
        elif p_idx == 4:
            st.markdown("#### 🎯 Course 1 Quiz")
            ans = st.radio("If you invest ₹1,000 at a 10% interest rate compounding annually, how much money do you have after 2 years?", ["An exact choice of ₹1,200.00", "An exact choice of ₹1,210.00", "An exact choice of ₹1,100.00"])
            if st.button("Submit Quiz Answer"):
                if "₹1,210.00" in ans: st.success("Correct! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()
                else: st.error("Incorrect. Remember, the second year's interest builds on top of your year one balance (₹1,100).")

    elif c_idx == 1:
        if p_idx == 1:
            st.markdown("#### Course 2: The 50/30/20 Budget Rule")
            st.write("The 50/30/20 rule is a simple guide to split your take-home check cleanly into three functional categories without feeling restricted or dealing with deep accounting burnouts.")
        elif p_idx == 2:
            st.markdown("#### Course 2: Needs vs. Wants")
            st.write("Allocate **50%** of your net income to mandatory **Needs** (rent, utility bills, core groceries) and **30%** to personal **Wants** (eating out, movies, lifestyle shopping).")
        elif p_idx == 3:
            st.markdown("#### Course 2: Saving for Tomorrow")
            st.write("The remaining **20%** must go directly into high-yield savings accounts, emergency funds, or liquid equity markets to grow your future net worth.")
        elif p_idx == 4:
            st.markdown("#### 🎯 Course 2 Quiz")
            ans = st.radio("Where does a monthly premium Netflix subscription fit in a balanced 50/30/20 budget architecture?", ["Needs (50%)", "Wants (30%)", "Savings (20%)"])
            if st.button("Submit Quiz Answer"):
                if ans == "Wants (30%)": st.success("Correct! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

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
            if st.button("Next Screen ➡️", use_container_width=True): st.session_state.page_idx += 1; st.rerun()

def show_budgeting(username):
    st.markdown("<p class='section-header'>📉 Expense & Budget Tracker</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        with st.form("exp_form", clear_on_submit=True):
            cat = st.selectbox("Category", ["Food", "Education", "Rent/Housing", "Entertainment", "Investments"])
            amt = st.number_input("Amount (₹)", min_value=1.0, value=500.0, step=50.0)
            if st.form_submit_button("Save Expense Entry", use_container_width=True):
                supabase.table("expenses").insert({"username": username, "category": cat, "amount": amt}).execute()
                st.rerun()
    with col2:
        res = supabase.table("expenses").select("amount").eq("username", username).execute()
        total = sum([float(i['amount']) for i in res.data])
        
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 15px;">
            <span style="font-size:13px; color:#64748b; font-weight: 500;">MONTHLY BUDGET USAGE FRAMEWORK</span><br/>
            <span style="font-size:22px; font-weight:700; color:#4A90E2;">₹{total:.2f} Used / ₹25,000 Target Limit</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(total/25000, 1.0))

def show_savings():
    st.markdown("<p class='section-header'>🐷 Savings & Fixed Deposit (FD) Yields</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.3, 1.7])
    with col1:
        principal = st.number_input("Investment Principal (₹)", min_value=1000, value=10000, step=1000)
        tenure = st.slider("Time Period Horizons (Years)", 1, 10, 3)
    with col2:
        sav_rate, fd_rate = 0.035, 0.071
        sav_final = principal * ((1 + sav_rate) ** tenure)
        fd_final = principal * ((1 + fd_rate) ** tenure)
        difference = fd_final - sav_final
        
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:12px; color:#64748b; font-weight:700; letter-spacing:0.5px;">GROWTH PROJECTION VIEW</span>
            <hr style="margin:8px 0; border-color:#e2e8f0;"/>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:6px 0;">
                <span style="color:#475569;">Normal Savings Balance (~3.5% Return):</span>
                <span style="margin-left:auto; font-weight:600; color:#1e293b;">₹{sav_final:.2f}</span>
            </div>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:6px 0; color:#10b981;">
                <span style="font-weight: 500;">Fixed Deposit Bank Value (~7.1% Return):</span>
                <span style="margin-left:auto; font-weight:700;">₹{fd_final:.2f}</span>
            </div>
            <hr style="margin:8px 0; border-color:#e2e8f0;"/>
            <span style="font-size:13px; color:#4A90E2; font-weight:600;">💡 Alpha Yield Opportunity: Choosing a fixed tenure deposit generates ₹{difference:.2f} more than leaving cash liquid!</span>
        </div>
        """, unsafe_allow_html=True)

def show_splitting():
    st.markdown("<p class='section-header'>👥 Bill Splitter & Shareable UPI Strings</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.4, 1.6])
    with col1:
        bill = st.number_input("Total Shared Bill Amount (₹)", value=1500.0, step=100.0)
        people = st.slider("Split Count (Number of Friends)", 2, 12, 3)
        vpa = st.text_input("Your UPI ID String (Optional)", placeholder="example@okhdfcbank").strip()
    with col2:
        per_person = round(bill/people, 2) if people > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:18px 16px; border-left: 6px solid #10b981; margin-top: 10px;">
            <span style="font-size:14px; color:#64748b; font-weight:500;">INDIVIDUAL SHARED LIABILITY:</span><br/>
            <span style="font-size:36px; font-weight:800; color:#0f172a;">₹{per_person:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if vpa:
            st.markdown("<span style='font-size:13px; color:#64748b; font-weight:600;'>MESSENGER REQUEST LINK STRING:</span>", unsafe_allow_html=True)
            upi_link = f"upi://pay?pa={vpa}&pn=FinSmart&am={per_person}&cu=INR"
            st.code(upi_link, language="markdown")

# --- CORE APPLICATION MASTER SKELETON ---
if st.session_state.username is None:
    login_page()
else:
    profile = fetch_user_profile(st.session_state.username)
    
    with st.sidebar:
        st.markdown("<p class='main-header' style='color:#4A90E2; font-size: 24px !important;'>💳 FinSmart</p>", unsafe_allow_html=True)
        st.caption(f"Operator Account: {st.session_state.username.upper()}")
        
        user_points = profile['points'] if profile else 0
        st.markdown(f"🏆 Profile Reward Balance: **{user_points} XP**")
        st.markdown("<hr style='margin: 8px 0; border-color:#e2e8f0;'/>", unsafe_allow_html=True)
        
        if st.sidebar.button("📊 Dashboard Hub"): st.session_state.nav_selection = "📊 Dashboard"; st.rerun()
        if st.sidebar.button("📚 Micro-Courses"): st.session_state.nav_selection = "📚 Micro-Courses"; st.rerun()
        if st.sidebar.button("📉 Expense Tracker"): st.session_state.nav_selection = "📉 Expense Tracker"; st.rerun()
        if st.sidebar.button("🐷 Savings Calculator"): st.session_state.nav_selection = "🐷 Savings Calculator"; st.rerun()
        if st.sidebar.button("👥 Split Bills"): st.session_state.nav_selection = "👥 Split Bills"; st.rerun()
        
        st.markdown("<hr style='margin: 12px 0; border-color:#e2e8f0;'/>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Terminate Session"):
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
