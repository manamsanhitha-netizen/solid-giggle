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
        padding: 30px;
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.02);
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
if "course_idx" not in st.session_state:
    st.session_state.course_idx = 0
if "page_idx" not in st.session_state:
    st.session_state.page_idx = 1

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

# --- APP PAGES ---

def show_finance_desk(profile, username):
    st.markdown("## 📊 Personal Finance Desk")
    st.caption("Real-time summary of your account standing and XP growth.")
    
    standing = profile['occupation'] if profile else "Student"
    points = profile['points'] if profile else 0
    level = "Beginner" if points < 150 else "Intermediate" if points < 400 else "Financial Master"

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
    
    courses = [
        "Course 1: The Velocity of Compounding",
        "Course 2: Tactical Capital Allocation (50/30/20)",
        "Course 3: Credit Architecture & Trust",
        "Course 4: Index Funds & Passive Capture",
        "Course 5: The Liquidity Safety Buffer",
        "Course 6: Taxes for Freelancers & Operators",
        "Course 7: Inflation Dynamics & Asset Erosion",
        "Course 8: High vs. Low Cost Debt Leverage"
    ]
    
    # Selection box resets the sub-page index back to 1 if the user hops courses
    sel_course = st.selectbox("Choose Academy Track", courses, index=st.session_state.course_idx)
    new_course_idx = courses.index(sel_course)
    if new_course_idx != st.session_state.course_idx:
        st.session_state.course_idx = new_course_idx
        st.session_state.page_idx = 1
        st.rerun()

    current_points = profile['points'] if profile else 0
    c_idx = st.session_state.course_idx
    p_idx = st.session_state.page_idx

    # --- DYNAMIC PROGRESS BAR CALCULATOR ---
    # Total progress = (current course index * 4 pages per course + current page offset) / (8 courses * 4 pages total)
    total_steps = 32
    current_step = (c_idx * 4) + p_idx
    progress_percentage = min(current_step / total_steps, 1.0)
    st.progress(progress_percentage, text=f"Overall Academy Journey Progress: {int(progress_percentage * 100)}% Complete (Step {current_step}/{total_steps})")
    
    st.markdown(f"#### Page {p_idx} of 4")
    st.markdown("<div class='stLessonCard'>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # COURSE MODULE CONTENT DATA MATRIX
    # ----------------------------------------------------
    if c_idx == 0:  # Course 1: Compounding
        if p_idx == 1:
            st.markdown("### 📈 Course 1 (Page 1): The Mathematics of Compound Returns")
            st.write("Compounding operates as calculation architecture where your yields generate additional subsequent returns over time. Unlike simple interest, which only pays out returns on your original seed capital, compounding continually layers interest onto your historical gains.")
            st.write("This creates a geometric progression model. In the early phases of a portfolio's life cycle, the asset growth line appears flat and underwhelming. However, across a multi-decade runway, the absolute return values spin upwards into a nearly vertical trajectory.")
        elif p_idx == 2:
            st.markdown("### 📈 Course 1 (Page 2): The Rule of 72 & The Cost of Waiting")
            st.write("To quickly calculate the velocity of compounding, professionals utilize the **Rule of 72**. By dividing 72 by your expected annual rate of return, you arrive at the exact number of years required to double your principal balance without adding another dollar.")
            st.latex(r"Years\ to\ Double = \frac{72}{Annual\ Interest\ Rate}")
            st.write("This formula demonstrates why delaying your investment horizon is the single most expensive error a student can commit. A dollar invested at age 20 enjoys twice as many doubling cycles as a dollar invested at age 35.")
        elif p_idx == 3:
            st.markdown("### 📈 Course 1 (Page 3): Setting Up the Equation Variables")
            st.write("The underlying mathematical expression driving this phenomenon relies on exponential variables, where time ($t$) acts as the exponent raising the entire rate equation:")
            st.latex(r"A = P\left(1 + \frac{r}{n}\right)^{nt}")
            st.write("Where $A$ is the final future balance, $P$ is the principal seed value, $r$ represents the annual rate of interest, $n$ is the compounding frequency per period, and $t$ defines the macro duration in years. Maximizing your frequency value ($n$) and time limit ($t$) optimizes the output vector automatically.")
        elif p_idx == 4:
            st.markdown("### 🎯 Course 1 Assessment: The Compounding Quiz")
            ans = st.radio("If you deposit $1,000 compounding at an annual interest yield of 10%, what is the profile value tracking state at Year 2 conclusion?", ["$1,200.00", "$1,210.00", "$1,100.00"])
            if st.button("Submit Module Quiz Entry"):
                if ans == "$1,210.00": st.success("Correct! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute()
                else: st.error("Incorrect. Remember that the 10% rate applies directly to the adjusted Year 1 ending asset base ($1,100), not the initial seed balance.")

    elif c_idx == 1:  # Course 2: 50/30/20
        if p_idx == 1:
            st.markdown("### 🎛️ Course 2 (Page 1): Introduction to Balanced Budget Engineering")
            st.write("Budget models collapse in real-world scenarios when they are built with rigid restrictions. Denying all discretionary personal gratification leads to psychological burnout, causing students to abandon fiscal tracking software entirely.")
            st.write("The 50/30/20 allocation rule provides structural flexibility by organizing expenses into three transparent buckets based on prioritization indexes. It scales automatically alongside your income, preserving your standard of living while securing your wealth.")
        elif p_idx == 2:
            st.markdown("### 🎛️ Course 2 (Page 2): Dissecting Needs vs. Wants Parameters")
            st.write("The framework splits your net, take-home income as follows:")
            st.markdown("- **50% Needs:** These represent your non-negotiable structural costs. If omitted, they directly impair your safety or legal status. Examples include basic housing rent, transportation, utilities, and raw lifestyle groceries.")
            st.markdown("- **30% Wants:** These cover your discretionary personal comfort choices. This includes entertainment subscriptions, upscale dining, fashion alternatives, travel, and hobby investments.")
        elif p_idx == 3:
            st.markdown("### 🎛️ Course 2 (Page 3): Financing the Future Layer")
            st.write("The final **20%** of your capital configuration must be strictly ring-fenced for your financial future. This bucket does not cover daily operational expenses or vacation savings.")
            st.write("Instead, this money is instantly routed toward long-term asset acceleration, high-yield retirement accounts, index portfolios, and the aggressive pay-down of any high-interest debt balances. Automating this 20% transfer on payday ensures your safety net grows continuously.")
        elif p_idx == 4:
            st.markdown("### 🎯 Course 2 Assessment: The 50/30/20 Quiz")
            ans = st.radio("Under proper 50/30/20 budget criteria, where does a premium streaming television package settle into?", ["Fixed Structural Needs (50%)", "Discretionary Wants Allocation (30%)", "Financial Future Acceleration (20%)"])
            if st.button("Submit Module Quiz Entry"):
                if ans == "Discretionary Wants Allocation (30%)": st.success("Correct! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute()
                else: st.error("Incorrect. While entertainment adds personal value, it represents a flexible luxury that can be paused during financial emergencies.")

    elif c_idx == 2:  # Course 3: Credit Scores
        if p_idx == 1:
            st.markdown("### 💳 Course 3 (Page 1): The Architecture of Institutional Credit")
            st.write("A credit score functions as a standardized algorithmic evaluation designed to calculate your probability of default. Institutional lenders utilize this rating to determine your interest rates on mortgages, auto loans, and corporate lines of credit.")
            st.write("Operating without an established credit history does not signify safety; instead, it signals a lack of data to banking systems, resulting in higher insurance premiums, renting hurdles, and loan rejections.")
        elif p_idx == 2:
            st.markdown("### 💳 Course 3 (Page 2): The Variables of FICO Score Calculation")
            st.write("Your primary credit rating (FICO) evaluates five discrete structural attributes:")
            st.markdown("- **35% Payment History:** Your record of clearing debt obligations on schedule.")
            st.markdown("- **30% Amounts Owed (Utilization):** The ratio of your active rolling balances relative to your maximum allowed borrowing limits.")
            st.markdown("- **15% Length of History:** The age profile of your oldest active reporting accounts.")
            st.markdown("- **10% New Credit Queries & 10% Credit Mix**")
        elif p_idx == 3:
            st.markdown("### 💳 Course 3 (Page 3): Practical Credit Optimization Rules")
            st.write("To optimize your credit profile before graduation, implement two rules. First, configure automatic minimum payments to guarantee your 35% Payment History metric remains flawless.")
            st.write("Second, maintain a credit utilization ratio below 30% on all revolving lines of credit. If your credit limit is $1,000, your reported balance should never cross $300 at any point during the billing cycle.")
        elif p_idx == 4:
            st.markdown("### 🎯 Course 3 Assessment: The Credit Mastery Quiz")
            ans = st.radio("What specific variable holds the single highest weighting percentage inside your institutional FICO score matrix?", ["The absolute income value of the individual", "Historical payment performance timeline data", "The total number of credit card accounts open"])
            if st.button("Submit Module Quiz Entry"):
                if ans == "Historical payment performance timeline data": st.success("Correct! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute()
                else: st.error("Incorrect. Payment history accounts for 35% of the total score computation, making consistency your most critical asset.")

    elif c_idx == 3:  # Course 4: Index Funds
        if p_idx == 1:
            st.markdown("### 🏛️ Course 4 (Page 1): The Fallacy of Stock Picking")
            st.write("Many beginner investors believe that building wealth requires identifying the next explosive individual stock, such as Tesla or Amazon, right before it surges. In reality, picking single stocks exposes your capital to severe company-specific volatility.")
            st.write("If that single company suffers an executive crisis, product recall, or bankruptcy, your personal savings can evaporate instantly. Diversification eliminates this single point of failure.")
        elif p_idx == 2:
            st.markdown("### 🏛️ Course 4 (Page 2): Index Funds & Broad Market Capture")
            st.write("An Index Fund or Exchange-Traded Fund (ETF) solves this problem by purchasing tiny fractions of hundreds of major companies simultaneously. For instance, an S&P 500 index fund holds an equity slice of the 500 largest corporate entities in America.")
            st.write("If ten of those companies encounter operational failures, their declines are completely ironed out by the collective gains of the remaining 490 enterprises, giving you smoother, market-wide returns.")
        elif p_idx == 3:
            st.markdown("### 🏛️ Course 4 (Page 3): Passive Management Fees & Market Data")
            st.write("Index funds utilize passive asset capture, meaning they simply replicate the market index rather than paying expensive research teams to speculate on stock movements. This structural design drives management costs (expense ratios) close to 0%.")
            st.write("Long-term historical market records show that broad market indexes average an annual yield of 7-10% over multi-decade tracking horizons, consistently outperforming over 90% of professional wall-street fund managers.")
        elif p_idx == 4:
            st.markdown("### 🎯 Course 4 Assessment: The Index Fund Quiz")
            ans = st.radio("What primary structural advantage do Index ETFs offer to student retail portfolios?", ["A guarantee of zero market volatility risks", "Instant asset diversification across entire macro markets at low cost", "The ability to choose matching daily price points"])
            if st.button("Submit Module Quiz Entry"):
                if ans == "Instant asset diversification across entire macro markets at low cost": st.success("Correct! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute()
                else: st.error("Incorrect. Index funds do not remove market volatility, but they excel at protecting your portfolio from the total collapse of any single company.")

    elif c_idx == 4:  # Course 5: Emergency Funds
        if p_idx == 1:
            st.markdown("### 🛡️ Course 5 (Page 1): The Financial Insulation Barrier")
            st.write("An emergency fund acts as an insulation layer separating your lifestyle from unexpected real-world shocks. Without a liquid emergency cushion, a sudden dental expense, automotive breakdown, or gap in employment forces you to assume high-cost credit card debt.")
            st.write("Alternatively, a lack of liquid reserves might force you to liquidate long-term stock holdings during a market downturn, permanently locking in portfolio losses to cover short-term bills.")
        elif p_idx == 2:
            st.markdown("### 🛡️ Course 5 (Page 2): Sizing Your Liquidity Thresholds")
            st.write("The exact scale of your emergency cache depends on your structural baseline living expenses. Calculate your monthly fixed requirements (Needs: rent + utilities + insurance + baseline groceries).")
            st.write("Standard financial planning dictates keeping a reserve equal to **3 to 6 months** of those baseline cash needs. If your essential outlays total $1,500 monthly, your target emergency vault parameter should range securely from $4,500 to $9,000.")
        elif p_idx == 3:
            st.markdown("### 🛡️ Course 5 (Page 3): Allocation Channels & HYSAs")
            st.write("Emergency capital must never be exposed to market volatility; it belongs strictly in secure, highly liquid accounts. However, keeping this cash in traditional checking accounts causes its purchasing power to slowly erode due to inflation.")
            st.write("The ideal home for an emergency fund is a High-Yield Savings Account (HYSA). HYSAs offer identical liquidity to basic bank accounts but pay substantially higher interest yields, allowing your safety net to grow alongside inflation.")
        elif p_idx == 4:
            st.markdown("### 🎯 Course 5 Assessment: The Emergency Fund Quiz")
            ans = st.radio("Where should your 3-6 month cash liquidity safety buffers be positioned?", ["Inside volatile technology equity options", "Inside a secure High-Yield Savings Account (HYSA)", "Inside a non-interest cash envelope at home"])
            if st.button("Submit Module Quiz Entry"):
                if ans == "Inside a secure High-Yield Savings Account (HYSA)": st.success("Correct! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute()
                else: st.error("Incorrect. Emergency reserves must stay in low-risk, highly accessible environments that still generate yield to outpace inflation.")

    elif c_idx == 5:  # Course 6: Side-Hustle Taxes
        if p_idx == 1:
            st.markdown("### 🧾 Course 6 (Page 1): The Realities of the 1099 Economy")
            st.write("Generating cash flow outside a standard corporate payroll architecture (e.g., freelance consulting, digital design contracts, app-based ride-sharing, or running an online store) reclassifies your identity in the eyes of tax authorities.")
            st.write("You are no longer an employee; you are a sole proprietor. Instead of receiving a standard W-2 tax form, your earnings will be summarized on a **1099-NEC** form, altering your tax obligations.")
        elif p_idx == 2:
            st.markdown("### 🧾 Course 6 (Page 2): Self-Employment Tax Metrics")
            st.write("When you work as a traditional employee, the company automatically pays half of your Social Security and Medicare taxes behind the scenes. When you operate as an independent freelancer, you become responsible for both halves.")
            st.write("This combined liability is known as the **Self-Employment Tax**, which adds a flat base rate of 15.3% on top of your regular federal and state income tax brackets. This applies to any net freelance income that crosses over $400 in a calendar year.")
        elif p_idx == 3:
            st.markdown("### 🧾 Course 6 (Page 3): Proactive Retention & Deductions")
            st.write("Because independent income platforms distribute payouts without withholding taxes, you must act as your own payroll manager. A vital rule of thumb is to automatically route **25-30% of every freelance payment** into a separate tax holding account.")
            st.write("To reduce this tax liability, track all business-related expenses—such as software tools, computing hardware, or project supplies—which can be deducted directly from your gross earnings to lower your taxable income.")
        elif p_idx == 4:
            st.markdown("### 🎯 Course 6 Assessment: The Side-Hustle Tax Quiz")
            ans = st.radio("What percentage baseline threshold of gross freelance earnings should an operator proactively retain to cover tax liabilities?", ["Roughly 5% to 10%", "Roughly 25% to 30%", "Exactly 0% until graduation milestones are achieved"])
            if st.button("Submit Module Quiz Entry"):
                if ans == "Roughly 25% to 30%": st.success("Correct! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute()
                else: st.error("Incorrect. Freelancers must retain 25-30% of their gross receipts to prevent severe penalty assessments during annual filings.")

    elif c_idx == 6:  # Course 7: Inflation
        if p_idx == 1:
            st.markdown("### 💸 Course 7 (Page 1): The Hidden Erosion of Capital")
            st.write("Inflation represents the continuous, widespread increase in prices across an economy, which causes a currency's purchasing power to drop over time. When macro inflation tracks at an annual rate of 3%, a basket of groceries that costs $100 today will require $103 next year.")
            st.write("Inflation acts as a invisible tax on cash. If your money isn't actively generating yields that outpace this rate, your purchasing power is shrinking, even if the nominal balance on your screen stays exactly the same.")
        elif p_idx == 2:
            st.markdown("### 💸 Course 7 (Page 2): Real vs. Nominal Returns")
            st.write("To track your true wealth expansion, you must calculate the critical difference between your **Nominal Return** (the raw interest rate printed on your account statement) and your **Real Return** (your actual purchasing power adjusted for inflation).")
            st.latex(r"Real\ Return \approx Nominal\ Return - Inflation\ Rate")
            st.write("If a traditional checking account pays you 0.01% interest while the surrounding economy experiences 4% inflation, your real return is -3.99%, representing a guaranteed loss of future wealth.")
        elif p_idx == 3:
            st.markdown("### 💸 Course 7 (Page 3): Hedging with Productive Assets")
            st.write("Beating inflation requires moving beyond pure cash storage and deploying capital into productive, inflation-resistant assets. Productive assets include equities, index funds, and real estate.")
            st.write("These assets historically outpace inflation because businesses can raise their prices to track rising costs, and real estate values adjust alongside broader economic scaling, keeping your net worth intact.")
        elif p_idx == 4:
            st.markdown("### 🎯 Course 7 Assessment: The Inflation Quiz")
            ans = st.radio("If an investment generates a 6% nominal interest return during an economic phase experiencing 4% inflation, what is the true approximate real yield?", ["+10.00%", "+2.00%", "-2.00%"])
            if st.button("Submit Module Quiz Entry"):
                if ans == "+2.00%": st.success("Correct! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute()
                else: st.error("Incorrect. Subtract the 4% inflation rate from your 6% nominal gain to determine your actual real purchasing power adjustment.")

    elif c_idx == 7:  # Course 8: Debt Leverage
        if p_idx == 1:
            st.markdown("### ⚖️ Course 8 (Page 1): The Arbitrage of Debt Liability")
            st.write("In consumer financial media, debt is often portrayed as an absolute negative that must be avoided entirely. However, professional wealth management treats debt as a tool evaluated by its structural cost and leverage potential.")
            st.write("The dividing line between productive leverage and toxic liability is determined by your interest rate. High-cost liabilities destroy cash flow, while low-cost liabilities can be managed strategically to build wealth.")
        elif p_idx == 2:
            st.markdown("### ⚖️ Course 8 (Page 2): Toxic High-Cost Liabilities")
            st.write("High-cost debt is defined as any liability carrying an interest rate higher than the average historical return of the broad stock market (roughly 7-8%). The primary example is credit card debt, which frequently averages between 20% and 30% interest.")
            st.write("Attempting to invest in index funds while carrying a balance on a 24% credit card is mathematically broken. Clearing that debt provides a guaranteed 24% return on your money by instantly stopping those heavy interest losses.")
        elif p_idx == 3:
            st.markdown("### ⚖️ Course 8 (Page 3): Strategic Low-Cost Capital")
            st.write("Low-cost debt carries an interest rate well below average market returns, typically tracking under 4-5%. This category can include subsidized student loans or long-term mortgages.")
            st.write("If you hold a student loan locked at a 3% interest rate, paying it down aggressively ahead of schedule can actually be an opportunity cost. You can build wealth faster by making your standard payments and routing your extra savings into index funds yielding 8%.")
        elif p_idx == 4:
            st.markdown("### 🎯 Course 8 Assessment: The Debt Leverage Quiz")
            ans = st.radio("What is the most mathematically optimal strategy for managing a $1,000 credit card debt balance at 25% interest?", ["Make minimum payments and route surplus cash directly into index funds", "Pay off the credit card balance immediately to lock in a guaranteed 25% savings return", "Hold matching capital amounts inside standard checking lines"])
            if st.button("Submit Module Quiz Entry"):
                if ans == "Pay off the credit card balance immediately to lock in a guaranteed 25% savings return": st.success("Correct! +25 XP Added."); supabase.table("profiles").update({"points": current_points + 25}).eq("username", username).execute()
                else: st.error("Incorrect. Eliminating a 25% interest liability is structurally identical to earning a guaranteed 25% return on your investment capital.")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- SUB-PAGE PAGINATION CONTROLLER DECK ---
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if p_idx > 1:
            if st.button("⬅️ Previous Page", use_container_width=True):
                st.session_state.page_idx -= 1
                st.rerun()
    with nav_col3:
        if p_idx < 4:
            if st.button("Next Page ➡️", use_container_width=True):
                st.session_state.page_idx += 1
                st.rerun()

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
