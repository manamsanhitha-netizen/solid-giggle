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
st.set_page_config(page_title="Finora | Student Finance Hub", page_icon="💳", layout="wide")

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
    st.markdown("<p class='main-header' style='text-align: center; color: #4A90E2;'>🎓 Finora Academy</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size:15px; margin-top: -10px; margin-bottom: 20px;'>Simple Financial Tools & Gamified Learning for Students</p>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1.4, 1.2, 1.4])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Secure Login", "📝 Create Finora Account"])
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
                new_user = st.text_input("Choose Unique Username").strip().lower()
                new_pass = st.text_input("Choose Strong Password", type="password")
                occ = st.selectbox("Current Track:", ["Undergraduate Student", "Freelancer", "High School Student", "Self-Employed / Founder"])
                if st.form_submit_button("Sign Up", use_container_width=True):
                    if new_user and new_pass:
                        try:
                            supabase.table("profiles").insert({
                                "username": new_user, "password_hash": hash_password(new_pass),
                                "age": 19, "occupation": occ, "points": 0
                            }).execute()
                            st.success("Finora account created! Please log in above.")
                        except APIError: st.error("Username is already taken.")

# --- WORKSPACE PANELS ---

def show_finance_desk(profile, username):
    st.markdown("<p class='section-header'>📊 Finora Analytics Control Panel</p>", unsafe_allow_html=True)
    left_panel, right_panel = st.columns([1.6, 1.4])
    
    res = supabase.table("expenses").select("*").eq("username", username).execute()
    total_spent = sum([float(i['amount']) for i in res.data]) if res.data else 0.0

    with left_panel:
        standing = profile['occupation'] if profile else "Student"
        points = profile['points'] if profile else 0
        level = "Beginner Saver" if points < 150 else "Smart Investor" if points < 400 else "Money Master"

        st.markdown(f"""
        <div class="metric-card">
            <table style="width:100%; border:none; margin:0; line-height: 1.5;">
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b;">Profile Track:</td><td style="padding:4px; font-size:14.5px; font-weight:600; text-align:right; color:#1e293b;">{standing}</td></tr>
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b;">Learning Points:</td><td style="padding:4px; font-size:14.5px; font-weight:600; text-align:right; color:#4A90E2;">🏅 {points} XP</td></tr>
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b;">Finora Ranking Rank:</td><td style="padding:4px; font-size:14.5px; font-weight:600; text-align:right; color:#10b981;">{level}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # FEATURE ADDITION: Dynamic Smart Cash Burn Predictor
        predicted_annual = total_spent * 12
        if predicted_annual > 0:
            status_color = "#ef4444" if predicted_annual > 150000 else "#10b981"
            status_text = "Aggressive Outflows" if predicted_annual > 150000 else "Sustainable Cash Run-Rate"
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {status_color};">
                <span style="font-size:12px; color:#64748b; font-weight:700;">📊 INTELLIGENT CASH BURN PREDICTOR</span><br/>
                <span style="font-size:14.5px;">Estimated Annual Outflow Rate: <b>₹{predicted_annual:,.2f}</b></span><br/>
                <span style="font-size:12.5px; color:{status_color}; font-weight:600;">System Alert Profile: {status_text}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("##### ⚡ Quick Expense Logger")
        with st.form("quick_log_form", clear_on_submit=True):
            q_col1, q_col2, q_col3 = st.columns([1.5, 1.1, 1.1])
            with q_col1: q_cat = st.selectbox("Category", ["Food & Dining", "Education & Books", "Rent & Bills", "Entertainment & Leisure", "Mutual Funds & SIPs"], key="q_cat")
            with q_col2: q_amt = st.number_input("Amount (₹)", min_value=1.0, value=100.0, step=10.0, key="q_amt")
            with q_col3: 
                st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
                q_sub = st.form_submit_button("Add Expense", use_container_width=True)
            if q_sub:
                supabase.table("expenses").insert({"username": username, "category": q_cat, "amount": q_amt}).execute()
                st.toast("Expense tracked successfully inside Finora!", icon="✅")
                st.rerun()

    with right_panel:
        if res.data:
            df = pd.DataFrame(res.data)
            df['amount'] = df['amount'].astype(float)
            fig = px.pie(df, values='amount', names='category', hole=0.55, color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(height=240, margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div style='height:210px; display:flex; align-items:center; justify-content:center; background:#f8fafc; border: 1px dashed #cbd5e1; border-radius:10px; color:#64748b; font-size:14px;'>No expenses logged yet. Add your first transaction on the left panel!</div>", unsafe_allow_html=True)

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
    with h_col1: st.markdown("<p class='section-header'>📚 Finora Interactive Academy</p>", unsafe_allow_html=True)
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
            ans = st.radio("If you invest ₹1,000 at a 10% interest rate compounding annually, how much money do you have after 2 years?", ["₹1,200.00", "₹1,210.00", "₹1,100.00"])
            if st.button("Submit Quiz Answer"):
                if ans == "₹1,210.00": st.success("Correct! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()
                else: st.error("Incorrect. Remember, the second year's interest builds on top of your year one balance (₹1,100).")

    elif c_idx == 4: # Mutual Funds
        if p_idx == 1:
            st.markdown("#### Course 5: Mutual Funds & Diversification")
            st.write("A Mutual Fund pools capital from thousands of retail investors to purchase a diversified portfolio of stock equities or bond vectors. This saves you from the danger of buying single individual stocks.")
        elif p_idx == 2:
            st.markdown("#### Course 5: The Power of a Systemic Investment Plan (SIP)")
            st.write("An SIP lets you invest a fixed amount (e.g., ₹500/month) automatically into a chosen mutual fund. This leverages **Rupee Cost Averaging**, meaning you naturally buy more fund units when prices are low and fewer when markets are overvalued.")
        elif p_idx == 3:
            st.markdown("#### Course 5: Expense Ratios & Direct vs Regular Funds")
            st.write("Always look at the **Expense Ratio** (the management fee charged by the fund). Direct funds bypass asset brokers, dropping fees lower and saving you lakhs over your investing lifespan.")
        elif p_idx == 4:
            st.markdown("#### 🎯 Course 5 Quiz")
            ans = st.radio("What strategy allows you to safely buy more mutual fund units when stock prices drop?", ["Market Timing Speculation", "Systematic Investment Plan (SIP) Averaging", "High Frequency Active Trading"])
            if st.button("Submit Quiz Answer"):
                if "SIP" in ans: st.success("Fantastic Analysis! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    elif c_idx == 7: # Credit Card Trap
        if p_idx == 1:
            st.markdown("#### Course 8: Understanding Credit Card Mechanics")
            st.write("Credit cards are excellent tools for building user scores, tracking safety holds, and getting cashback markers. However, they do not provide free capital. They are high-cost short term loans.")
        elif p_idx == 2:
            st.markdown("#### Course 8: The Toxic 'Minimum Balance Due' Mirage")
            st.write("Paying only the minimum amount due on your bill statement stops late fees, but allows banks to compound interest on your remaining debt at brutal interest rates of up to **36% to 45% annually**!")
        elif p_idx == 3:
            st.markdown("#### Course 8: Golden Rules of Cards")
            st.write("1. Treat your card precisely like a checkbook debit engine. If you do not have the money liquid inside your checking account right now, **do not swipe.**\n2. Set up automated auto-pay structures to clear the **Total Statement Balance** monthly.")
        elif p_idx == 4:
            st.markdown("#### 🎯 Course 8 Quiz")
            ans = st.radio("What happens if you clear only the 'Minimum Balance Due' on a standard card bill?", ["The rest of the balance is completely forgiven", "The bank compounds high interest rates (up to 40%+) on your remaining balance", "Your score spikes instantly"])
            if st.button("Submit Quiz Answer"):
                if "compounds high interest" in ans: st.success("Magnificent Execution! +25 XP."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    else:
        if p_idx < 4:
            st.markdown(f"#### {courses[c_idx]} (Section {p_idx})")
            st.write("This interactive Finora module covers essential frameworks on systematic savings pipelines, compliance criteria, tax mitigation avenues, and risk diversification profiles.")
        else:
            st.markdown("#### 🎯 Comprehensive Track Quiz")
            ans = st.radio("Identify the optimized framework to achieve financial independence:", ["Keep extra cash liquid in checking portfolios", "Pay down bad toxic card lines, build defensive cash cushions, and clear automated monthly investment targets", "Trade micro cap digital currencies on leverage margins"])
            if st.button("Submit Quiz Answer"):
                if "Pay down bad toxic" in ans: st.success("Correct! +25 XP."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    nav_col1, _, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if p_idx > 1:
            if st.button("⬅️ Previous Screen", use_container_width=True): st.session_state.page_idx -= 1; st.rerun()
    with nav_col3:
        if p_idx < 4:
            if st.button("Next Lesson ➡️", use_container_width=True): st.session_state.page_idx += 1; st.rerun()

def show_budgeting(username):
    st.markdown("<p class='section-header'>📉 Finora Budget Planner & Envelopes</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        with st.form("exp_form", clear_on_submit=True):
            cat = st.selectbox("Budget Allocation Group", ["Food & Dining", "Education & Books", "Rent & Bills", "Entertainment & Leisure", "Mutual Funds & SIPs"])
            amt = st.number_input("Transaction Value (₹)", min_value=1.0, value=500.0, step=50.0)
            if st.form_submit_button("Securely Record Outflow", use_container_width=True):
                supabase.table("expenses").insert({"username": username, "category": cat, "amount": amt}).execute()
                st.rerun()
    with col2:
        res = supabase.table("expenses").select("amount").eq("username", username).execute()
        total = sum([float(i['amount']) for i in res.data])
        
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 15px;">
            <span style="font-size:13px; color:#64748b; font-weight: 500;">MONTHLY TARGET CAPACITY METRIC</span><br/>
            <span style="font-size:22px; font-weight:700; color:#4A90E2;">₹{total:.2f} Transacted / ₹25,000 Target Threshold</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(total/25000, 1.0))

def show_savings():
    st.markdown("<p class='section-header'>🐷 Finora Savings Yield Engine</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        principal = st.number_input("Principal Deployment (₹)", min_value=1000, value=10000, step=1000)
        tenure = st.slider("Time Horizon Term (Years)", 1, 10, 3)
    with col2:
        sav_rate, fd_rate, inf_rate = 0.035, 0.071, 0.060
        sav_final = principal * ((1 + sav_rate) ** tenure)
        fd_final = principal * ((1 + fd_rate) ** tenure)
        
        # FEATURE ADDITION: Inflation Purchasing Power Loss Simulation
        purchasing_power = principal / ((1 + inf_rate) ** tenure)
        loss_value = principal - purchasing_power
        
        st.markdown(f"""
        <div class="metric-card">
            <span style="font-size:12px; color:#64748b; font-weight:700; letter-spacing:0.5px;">GROWTH PROJECTION VIEW</span>
            <hr style="margin:6px 0; border-color:#e2e8f0;"/>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:4px 0;">
                <span style="color:#475569;">Normal Savings Balance (~3.5% Return):</span>
                <span style="margin-left:auto; font-weight:600; color:#1e293b;">₹{sav_final:.2f}</span>
            </div>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:4px 0; color:#10b981;">
                <span style="font-weight: 500;">Fixed Deposit Bank Value (~7.1% Return):</span>
                <span style="margin-left:auto; font-weight:700;">₹{fd_final:.2f}</span>
            </div>
            <hr style="margin:6px 0; border-color:#e2e8f0;"/>
            <div style="display:flex; justify-content:between; font-size:14.5px; margin:4px 0; color:#ef4444;">
                <span>⚠️ Mattress Cash Value (Loss to ~6% Inflation):</span>
                <span style="margin-left:auto; font-weight:700;">-₹{loss_value:.2f} Buying Power</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_splitting():
    st.markdown("<p class='section-header'>👥 Finora Shared Bill Settlement Space</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.4, 1.6])
    with col1:
        bill = st.number_input("Total Shared Bill Amount (₹)", value=1500.0, step=100.0)
        people = st.slider("Split Count (Number of Friends)", 2, 12, 3)
        vpa = st.text_input("Your UPI Address VPA (e.g., name@okaxis)", placeholder="example@okhdfcbank").strip()
    with col2:
        per_person = round(bill/people, 2) if people > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:18px 16px; border-left: 6px solid #10b981; margin-top: 10px;">
            <span style="font-size:14px; color:#64748b; font-weight:500;">INDIVIDUAL SHARED LIABILITY:</span><br/>
            <span style="font-size:36px; font-weight:800; color:#0f172a;">₹{per_person:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if vpa:
            st.markdown("<span style='font-size:13px; color:#64748b; font-weight:600;'>⚡ DEEP-LINK UPI LINK FOR DIRECT CHAT SHARING:</span>", unsafe_allow_html=True)
            upi_link = f"upi://pay?pa={vpa}&pn=FinoraSplit&am={per_person}&cu=INR"
            st.code(upi_link, language="markdown")

# --- CORE APPLICATION MASTER SKELETON ---
if st.session_state.username is None:
    login_page()
else:
    profile = fetch_user_profile(st.session_state.username)
    
    with st.sidebar:
        st.markdown("<p class='main-header' style='color:#4A90E2; font-size: 26px !important;'>✨ Finora</p>", unsafe_allow_html=True)
        st.caption(f"Operator Profile: {st.session_state.username.upper()}")
        
        user_points = profile['points'] if profile else 0
        st.markdown(f"🏆 Rewards Bank: **{user_points} Finora XP**")
        st.markdown("<hr style='margin: 8px 0; border-color:#e2e8f0;'/>", unsafe_allow_html=True)
        
        if st.sidebar.button("📊 Analytics Dashboard"): st.session_state.nav_selection = "📊 Dashboard"; st.rerun()
        if st.sidebar.button("📚 Finora Academy"): st.session_state.nav_selection = "📚 Micro-Courses"; st.rerun()
        if st.sidebar.button("📉 Expense Envelopes"): st.session_state.nav_selection = "📉 Expense Tracker"; st.rerun()
        if st.sidebar.button("🐷 Savings Multiplier"): st.session_state.nav_selection = "🐷 Savings Calculator"; st.rerun()
        if st.sidebar.button("👥 Split Peer Expenses"): st.session_state.nav_selection = "👥 Split Bills"; st.rerun()
        
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
