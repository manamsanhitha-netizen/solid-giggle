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
    """Fetches conversion rates for students looking to study abroad"""
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
    """Fetches real-world digital token metrics in INR"""
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
    """Fetches a free daily wealth-mindset or motivational quote"""
    try:
        url = "https://zenquotes.io/api/today"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return f'"{data[0]["q"]}" — {data[0]["a"]}'
        return "Small daily savings compound into massive future freedom! ✨"
    except Exception:
        return "Small daily savings compound into massive future freedom! ✨"

# --- THE FINORA PREMIUM CLEAN UI THEME ---
st.set_page_config(page_title="Finora | Simple Student Wealth Hub", page_icon="💳", layout="wide")

st.markdown("""
    <style>
    /* Prevent Header Clipping & Drop Blank Space */
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
    
    /* Component Cards with Soft Gradients and Drop Shadows */
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
        padding: 10px 14px;
        background: #f8fafc;
        border-radius: 8px;
        margin-bottom: 6px;
        border-left: 4px solid #cbd5e1;
    }
    
    /* Interactive Sidebar Control Array */
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
    st.markdown("<div style='text-align: center; margin-bottom: 10px;'><span class='main-header'>✨Finora</span></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size:15px; margin-top: -12px; margin-bottom: 24px;'>Easy Money Tracking, Bill Splitting, and Simple Lessons for Students</p>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1.4, 1.2, 1.4])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Log In", "📝 Create Free Account"])
        with tab1:
            with st.form("login_form"):
                user_input = st.text_input("Username", placeholder="e.g. rahul_123").strip().lower()
                pass_input = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Open My Dashboard", use_container_width=True):
                    profile = fetch_user_profile(user_input)
                    if profile and profile['password_hash'] == hash_password(pass_input):
                        st.session_state.username = user_input
                        st.rerun()
                    else:
                        st.error("Incorrect username or password.")
        with tab2:
            with st.form("reg_form"):
                new_user = st.text_input("Pick a Username").strip().lower()
                new_pass = st.text_input("Pick a Strong Password", type="password")
                occ = st.selectbox("What do you do right now?", ["College Student", "Freelancer", "School Student", "Self-Employed / Founder"])
                if st.form_submit_button("Create My Account", use_container_width=True):
                    if new_user and new_pass:
                        try:
                            supabase.table("profiles").insert({
                                "username": new_user, "password_hash": hash_password(new_pass),
                                "age": 19, "occupation": occ, "points": 0
                            }).execute()
                            st.success("Account created! You can now log in using the first tab.")
                        except APIError: st.error("That username is already taken.")

# --- WORKSPACE PANELS ---
def show_finance_desk(profile, username):
    st.markdown("<p class='section-header'>📊 Your Financial Dashboard</p>", unsafe_allow_html=True)
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
            <h5 style="margin: 0 0 10px 0; color: #1e293b; font-weight:700;">Account Profile Summary</h5>
            <table style="width:100%; border:none; margin:0; line-height: 1.6;">
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b; font-weight:500;">Your Current Focus:</td><td style="padding:4px; font-size:14.5px; font-weight:700; text-align:right; color:#0f172a;">{standing}</td></tr>
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b; font-weight:500;">Lesson Score:</td><td style="padding:4px; font-size:14.5px; font-weight:700; text-align:right; color:#0284c7;">🏅 {points} XP Earned</td></tr>
                <tr><td style="padding:4px; font-size:14.5px; color:#64748b; font-weight:500;">Finora Badge Rank:</td><td style="padding:4px; font-size:14.5px; font-weight:700; text-align:right; color:#10b981;">{level}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # FINANCIAL HEALTH STATUS ALERT BOX
        rem_pct = max(((budget_max - total_spent) / budget_max) * 100, 0.0)
        health_color = "#10b981" if rem_pct > 40 else "#f59e0b" if rem_pct > 15 else "#ef4444"
        health_label = "Great Job! Your spending looks super healthy." if rem_pct > 40 else "Careful. You are spending money a bit too fast this month." if rem_pct > 15 else "Danger! You have almost run out of spending money."
        
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid {health_color};">
            <span style="font-size:12px; color:#64748b; font-weight:700; letter-spacing:0.5px;">❤️ FINANCIAL HEALTH STATUS</span><br/>
            <span style="font-size:15px; color:#1e293b;">You still have <b>{rem_pct:.1f}%</b> of your monthly safety budget left.</span><br/>
            <span style="font-size:13px; color:{health_color}; font-weight:700; display:inline-block; margin-top:4px;">Finora Advice: {health_label}</span>
        </div>
        """, unsafe_allow_html=True)

        # STUDY ABROAD LIVE CURRENCY WIDGET
        rates = get_live_exchange_rates()
        if rates:
            usd_val = rates.get("USD", 0.012)
            gbp_val = rates.get("GBP", 0.009)
            st.markdown(f"""
            <div class="metric-card" style="background-color: #f0f9ff; border: 1px solid #bae6fd;">
                <span style="font-size:12px; color:#0369a1; font-weight:700; letter-spacing:0.5px;">🌐 STUDY ABROAD WALLET CONVERTER</span><br/>
                <span style="font-size:14px; color:#1e293b;">Your <b>₹25,000</b> monthly budget equals roughly <b>${25000 * usd_val:,.2f} USD</b> or <b>£{25000 * gbp_val:,.2f} GBP</b>.</span>
            </div>
            """, unsafe_allow_html=True)

        # DAILY BUDGET GUIDELINE
        daily_allowance = max((budget_max - total_spent) / 30, 0.0)
        st.markdown(f"""
        <div class="metric-card" style="background-color: #f8fafc; border: 1px solid #e2e8f0;">
            <span style="font-size:12px; color:#475569; font-weight:700; letter-spacing:0.5px;">📅 DAILY BUDGET GUIDELINE</span><br/>
            <span style="font-size:14.5px; color:#1e293b;">To stay safe until the end of the month, try not to spend more than <b>₹{daily_allowance:,.2f} per day</b>.</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size: 16px; font-weight: 700; color:#1e293b; margin-bottom:4px;'>⚡ Add an Expense Quickly</p>", unsafe_allow_html=True)
        with st.form("quick_log_form", clear_on_submit=True):
            q_col1, q_col2, q_col3 = st.columns([1.5, 1.1, 1.1])
            with q_col1: q_cat = st.selectbox("What was this for?", ["Food & Dining", "Education & Books", "Rent & Bills", "Entertainment & Leisure", "Mutual Funds & Investments"], key="q_cat")
            with q_col2: q_amt = st.number_input("Amount (₹)", min_value=1.0, value=100.0, step=10.0, key="q_amt")
            with q_col3: 
                st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                q_sub = st.form_submit_button("Save Expense", use_container_width=True)
            if q_sub:
                supabase.table("expenses").insert({"username": username, "category": q_cat, "amount": q_amt}).execute()
                st.toast("Expense saved successfully!", icon="✅")
                st.rerun()

    with right_panel:
        st.markdown("<p style='font-size: 16px; font-weight: 700; color:#1e293b; margin-bottom:4px;'>📊 Spending Breakdown Graph</p>", unsafe_allow_html=True)
        if res.data:
            df = pd.DataFrame(res.data)
            df['amount'] = df['amount'].astype(float)
            fig = px.pie(df, values='amount', names='category', hole=0.62, color_discrete_sequence=px.colors.qualitative.Safe)
            fig.update_layout(height=260, margin=dict(t=15, b=15, l=15, r=15), showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div style='height:240px; display:flex; align-items:center; justify-content:center; background:#f8fafc; border: 1px dashed #cbd5e1; border-radius:14px; color:#64748b; font-size:14px; margin-top:4px; text-align:center; padding:20px;'>Your personal pie chart will show up here as soon as you type in your first expense!</div>", unsafe_allow_html=True)

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
    
    h_col1, h_col2 = st.columns([1.8, 2.2])
    with h_col1: st.markdown("<p class='section-header'>📚 Finora Fun Interactive Academy</p>", unsafe_allow_html=True)
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
    st.progress(current_step / total_steps, text=f"Total Course Progress: {int((current_step/total_steps)*100)}% Completed (Page {current_step}/{total_steps})")
    
    st.markdown(f"<div class='stLessonCard'><span style='color:#10b981; font-weight:800; font-size:11.5px; letter-spacing:1px;'>YOUR LESSON CARD • PAGE {p_idx} OF 4</span>", unsafe_allow_html=True)

    if c_idx == 0:
        if p_idx == 1:
            st.markdown("### The Magic of Growing Your Money Automatically")
            st.write("Imagine earning rewards on your money, and then earning **even more rewards on top of those rewards**! That is how money grows over time. When you leave your extra cash or your interest returns alone instead of spending them instantly, your balance starts to grow larger and faster every single year.")
            st.write("**💡 Real World Example:** If you save a small amount every single month while you are in college, that money has decades to grow quietly in the background. It will end up much bigger than if you tried to save a massive lump sum later in life.")
        elif p_idx == 2:
            st.markdown("### Simple Shortcuts: The Rule of 72")
            st.write("Want to know exactly how many years it will take for your saved money to double in size? There is a beautiful mathematical shortcut called the **Rule of 72**. All you have to do is divide the number **72** by the yearly growth rate your account gives you.")
            st.latex(r"Years\ to\ Double\ Your\ Money = \frac{72}{Yearly\ Growth\ Rate}")
            st.write("**📋 Quick Checklist:**\n* If an investment grows at 6% a year, it takes 12 years to double ($72 / 6 = 12$).\n* If it grows at 12% a year, it takes just 6 years to double ($72 / 12 = 6$)!")
        elif p_idx == 3:
            st.markdown("### The Basic Growth Formula")
            st.write("For those who love seeing the simple math behind the scenes, here is the official formula used around the world to track how money multiplies over time:")
            st.latex(r"A = P\left(1 + \frac{r}{n}\right)^{nt}")
            st.write("**What these letters mean in plain English:**\n* **A** = How much total money you will have at the end.\n* **P** = The starting cash balance you began with.\n* **r** = The yearly growth rate.\n* **t** = The number of years you leave it to grow.")
        elif p_idx == 4:
            st.markdown("### 🎯 Quick Pop Quiz!")
            ans = st.radio("If you save ₹1,000 at a 10% interest rate that builds on itself every year, how much total money do you have after 2 years?", ["₹1,200.00", "₹1,210.00", "₹1,100.00"])
            if st.button("Check My Quiz Answer"):
                if ans == "₹1,210.00": 
                    st.success("Awesome job! You got it right! +25 Finora XP added to your profile.")
                    supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute()
                    st.rerun()
                else: 
                    st.error("Not quite! Remember, in the second year, you earn interest on top of the first year's interest too. Try again!")

    elif c_idx == 4:
        if p_idx == 1:
            st.markdown("### What is a Mutual Fund?")
            st.write("A Mutual Fund is like a giant money pool. Thousands of everyday people put their small savings together, and a professional manager uses that massive pool of cash to buy tiny pieces of hundreds of different stable companies like Apple, Google, or Tata.")
            st.write("**🌟 Why this helps you:** If one single company goes out of business, you do not lose your shirt because you still own tiny pieces of hundreds of other healthy companies that protect your cash.")
        elif p_idx == 2:
            st.markdown("### Saving Every Month Automatically (SIP)")
            st.write("A Systematic Investment Plan (or **SIP** for short) is just a fancy way of saying: *'Set it and forget it.'* It automatically moves a tiny amount of cash (like ₹500) from your regular bank account into your investments on the exact same day every single month.")
            st.write("**🚀 The Superpower:** This protects you from bad timing. When prices drop in the market, your regular ₹500 automatically buys **more** cheap shares. When pri
