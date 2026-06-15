import streamlit as st
from supabase import create_client, Client
from postgrest.exceptions import APIError
import hashlib
import pandas as pd
import plotly.express as px

# --- SUPABASE SECURE CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- APP CONFIG & CUSTOM CSS THEME ---
st.set_page_config(page_title="FinSmart Platform", page_icon="💳", layout="wide")

# Custom UI styling injection for clean card aesthetic
st.markdown("""
    <style>
    .block-container {padding-top: 2rem;}
    .stCard {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #4A90E2;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_value_with_restore=True)

# --- SECURITY & AUTH ENGINE ---
def hash_password(password: str) -> str:
    """Returns a secure SHA-256 string hash of the user password."""
    return hashlib.sha256(password.encode()).hexdigest()

def fetch_user_profile(username):
    try:
        res = supabase.table("profiles").select("*").eq("username", username.strip().lower()).execute()
        return res.data[0] if res.data else None
    except APIError as e:
        st.error(f"Database Communication Error: {e.message}")
        return None

# --- STATE MANAGERS ---
if "username" not in st.session_state:
    st.session_state.username = None

# --- APP PAGES ---

def login_page():
    # Centered Header UI
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🎓 FinSmart Studio</h1>", unsafe_value_with_restore=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: gray;'>The Smart Interactive Financial Hub For Students & Founders</p>", unsafe_value_with_restore=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔒 Secure Login", "📝 Create Student Profile"])
        
        with tab1:
            with st.form("login_form"):
                user_input = st.text_input("Username").strip().lower()
                pass_input = st.text_input("Password", type="password")
                submit = st.form_submit_button("Log In to Dashboard", use_container_width=True)
                
                if submit:
                    if user_input and pass_input:
                        profile = fetch_user_profile(user_input)
                        if profile and profile['password_hash'] == hash_password(pass_input):
                            st.session_state.username = user_input
                            st.success(f"Successfully authenticated as {user_input}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or matching security password credentials.")
                    else:
                        st.warning("Please provide entries for all login credential inputs.")
                        
        with tab2:
            with st.form("reg_form"):
                st.markdown("##### Basic Credentials")
                new_user = st.text_input("Choose Unique Username").strip().lower()
                new_pass = st.text_input("Choose Strong Password", type="password")
                
                st.markdown("##### Personal Profile (Customizes App Context)")
                age = st.slider("Select Current Age", 14, 28, 19)
                occupation = st.selectbox("Current Activity Metric", ["High School Student", "College Undergraduate", "Student Freelancer", "Early-Stage Founder"])
                
                register_submit = st.form_submit_button("Complete Enrolment & Sign Up", use_container_width=True)
                
                if register_submit:
                    if new_user and new_pass:
                        if fetch_user_profile(new_user):
                            st.error("This username signature is already claimed by another user.")
                        else:
                            try:
                                supabase.table("profiles").insert({
                                    "username": new_user,
                                    "password_hash": hash_password(new_pass),
                                    "age": age,
                                    "occupation": occupation,
                                    "points": 0
                                }).execute()
                                st.success("Account securely provisioned! Proceed to the Login Tab.")
                            except APIError as e:
                                st.error(f"Failed to create ledger: {e.message}")
                    else:
                        st.warning("Both primary authentication metric input blocks are mandatory.")

def dashboard_page():
    username = st.session_state.username
    profile = fetch_user_profile(username)
    
    st.markdown(f"## 👋 Welcome back, {username.capitalize()}!")
    
    # Elegant Clean KPI Summary Ribbons
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="Profile Status", value=profile['occupation'] if profile else "Student")
    with m2:
        st.metric(label="Available Education Points", value=f"🏅 {profile['points'] if profile else 0} XP")
    with m3:
        st.metric(label="Default Safe Monthly Cap", value="$500.00")
        
    st.markdown("---")
    
    left_ui, right_ui = st.columns([1, 2])
    
    with left_ui:
        st.markdown("<div class='stCard'><h4>📉 Log Personal Expense</h4>", unsafe_value_with_restore=True)
        with st.form("expense_form", clear_on_submit=True):
            category = st.selectbox("Allocation Category", ["Food & Routine", "Academic Materials", "Housing & Utilities", "Leisure & Welfare", "Startup / Side-Hustle Investment"])
            amount = st.number_input("Transaction Cost ($)", min_value=0.50, step=1.00)
            add_expense = st.form_submit_button("Record Transaction Entry", use_container_width=True)
            
            if add_expense:
                try:
                    supabase.table("expenses").insert({"username": username, "category": category, "amount": amount}).execute()
                    st.toast("Expense appended safely!", icon="✅")
                    st.rerun()
                except APIError as e:
                    st.error(f"Failed to compile data: {e.message}")
        st.markdown("</div>", unsafe_value_with_restore=True)
                
    with right_ui:
        st.markdown("<h4>📊 Budget Visualization & Analytics Desk</h4>", unsafe_value_with_restore=True)
        try:
            res = supabase.table("expenses").select("*").eq("username", username).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                df['amount'] = df['amount'].astype(float)
                
                # Plotly Donut Chart
                fig = px.pie(df, values='amount', names='category', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                # Active Notification Warning Systems
                total_spent = df['amount'].sum()
                limit = 500.00
                ratio = min(total_spent / limit, 1.0)
                
                st.markdown(f"**Budget Consumption Status: ${total_spent:.2f} / ${limit:.2f}**")
                if total_spent > limit:
                    st.error(f"🚨 ACTION ALERT: Monthly threshold exceeded by **${total_spent - limit:.2f}**! Cool down discretionary luxury outlays.")
                elif total_spent > (limit * 0.8):
                    st.warning("⚠️ BUDGET NUDGE: You've consumed over 80% of your student parameters with multiple periods remaining.")
                else:
                    st.success("🍏 Looking good! Current spending limits remain within healthy fiscal bounds.")
            else:
                st.info("No expense objects mapped to this account signature. Use the logger matrix to start data visualization loops.")
        except APIError as e:
            st.error(f"Could not load tracking array: {e.message}")

def bill_splitting_page():
    st.markdown("## 👥 Shared Group Liability Engine")
    st.caption("Instantly divide shared expenses like rent, project supplies, or group meals.")
    
    st.markdown("<div class='stCard'>", unsafe_value_with_restore=True)
    with st.form("split_form"):
        col1, col2 = st.columns(2)
        with col1:
            total_bill = st.number_input("Total Invoice Sum ($)", min_value=1.00, step=5.00)
            payer = st.text_input("Settling Party Name", value="Myself")
        with col2:
            num_friends = st.number_input("Headcount Splitting (Including Self)", min_value=2, step=1)
            desc = st.text_input("Expense Purpose Description", value="Lab Project Materials")
            
        calculate = st.form_submit_button("Compute Group Balances", use_container_width=True)
        
        if calculate:
            share = total_bill / num_friends
            st.markdown(f"### 🎯 Calculation: **${share:.2f} per person**")
            st.info(f"💡 **Actionable Split Nudge Alert Sent:** Request **${share:.2f}** from each teammate to balance individual balances for '{desc}' paid by **{payer}**.")
    st.markdown("</div>", unsafe_value_with_restore=True)

def learning_page():
    st.markdown("## 🎓 Micro-Learning Academic Track")
    username = st.session_state.username
    profile = fetch_user_profile(username)
    
    try:
        res = supabase.table("courses").select("*").execute()
        courses = res.data
        
        if courses:
            titles = [c['title'] for c in courses]
            choice = st.selectbox("Select Active Interactive Course Module", titles)
            course = next(c for c in courses if c['title'] == choice)
            
            st.markdown(f"### 📘 {course['title']}")
            st.markdown(f"<div class='stCard'>{course['content']}</div>", unsafe_value_with_restore=True)
            
            st.markdown("#### Check Your Understanding")
            opts = ["Choose an explicit option...", course['option_a'], course['option_b'], course['option_c']]
            mapping = {"A": course['option_a'], "B": course['option_b'], "C": course['option_c']}
            
            answer = st.radio(course['question'], opts)
            
            if st.button("Submit Quiz Assessment Summary", use_container_width=True):
                if answer == "Choose an explicit option...":
                    st.warning("Please toggle a specific valid multiple-choice radio alternative.")
                elif answer == mapping[course['correct_option']]:
                    st.success("🎉 Correct execution! +10 Account XP added to student parameters.")
                    if profile:
                        try:
                            supabase.table("profiles").update({"points": profile['points'] + 10}).eq("username", username).execute()
                        except APIError:
                            pass
                else:
                    st.error("❌ Incorrect valuation calculation. Review module learning blocks and re-evaluate parameters.")
        else:
            st.info("No active micro-courses are indexed in the engine catalog databases currently.")
    except APIError as e:
        st.error(f"Unable to read courses matrix: {e.message}")

def professor_backend_page():
    st.markdown("## 👨‍🏫 Professor Curated Course Builder")
    st.caption("Author dynamic educational courses and multi-choice validation loops that deploy to students in real-time.")
    
    with st.form("prof_course_form", clear_on_submit=True):
        st.markdown("##### Course Framework Text Content")
        title = st.text_input("Module Title Block")
        content = st.text_area("Lesson Layout Text Content (Supports standard markdown parsing architecture)")
        
        st.markdown("---")
        st.markdown("##### Modular Interactive Evaluation Quiz Params")
        question = st.text_input("Target Evaluation Question")
        op_a = st.text_input("Option String A Alternative")
        op_b = st.text_input("Option String B Alternative")
        op_c = st.text_input("Option String C Alternative")
        correct = st.selectbox("Designated Solution Code Key", ["A", "B", "C"])
        
        publish = st.form_submit_button("Publish Module Live to Platform Catalogs", use_container_width=True)
        
        if publish:
            if title and content and question and op_a and op_b and op_c:
                try:
                    supabase.table("courses").insert({
                        "title": title, "content": content, "question": question,
                        "option_a": op_a, "option_b": op_b, "option_c": op_c, "correct_option": correct
                    }).execute()
                    st.success(f"Successfully compiled and deployed module tracking entity: '{title}'")
                except APIError as e:
                    st.error(f"Database rejected document compile protocol: {e.message}")
            else:
                st.warning("All input configurations are structural requirements for validation loops.")

# --- APPLICATION CONTROLLER NAVIGATION ROUTING ---
if st.session_state.username is None:
    login_page()
else:
    # Clean Left Sidebar Styling Layout Control Setup
    st.sidebar.markdown(f"🔮 User Session: **{st.session_state.username.upper()}**")
    if st.sidebar.button("🚪 Kill Active Authentication Session", use_container_width=True):
        st.session_state.username = None
        st.rerun()
        
    st.sidebar.markdown("---")
    
    pages = {
        "📊 Personal Finance Desk": dashboard_page,
        "👥 Team Liability Splitter": bill_splitting_page,
        "🎓 Academy Micro-Tracks": learning_page,
        "👨‍🏫 Professor CMS Port": professor_backend_page
    }
    
    selection = st.sidebar.radio("Application System Routing", list(pages.keys()))
    st.sidebar.markdown("---")
    st.sidebar.caption("FinSmart Studio Engine v2.0 • Secured via Supabase Remote Key Pairs")
    
    # Run the selected page execution routine
    pages[selection]()
