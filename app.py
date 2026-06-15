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
    st.markdown("<div style='text-align: center; margin-bottom: 10px;'><span class='main-header'>✨ Finora </span></div>", unsafe_allow_html=True)
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
                if ans == "₹1,210.00": st.success("Awesome job! You got it right! +25 Finora XP added to your profile."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()
                else: st.error("Not quite! Remember, in the second year, you earn interest on top of the first year's interest too. Try again!")

    elif c_idx == 4:
        if p_idx == 1:
            st.markdown("### What is a Mutual Fund?")
            st.write("A Mutual Fund is like a giant money pool. Thousands of everyday people put their small savings together, and a professional manager uses that massive pool of cash to buy tiny pieces of hundreds of different stable companies like Apple, Google, or Tata.")
            st.write("**🌟 Why this helps you:** If one single company goes out of business, you do not lose your shirt because you still own tiny pieces of hundreds of other healthy companies that protect your cash.")
        elif p_idx == 2:
            st.markdown("### Saving Every Month Automatically (SIP)")
            st.write("A Systematic Investment Plan (or **SIP** for short) is just a fancy way of saying: *'Set it and forget it.'* It automatically moves a tiny amount of cash (like ₹500) from your regular bank account into your investments on the exact same day every single month.")
            st.write("**🚀 The Superpower:** This protects you from bad timing. When prices drop in the market, your regular ₹500 automatically buys **more** cheap shares. When prices are sky-high, it buys fewer shares. Over time, this smooths out into a winning strategy.")
        elif p_idx == 3:
            st.markdown("### Watch Out For Hidden Management Fees!")
            st.write("Every mutual fund charges a small annual fee to pay the management team. This fee is called the **Expense Ratio**. Always look for **'Direct'** funds instead of **'Regular'** funds. Regular funds have middleman fees built in, while Direct funds skip the middleman and can save you lakhs of rupees over time.")
        elif p_idx == 4:
            st.markdown("### 🎯 Quick Pop Quiz!")
            ans = st.radio("What is the easiest way to safely buy more shares of a mutual fund automatically when prices drop?", ["Trying to guess the exact best day to trade", "Setting up a monthly automatic plan (SIP)", "Buying volatile single stocks on rumors"])
            if st.button("Check My Quiz Answer"):
                if "SIP" in ans: st.success("Perfect! Regular automated monthly plans are the safest way to grow wealth. +25 Finora XP added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    elif c_idx == 7:
        if p_idx == 1:
            st.markdown("### How Credit Cards Really Work")
            st.write("A credit card can be a wonderful helper. It lets you buy things safely, gives you cashback rewards, and helps you build a good reputation with banks. But it is vital to remember: **credit cards are temporary loans, not free income.**")
        elif p_idx == 2:
            st.markdown("### The Minimum Balance Trick")
            st.write("When your credit card bill arrives, the bank will show you a tiny number called the **'Minimum Balance Due'** (usually just 5% of the total bill). If you only pay this tiny amount, the bank will not charge you a late fee, but they will start charging you massive interest rates (**up to 40% a year!**) on the rest of your debt.")
            st.write("**⚠️ The Danger:** Paying only the minimum amount is a trap that can keep you trapped in debt for years.")
        elif p_idx == 3:
            st.markdown("### Two Golden Card Rules to Live By")
            st.write("1. **Treat it like cash:** If you do not have the real money inside your bank checking account right now to buy that item, **do not swipe your card for it.**\n2. **Turn on Auto-Pay:** Set your card app to automatically pay off the **Total Statement Balance** in full every single month so you never pay a single rupee of interest.")
        elif p_idx == 4:
            st.markdown("### 🎯 Quick Pop Quiz!")
            ans = st.radio("What happens if you only pay the 'Minimum Amount Due' on a credit card statement bill?", ["The bank forgives the rest of your debt for free", "The bank begins charging you brutal interest rates (up to 40%+) on the remaining balance", "Your credit score instantly hits a perfect rating"])
            if st.button("Check My Quiz Answer"):
                if "charging you brutal interest" in ans: st.success("Spot on! Always pay the full statement balance to stay safe. +25 Finora XP added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    else:
        if p_idx < 4:
            st.markdown(f"### {courses[c_idx]} (Section {p_idx})")
            st.write("This simple Finora lesson is designed to teach you actionable money habits step-by-step. You will learn how to organize your cash, avoid bad debt, and start building long-term security.")
        else:
            st.markdown("### 🎯 Final Review Quiz")
            ans = st.radio("What is the best everyday framework to build reliable personal wealth?", ["Keep all extra money sitting in a zero-interest wallet", "Pay off expensive debt, keep a small cash safety cushion, and invest monthly in simple index funds", "Day-trade random digital coins with borrowed money"])
            if st.button("Check My Quiz Answer"):
                if "Pay off expensive debt" in ans: st.success("Brilliant! You completed the quiz. +25 Finora XP added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute(); st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    nav_col1, _, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if p_idx > 1:
            if st.button("⬅️ Go Back", use_container_width=True): st.session_state.page_idx -= 1; st.rerun()
    with nav_col3:
        if p_idx < 4:
            if st.button("Next Page ➡️", use_container_width=True): st.session_state.page_idx += 1; st.rerun()

def show_budgeting(username):
    st.markdown("<p class='section-header'>📉 Money Envelopes & Expense Tracker</p>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.2, 1.8])
    with col1:
        with st.form("exp_form", clear_on_submit=True):
            st.markdown("<p style='font-size:15px; font-weight:700; margin:0; color:#334155;'>Log an Expense</p>", unsafe_allow_html=True)
            cat = st.selectbox("What bucket does this fit into?", ["Food & Dining", "Education & Books", "Rent & Bills", "Entertainment & Leisure", "Mutual Funds & Investments"])
            amt = st.number_input("How much did you spend? (₹)", min_value=1.0, value=500.0, step=50.0)
            if st.form_submit_button("Record Expense Entry", use_container_width=True):
                supabase.table("expenses").insert({"username": username, "category": cat, "amount": amt}).execute()
                st.rerun()
                
        # EMERGENCY SAFETY CUSHION ADVISOR
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        res_p = supabase.table("profiles").select("occupation").eq("username", username).execute()
        track = res_p.data[0]['occupation'] if res_p.data else "Student"
        months_needed = 6 if "Freelancer" in track or "Founder" in track else 4
        safety_total = 8000.0 * months_needed
        st.markdown(f"""
        <div class="metric-card" style="background:#f0fdfa; border: 1px solid #ccfbf1; margin-top:12px;">
            <span style="font-size:11.5px; color:#0f766e; font-weight:700; letter-spacing:0.5px;">🛡️ YOUR CASH SAFETY CUSHION</span><br/>
            <span style="font-size:13.5px; color:#115e59;">Because you are a <b>{track}</b>, we recommend keeping a <b>{months_needed}-Month Safety Fund</b> worth at least <b>₹{safety_total:,.2f}</b> in a safe bank account for sudden emergencies.</span>
        </div>
        """, unsafe_allow_html=True)
                
    with col2:
        res = supabase.table("expenses").select("*").eq("username", username).execute()
        total = sum([float(i['amount']) for i in res.data]) if res.data else 0.0
        
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 0px; border-left: 4px solid #0284c7;">
            <span style="font-size:12px; color:#64748b; font-weight:700; letter-spacing:0.5px;">MONTHLY SPENDING METER</span><br/>
            <span style="font-size:22px; font-weight:800; color:#0284c7;">₹{total:,.2f} Spent / ₹25,000 Safety Limit</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(total/25000, 1.0))
        
        # CLEAR ITEMIZED RECENT HISTORY LEDGER
        st.markdown("<p style='font-size:14px; font-weight:700; color:#475569; margin-bottom:6px; margin-top:14px;'>📜 Your Recent History Ledger</p>", unsafe_allow_html=True)
        if res.data:
            for item in res.data[-4:]:
                st.markdown(f"""
                <div class="ledger-row">
                    <span style="font-weight:600; color:#1e293b;">{item['category']}</span>
                    <span style="font-weight:700; color:#ef4444;">- ₹{float(item['amount']):,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='font-size:13px; color:gray; font-style:italic;'>You haven't tracked any expenses yet.</p>", unsafe_allow_html=True)

def show_savings():
    st.markdown("<p class='section-header'>🐷 The Wealth Multiplier & Milestone Engine</p>", unsafe_allow_html=True)
    st.write("Most people think saving is about sacrifice. At Finora, we look at it as buying your future freedom. See how small habits scale up, shield your cash from inflation, and map out your next big purchases.")

    # ---------------------------------------------------------
    # PART 1: THE DRIVER SEAT (SETTINGS INPUT)
    # ---------------------------------------------------------
    st.markdown("<p style='font-size: 16px; font-weight: 700; color:#1e293b; margin-bottom:8px;'>⚙️ Step 1: Set Your Baseline Numbers</p>", unsafe_allow_html=True)
    
    in_col1, in_col2, in_col3 = st.columns([1, 1, 1])
    with in_col1:
        starting_cash = st.number_input("Your Starting Cash Cushion (₹)", min_value=0, value=5000, step=1000, help="Money you already have set aside right now.")
    with in_col2:
        monthly_stash = st.number_input("Monthly Stash Contribution (₹)", min_value=0, value=1500, step=250, help="How much extra room you can squeeze out of your budget each month.")
    with in_col3:
        years_horizon = st.slider("Time Horizon Plan (Years)", min_value=1, max_value=10, value=3, help="How long you want to let this strategy run.")

    # Core engine math pipelines (Calculated monthly)
    months_total = years_horizon * 12
    rate_savings, rate_fd, rate_index, rate_inflation = 0.035, 0.071, 0.120, 0.060
    
    # Growth formulas with monthly cash flows
    final_savings = starting_cash * ((1 + rate_savings/12) ** months_total) + sum([monthly_stash * ((1 + rate_savings/12) ** (months_total - i)) for i in range(1, months_total + 1)])
    final_fd = starting_cash * ((1 + rate_fd/12) ** months_total) + sum([monthly_stash * ((1 + rate_fd/12) ** (months_total - i)) for i in range(1, months_total + 1)])
    final_index = starting_cash * ((1 + rate_index/12) ** months_total) + sum([monthly_stash * ((1 + rate_index/12) ** (months_total - i)) for i in range(1, months_total + 1)])
    
    out_of_pocket = starting_cash + (monthly_stash * months_total)
    lost_buying_power = out_of_pocket - (out_of_pocket / ((1 + rate_inflation) ** years_horizon))

    # ---------------------------------------------------------
    # PART 2: THE TRIPLE-TRACK VERDICT CARDS
    # ---------------------------------------------------------
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 16px; font-weight: 700; color:#1e293b; margin-bottom:4px;'>🔮 Step 2: Choose Your Money's Growth Path</p>", unsafe_allow_html=True)
    st.caption(f"Actual cash physically saved out of your pocket over {years_horizon} years: ₹{out_of_pocket:,.2f}")
    
    card1, card2, card3 = st.columns([1, 1, 1])
    
    with card1:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #94a3b8; height: 100%;">
            <span style="font-size:11px; color:#64748b; font-weight:700; letter-spacing:0.5px;">🏥 TRADITIONAL BANK WALLET</span><br/>
            <span style="font-size:24px; font-weight:800; color:#475569;">₹{final_savings:,.2f}</span><br/>
            <span style="font-size:13px; color:#64748b;">Grows at a crawl (~3.5%). Completely safe, but fails to beat the rising cost of living.</span>
        </div>
        """, unsafe_allow_html=True)
        
    with card2:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #0284c7; height: 100%;">
            <span style="font-size:11px; color:#0284c7; font-weight:700; letter-spacing:0.5px;">🔒 GUARANTEED FIXED CONTRACT</span><br/>
            <span style="font-size:24px; font-weight:800; color:#0284c7;">₹{final_fd:,.2f}</span><br/>
            <span style="font-size:13px; color:#0369a1;">Locked in safely (~7.1%). Your balance is legally protected and keeps up with standard inflation drops.</span>
        </div>
        """, unsafe_allow_html=True)
        
    with card3:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #10b981; height: 100%; background: linear-gradient(180deg, #ffffff 0%, #f0fdf4 100%);">
            <span style="font-size:11px; color:#10b981; font-weight:700; letter-spacing:0.5px;">🚀 DIVERSIFIED MARKET INDEX</span><br/>
            <span style="font-size:24px; font-weight:800; color:#10b981;">₹{final_index:,.2f}</span><br/>
            <span style="font-size:13px; color:#15803d;">Paced along India's top companies (~12% historic average). Best path to turn minor cash into real wealth.</span>
        </div>
        """, unsafe_allow_html=True)

    # Behavioral Psychology Trigger: The Loss Focus
    st.markdown(f"""
    <div style="background-color: #fef2f2; color: #b91c1c; padding: 12px 16px; border-radius: 10px; border: 1px solid #fee2e2; margin-top: 10px; font-size: 14px;">
        ⚠️ <b>The Hidden Cost of Doing Nothing:</b> Leaving your saved cash sitting uninvested inside a drawer or a basic smartphone wallet means a standard 6% inflation rate melts away <b>₹{lost_buying_power:,.2f}</b> of its raw purchasing power over your {years_horizon}-year timeline.
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # PART 3: THE HABIT COMPONENT & ASSETS
    # ---------------------------------------------------------
    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    
    layout_col, crypto_col = st.columns([2.1, 0.9])
    
    with layout_col:
        st.markdown("<p style='font-size: 16px; font-weight: 700; color:#1e293b; margin-bottom:4px;'>☕ Step 3: Small Swaps, Big Future Wins</p>", unsafe_allow_html=True)
        st.write("Instead of trying to find massive sums of money to invest, see what happens if you swap out just one everyday small expense pattern over a 5-year run:")
        
        habit1, habit2, habit3 = st.columns([1, 1, 1])
        with habit1:
            stash_tea = sum([(40 * 30) * ((1 + rate_index/12) ** (60 - i)) for i in range(1, 61)])
            st.markdown(f"""
            <div class="metric-card" style="background-color: #fffbeb; border: 1px solid #fef3c7; height:100%; padding:15px;">
                <span style="font-size:11.5px; font-weight:700; color:#b45309; text-transform: uppercase;">☕ The Daily Chai Swap</span><br/>
                <span style="font-size:20px; font-weight:800; color:#78350f;">₹{stash_tea:,.2f}</span><br/>
                <span style="font-size:12.5px; color:#92400e;">Saved by putting away <b>₹40 a day</b> into an index option instead of premium street drinks.</span>
            </div>
            """, unsafe_allow_html=True)
        with habit2:
            stash_food = sum([(160 * 30) * ((1 + rate_index/12) ** (60 - i)) for i in range(1, 61)])
            st.markdown(f"""
            <div class="metric-card" style="background-color: #f0fdfa; border: 1px solid #ccfbf1; height:100%; padding:15px;">
                <span style="font-size:11.5px; font-weight:700; color:#0f766e; text-transform: uppercase;">🍔 The Delivery App Skip</span><br/>
                <span style="font-size:20px; font-weight:800; color:#115e59;">₹{stash_food:,.2f}</span><br/>
                <span style="font-size:12.5px; color:#134e4a;">Saved by cooking at home just once more per week and stashing <b>₹160 a day</b>.</span>
            </div>
            """, unsafe_allow_html=True)
        with habit3:
            stash_sub = sum([(350 * 30) * ((1 + rate_index/12) ** (60 - i)) for i in range(1, 61)])
            st.markdown(f"""
            <div class="metric-card" style="background-color: #f5f3ff; border: 1px solid #edd5ff; height:100%; padding:15px;">
                <span style="font-size:11.5px; font-weight:700; color:#6d28d9; text-transform: uppercase;">👟 The Impulse Guard</span><br/>
                <span style="font-size:20px; font-weight:800; color:#5b21b6;">₹{stash_sub:,.2f}</span><br/>
                <span style="font-size:12.5px; color:#4c1d95;">Saved by pausing 24 hours before buying clothes or tech accessories (Saves <b>₹350 a day</b>).</span>
            </div>
            """, unsafe_allow_html=True)
            
    with crypto_col:
        st.markdown("<p style='font-size:16px; font-weight:700; color:#1e293b; margin-bottom:4px;'>⚡ Live Global Crypto Rates</p>", unsafe_allow_html=True)
        crypto = get_crypto_prices()
        if crypto:
            btc_inr = crypto.get("bitcoin", {}).get("inr", 0)
            eth_inr = crypto.get("ethereum", {}).get("inr", 0)
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid #f59e0b; padding: 12px; margin-bottom:8px;">
                <span style="font-size:11px; color:gray; font-weight:bold;">BITCOIN (BTC)</span><br/>
                <span style="font-size:15px; font-weight:700; color:#0f172a;">₹{btc_inr:,.2f}</span>
            </div>
            <div class="metric-card" style="border-top: 3px solid #6366f1; padding: 12px; margin-bottom:8px;">
                <span style="font-size:11px; color:gray; font-weight:bold;">ETHEREUM (ETH)</span><br/>
                <span style="font-size:15px; font-weight:700; color:#0f172a;">₹{eth_inr:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.caption("Live asset feed unavailable at this hour.")

    # ---------------------------------------------------------
    # PART 4: THE REVERSE GOAL HORIZON ARCHITECT
    # ---------------------------------------------------------
    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 16px; font-weight: 700; color:#1e293b; margin-bottom:4px;'>🎯 Step 4: Map Out a Custom Financial Goal Target</p>", unsafe_allow_html=True)
    
    plan_left, plan_right = st.columns([1.2, 1.8])
    with plan_left:
        with st.form("dynamic_goal_engine"):
            st.markdown("<p style='font-size:14px; font-weight:700; margin:0 0 6px 0; color:#475569;'>Configure Milestone Blueprint</p>", unsafe_allow_html=True)
            milestone_label = st.text_input("What are you building this fund for?", value="Next-Gen Developer Laptop")
            milestone_target = st.number_input("Target Amount Needed (₹)", min_value=2000, value=75000, step=5000)
            monthly_capacity = st.number_input("Your Comfortable Monthly Stash Power (₹)", min_value=250, value=3500, step=250)
            st.form_submit_button("Calculate My Exact Timeline")
            
    with plan_right:
        if monthly_capacity > 0:
            total_months_needed = int(milestone_target / monthly_capacity) if milestone_target > monthly_capacity else 1
            years_part = total_months_needed // 12
            months_part = total_months_needed % 12
            
            duration_readout = f"{years_part} Year{'s' if years_part > 1 else ''} " if years_part > 0 else ""
            if months_part > 0 or years_part == 0:
                duration_readout += f"{months_part} Month{'s' if months_part != 1 else ''}"
                
            st.markdown(f"""
            <div class="metric-card" style="background-color: #fafafa; border-left: 5px solid #0284c7; padding: 24px; height: 100%;">
                <span style="font-size:12px; color:#64748b; font-weight:700; letter-spacing:0.5px;">🏁 TARGET HORIZON OUTCOME: {milestone_label.upper()}</span><br/>
                <span style="font-size:32px; font-weight:900; color:#0f172a; line-height:1.2;">{duration_readout}</span><br/>
                <p style="font-size:14.5px; color:#475569; margin-top:10px; line-height:1.5;">
                    By maintaining an automated rhythm of <b>₹{monthly_capacity:,.2f} each month</b>, your cash reserve will fully bridge the <b>₹{milestone_target:,.2f}</b> goal post in exactly <b>{total_months_needed} months</b>.
                </p>
                <div style="font-size:12.5px; color:#0284c7; font-weight:700; background-color:#f0f9ff; padding:8px 12px; border-radius:6px; display:inline-block; margin-top:4px;">
                    💡 Finora Automation Hack: Set a bank instruction to move this ₹{monthly_capacity:,.2f} out of your main account on the 1st day of the month before you get a chance to spend it.
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_splitting():
    st.markdown("<p class='section-header'>👥 Easy Friend Bill Splitter & Shareable UPI Links</p>", unsafe_allow_html=True)
    st.write("Split dinner or rent bills with friends perfectly and create an instant payment share link without doing any complicated math.")
    
    col1, col2 = st.columns([1.4, 1.6])
    with col1:
        bill = st.number_input("Total Bill Amount to Split (₹)", value=1500.0, step=100.0)
        people = st.slider("How many people are splitting it?", 2, 12, 3)
        vpa = st.text_input("Your UPI Address ID (Optional - e.g., name@okaxis)", placeholder="name@upi").strip()
    with col2:
        per_person = round(bill/people, 2) if people > 0 else 0
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:22px 18px; border-left: 6px solid #10b981; background: linear-gradient(180deg, #ffffff 0%, #f9fbf9 100%); margin-top:10px;">
            <span style="font-size:13.5px; color:#64748b; font-weight:600; letter-spacing:0.5px;">EACH PERSON OWES:</span><br/>
            <span style="font-size:40px; font-weight:900; color:#0f172a; line-height:1.2;">₹{per_person:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if vpa:
            st.markdown("<span style='font-size:13px; color:#475569; font-weight:700;'>⚡ UPI LINK TO PASTE INTO YOUR FRIEND CHAT:</span>", unsafe_allow_html=True)
            upi_link = f"upi://pay?pa={vpa}&pn=FinoraSplit&am={per_person}&cu=INR"
            st.code(upi_link, language="markdown")
            
            # AUTOMATED WHATSAPP SPLIT LINK GENERATOR
            message_text = f"Hey! Here is the split for our bill. Your share comes out to exactly ₹{per_person:,.2f}. You can pay directly via UPI here: {upi_link}"
            encoded_message = message_text.replace(" ", "%20")
            whatsapp_url = f"https://wa.me/?text={encoded_message}"
            
            st.markdown(f"""
            <a href="{whatsapp_url}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #25d366; color: white; text-align: center; padding: 12px; border-radius: 10px; font-weight: bold; font-size: 14px; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-transform: uppercase; letter-spacing:0.5px;">
                    📱 Ping Friends on WhatsApp
                </div>
            </a>
            """, unsafe_allow_html=True)

# --- CORE APPLICATION MASTER SKELETON ---
if st.session_state.username is None:
    login_page()
else:
    profile = fetch_user_profile(st.session_state.username)
    
    with st.sidebar:
        st.markdown("<p class='main-header' style='font-size: 28px !important; margin-bottom:0px;'>✨ Finora</p>", unsafe_allow_html=True)
        st.caption(f"Logged in as: {st.session_state.username.upper()}")
        
        # SIDEBAR MOTIVATION VALUE BLOCK
        quote = get_daily_motivation()
        st.markdown(f"""
        <div style="background: #f8fafc; padding: 12px; border-radius: 10px; border: 1px solid #e2e8f0; margin: 10px 0;">
            <p style="font-size: 12px !important; font-style: italic; color: #475569; margin:0; line-height:1.4;">{quote}</p>
        </div>
        """, unsafe_allow_html=True)
        
        user_points = profile['points'] if profile else 0
        st.markdown(f"🏆 Academy Balance: **{user_points} Finora XP**")
        st.markdown("<hr style='margin: 8px 0; border-color:#e2e8f0;'/>", unsafe_allow_html=True)
        
        if st.sidebar.button("📊 My Dashboard Hub"): st.session_state.nav_selection = "📊 Dashboard"; st.rerun()
        if st.sidebar.button("📚 Finora Micro-Academy"): st.session_state.nav_selection = "📚 Micro-Courses"; st.rerun()
        if st.sidebar.button("📉 Envelope Expense Tracker"): st.session_state.nav_selection = "📉 Expense Tracker"; st.rerun()
        if st.sidebar.button("🐷 Savings Multiplier"): st.session_state.nav_selection = "🐷 Savings Calculator"; st.rerun()
        if st.sidebar.button("👥 Split Bills With Friends"): st.session_state.nav_selection = "👥 Split Bills"; st.rerun()
        
        st.markdown("<hr style='margin: 12px 0; border-color:#e2e8f0;'/>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Log Out of Session"):
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
