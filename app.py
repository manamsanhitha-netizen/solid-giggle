import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- SUPABASE SECURE CONFIGURATION ---
# Streamlit automatically fetches these from .streamlit/secrets.toml locally 
# or from the Advanced Settings panel on Streamlit Cloud.
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- APP CONFIG & SESSION STATE ---
st.set_page_config(page_title="FinSmart Student App", page_icon="🎓", layout="wide")

if "username" not in st.session_state:
    st.session_state.username = None

# --- HELPER DATABASE FUNCTIONS ---
def fetch_user_profile(username):
    res = supabase.table("profiles").select("*").eq("username", username).execute()
    return res.data[0] if res.data else None

def create_user_profile(username, age, occupation):
    supabase.table("profiles").insert({"username": username, "age": age, "occupation": occupation, "points": 0}).execute()

def update_user_points(username, current_points):
    supabase.table("profiles").update({"points": current_points + 10}).eq("username", username).execute()

# --- PAGES DEFINITIONS ---

def login_page():
    st.title("🚀 Welcome to FinSmart")
    st.subheader("The Student Personal Finance & Startup Launchpad")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register New Account"])
    
    with tab1:
        with st.form("login_form"):
            user_input = st.text_input("Enter Username").strip().lower()
            submit = st.form_submit_button("Log In")
            if submit:
                if user_input:
                    profile = fetch_user_profile(user_input)
                    if profile:
                        st.session_state.username = user_input
                        st.success(f"Welcome back, {user_input}!")
                        st.rerun()
                    else:
                        st.error("Username not found. Please register first.")
                else:
                    st.error("Please fill in a username.")
                    
    with tab2:
        with st.form("reg_form"):
            new_user = st.text_input("Choose Username").strip().lower()
            age = st.slider("Select your Age", 15, 30, 18)
            occupation = st.selectbox("Current Status / Occupation", ["High School Student", "College Student", "Freelancer", "Working Student"])
            register_submit = st.form_submit_button("Create Account")
            
            if register_submit:
                if new_user:
                    if fetch_user_profile(new_user):
                        st.error("Username already taken!")
                    else:
                        create_user_profile(new_user, age, occupation)
                        st.success("Account created successfully! You can now log in.")
                else:
                    st.error("Please provide a username.")

def dashboard_page():
    st.title("📊 Financial Command Center")
    username = st.session_state.username
    profile = fetch_user_profile(username)
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Logged-in User", value=username.capitalize())
    col2.metric(label="Occupation Profile", value=profile['occupation'] if profile else "N/A")
    col3.metric(label="🎓 Learning Reward Points", value=f"{profile['points'] if profile else 0} XP")
    
    st.markdown("---")
    
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        st.subheader("📉 Log an Expense")
        with st.form("expense_form", clear_on_submit=True):
            category = st.selectbox("Category", ["Food & Drinks", "Books & Study Material", "Rent & Utilities", "Entertainment", "Side Hustle Investment"])
            amount = st.number_input("Amount ($)", min_value=1.0, step=0.50)
            add_expense = st.form_submit_button("Track Expense")
            
            if add_expense:
                supabase.table("expenses").insert({"username": username, "category": category, "amount": amount}).execute()
                st.toast("Expense logged securely!", icon="💰")
                
    with right_col:
        st.subheader("📈 Monthly Spending Analysis")
        res = supabase.table("expenses").select("*").eq("username", username).execute()
        
        if res.data:
            df = pd.DataFrame(res.data)
            df['amount'] = df['amount'].astype(float)
            
            fig = px.pie(df, values='amount', names='category', title='Where Your Money Goes', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
            
            total_spent = df['amount'].sum()
            budget_limit = 500.00
            
            st.progress(min(total_spent / budget_limit, 1.0), text=f"Total Budget Used: ${total_spent:.2f} / ${budget_limit:.2f}")
            if total_spent > budget_limit:
                st.error(f"🚨 ALERT: You have exceeded your student monthly budget cap by ${total_spent - budget_limit:.2f}!")
            elif total_spent > (budget_limit * 0.8):
                st.warning("⚠️ CRITICAL BUDGET ALERT: You have consumed over 80% of your student spending limit.")
        else:
            st.info("No expenses tracked yet. Start budgeting using the left panel.")

def bill_splitting_page():
    st.title("👥 Student Friend Splitter Ledger")
    
    with st.form("split_form"):
        total_bill = st.number_input("Total Bill Amount ($)", min_value=1.0)
        num_friends = st.number_input("Number of friends splitting", min_value=2, step=1)
        payer = st.text_input("Who paid the initial bill? (e.g., 'Myself', 'Alex')")
        calculate = st.form_submit_button("Calculate Balances")
        
        if calculate:
            split_amount = total_bill / num_friends
            st.success(f"Calculation Complete: Each person owes **${split_amount:.2f}**.")
            st.info(f"💡 Actionable Alert Note: Send a request to everyone else for **${split_amount:.2f}** to reimburse **{payer}**.")

def learning_page():
    st.title("🎓 Micro-Learning & Accelerator Modules")
    
    username = st.session_state.username
    profile = fetch_user_profile(username)
    
    res = supabase.table("courses").select("*").execute()
    courses = res.data
    
    if courses:
        course_titles = [c['title'] for c in courses]
        selected_title = st.selectbox("Choose a micro-module lesson:", course_titles)
        
        course = next(c for c in courses if c['title'] == selected_title)
        
        st.markdown(f"### {course['title']}")
        st.info(course['content'])
        
        st.markdown("#### Test Your Knowledge")
        options = ["Select an answer...", course['option_a'], course['option_b'], course['option_c']]
        ans_map = {"A": course['option_a'], "B": course['option_b'], "C": course['option_c']}
        
        user_choice = st.radio(course['question'], options)
        
        if st.button("Submit Quiz Answer"):
            if user_choice == "Select an answer...":
                st.warning("Please choose an option.")
            elif user_choice == ans_map[course['correct_option']]:
                st.success("🎉 Correct answer! +10 Knowledge XP awarded to your user profile.")
                if profile:
                    update_user_points(username, profile['points'])
            else:
                st.error("❌ Incorrect. Try reading the module content again.")
    else:
        st.info("Your professors haven't uploaded any micro-courses yet.")

def professor_backend_page():
    st.title("👨‍🏫 Professor / Educator Administration Backend")
    
    with st.form("prof_course_form", clear_on_submit=True):
        title = st.text_input("Course/Module Title")
        content = st.text_area("Lesson Content")
        
        st.markdown("---")
        st.markdown("##### Accompanying Micro-Quiz Config")
        question = st.text_input("Interactive Question")
        op_a = st.text_input("Option A")
        op_b = st.text_input("Option B")
        op_c = st.text_input("Option C")
        correct = st.selectbox("Correct Option Code", ["A", "B", "C"])
        
        publish = st.form_submit_button("Publish Course Module Live")
        
        if publish:
            if title and content and question and op_a and op_b and op_c:
                supabase.table("courses").insert({
                    "title": title, "content": content, "question": question,
                    "option_a": op_a, "option_b": op_b, "option_c": op_c, "correct_option": correct
                }).execute()
                st.success(f"Successfully published '{title}' into student app database.")
            else:
                st.error("All text input fields must be filled to compile a course.")

# --- NAVIGATION ROUTER ROUTINE ---
if st.session_state.username is None:
    login_page()
else:
    st.sidebar.markdown(f"👤 Account: **{st.session_state.username.upper()}**")
    if st.sidebar.button("🚪 Disconnect/Log out"):
        st.session_state.username = None
        st.rerun()
        
    pages = {
        "Personal Dashboard": dashboard_page,
        "Friend Splitter Matrix": bill_splitting_page,
        "Student Academy Hub": learning_page,
        "Professor CMS Engine": professor_backend_page
    }
    
    selection = st.sidebar.radio("Navigate Application Modules", list(pages.keys()))
    st.sidebar.markdown("---")
    
    pages[selection]()
