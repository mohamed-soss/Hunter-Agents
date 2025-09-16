from google.oauth2.service_account import Credentials
import gspread
import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import io

# Setup Google Sheets connection
scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
client = gspread.authorize(creds)

# Open the Google Sheet using provided Sheet ID
SHEET_ID = "1PzBTiG0XkMOlnq0o-rO80_tg252nxtxOt5-aX1h0ivc"
try:
    sheet = client.open_by_key(SHEET_ID)
except Exception as e:
    st.error(f"Failed to open sheet: {e}")
    raise

# Function to create sheet if not exists
def create_sheet_if_not_exists(sheet_name, headers):
    try:
        worksheet = sheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
        worksheet.append_row(headers)
    return worksheet

# Initialize sheets with headers
AGENTS_HEADERS = ['Agent Name', 'Agent Code']
CALLBACKS_HEADERS = ['Agent Name', 'Full Name', 'Address', 'MCN', 'DOB', 'Number', 'Notes', 'Medical Conditions', 'CB Date', 'CB Timing', 'CB Type']
CHECKS_HEADERS = ['Agent Name', 'Plan', 'Date']

agents_sheet = create_sheet_if_not_exists("Agents", AGENTS_HEADERS)
callbacks_sheet = create_sheet_if_not_exists("Callbacks", CALLBACKS_HEADERS)
checks_sheet = create_sheet_if_not_exists("Checks", CHECKS_HEADERS)

# Function to get data as DataFrame
def get_df(worksheet):
    data = worksheet.get_all_values()
    return pd.DataFrame(data[1:], columns=data[0]) if len(data) > 1 else pd.DataFrame(columns=data[0])

# Streamlit config
st.set_page_config(
    page_title="Hunter International",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    .main {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
        background: #F9FAFB;
    }
    .header {
        font-size: 3rem;
        font-weight: 700;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 2.5rem;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.9) 0%, rgba(59, 130, 246, 0.7) 100%);
        border-radius: 16px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
        animation: slideInDown 1s ease-out;
    }
    .subheader {
        font-size: 2rem;
        font-weight: 600;
        color: #1E40AF;
        margin-bottom: 2rem;
        animation: fadeInUp 0.8s ease-out;
    }
    .card {
        background: #FFFFFF;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 2.5rem;
        border-left: 6px solid #3B82F6;
        transition: all 0.4s ease;
        animation: slideInLeft 0.8s ease-out;
    }
    .card:hover {
        transform: translateY(-6px);
        box-shadow: 0 15px 50px rgba(59, 130, 246, 0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
        color: #FFFFFF;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
        transition: all 0.4s ease;
        animation: fadeIn 1s ease-out;
    }
    .metric-card:hover {
        transform: scale(1.08);
        box-shadow: 0 15px 50px rgba(59, 130, 246, 0.4);
    }
    .stButton > button {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 12px;
        padding: 1.4rem 3rem;
        font-weight: 600;
        font-size: 1.3rem;
        backdrop-filter: blur(5px);
        background-color: rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(30, 58, 138, 0.3);
        transition: all 0.4s ease, transform 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2A5B9E 0%, #4DA0FA 100%);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(30, 58, 138, 0.4);
    }
    .stButton > button:active {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 58, 138, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Session state
if 'page' not in st.session_state:
    st.session_state.page = 'control_hub'
if 'agent_name' not in st.session_state:
    st.session_state.agent_name = None
if 'menu' not in st.session_state:
    st.session_state.menu = "Callbacks"

# Control Hub Page
if st.session_state.page == 'control_hub':
    st.markdown('<div class="header">Hunter Agents</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("User Portal", key="user_portal", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()
    with col2:
        if st.button("Admin Dashboard", key="admin_dashboard", use_container_width=True):
            st.session_state.page = 'admin'
            st.rerun()

# Login Page (User Portal)
elif st.session_state.page == 'login':
    st.markdown('<div class="header">User Portal</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        agents_df = get_df(agents_sheet)
        if agents_df.empty:
            sample_agents = [['John Doe', 'JD123'], ['Jane Smith', 'JS456']]
            for row in sample_agents:
                agents_sheet.append_row(row)
            agents_df = get_df(agents_sheet)
        
        agent_names = agents_df['Agent Name'].tolist()
        selected_agent = st.selectbox("Select Your Name", agent_names)
        agent_code = st.text_input("Enter Your Code", type="password")
    
    if st.button("Login", use_container_width=True):
        matching_row = agents_df[
            (agents_df['Agent Name'] == selected_agent) & 
            (agents_df['Agent Code'] == agent_code)
        ]
        if not matching_row.empty:
            st.session_state.agent_name = selected_agent
            st.session_state.page = 'agent_dashboard'
            st.rerun()
        else:
            st.error("Invalid name or code.")
    
    if st.button("Back to Control Hub", use_container_width=True):
        st.session_state.page = 'control_hub'
        st.rerun()

# Agent Dashboard
elif st.session_state.page == 'agent_dashboard':
    st.markdown(
        f'<div class="header">Welcome, {st.session_state.agent_name}!</div>', 
        unsafe_allow_html=True
    )
    
    with st.sidebar:
        st.image("hunter logo-02.jpg", width=180)

        if st.button("Callbacks", use_container_width=True):
            st.session_state.menu = "Callbacks"
            st.rerun()

        if st.button("Add Check", use_container_width=True):
            st.session_state.menu = "Add Check"
            st.rerun()

        if st.button("My Analytics", use_container_width=True):
            st.session_state.menu = "My Analytics"
            st.rerun()

        if st.button("Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = 'control_hub'
            st.rerun()

        if st.button("Back to Control Hub", use_container_width=True):
            st.session_state.page = 'control_hub'
            st.rerun()

    menu = st.session_state.menu

    # ---------------- Callbacks ----------------
    if menu == "Callbacks":
        st.markdown('<div class="subheader">Submit New Callback</div>', unsafe_allow_html=True)
        with st.form(key="callback_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name")
                address = st.text_input("Address")
                mcn = st.text_input("MCN")
            with col2:
                dob = st.date_input("DOB")
                number = st.text_input("Number")
                cb_date = st.date_input("CB Date")
            
            col1, col2 = st.columns(2)
            with col1:
                notes = st.text_area("Notes", height=120)
                medical_conditions = st.text_area("Medical Conditions", height=120)
            with col2:
                cb_timing = st.text_input("CB Timing")
                cb_type = st.selectbox("CB Type", ["cold", "warm", "hot"])
            
            submit = st.form_submit_button("Submit Callback", use_container_width=True)
        
        if submit:
            new_row = [
                st.session_state.agent_name, full_name, address, mcn, str(dob), 
                number, notes, medical_conditions, str(cb_date), cb_timing, cb_type
            ]
            callbacks_sheet.append_row(new_row)
            st.success("Callback submitted successfully!")
            st.rerun()
        
        st.markdown('<div class="subheader">Your Callbacks</div>', unsafe_allow_html=True)
        callbacks_df = get_df(callbacks_sheet)
        agent_callbacks = callbacks_df[callbacks_df['Agent Name'] == st.session_state.agent_name].reset_index(drop=True)
        
        if not agent_callbacks.empty:
            for idx, row in agent_callbacks.iterrows():
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**{row['Full Name']}**")
                        st.markdown(f"{row['Address']} | {row['Number']}")
                        st.markdown(f"MCN: {row['MCN']} | DOB: {row['DOB']}")
                        st.markdown(f"Medical Conditions: {row['Medical Conditions'][:100]}...")
                        st.markdown(f"Notes: {row['Notes'][:100]}...")
                    with col2:
                        st.markdown(f"CB Date: {row['CB Date']}")
                        st.markdown(f"CB Timing: {row['CB Timing']}")
                        st.markdown(f"CB Type: {row['CB Type']}")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No callbacks yet.")

    # ---------------- Add Check ----------------
    elif menu == "Add Check":
        st.markdown('<div class="subheader">Add New Check</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            plan = st.selectbox("Select Plan", ["HMO", "PPO", "OPlan"])
        with col2:
            check_date = st.date_input("Check Date", value=datetime.date.today())
        
        if st.button("Add Check", use_container_width=True):
            new_row = [st.session_state.agent_name, plan, str(check_date)]
            checks_sheet.append_row(new_row)
            st.success("Check added successfully!")
            st.rerun()
        
        st.markdown('<div class="subheader">Your Check Summary</div>', unsafe_allow_html=True)
        checks_df = get_df(checks_sheet)
        agent_checks = checks_df[checks_df['Agent Name'] == st.session_state.agent_name]
        total_checks = len(agent_checks)
        checks_per_plan = agent_checks['Plan'].value_counts().to_dict()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Checks", total_checks)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("HMO", checks_per_plan.get('HMO', 0))
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("PPO", checks_per_plan.get('PPO', 0))
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("OPlan", checks_per_plan.get('OPlan', 0))
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- My Analytics ----------------
    elif menu == "My Analytics":
        st.markdown('<div class="subheader">Analytics Dashboard</div>', unsafe_allow_html=True)
        checks_df = get_df(checks_sheet)
        agent_checks = checks_df[checks_df['Agent Name'] == st.session_state.agent_name]
        
        col1, col2 = st.columns(2)
        with col1:
            if not agent_checks.empty:
                fig, ax = plt.subplots(figsize=(6, 4))
                agent_checks['Plan'].value_counts().plot(
                    kind='bar', ax=ax, color=['#3B82F6', '#60A5FA', '#93C5FD']
                )
                ax.set_title("Checks by Plan", fontsize=14, fontweight='bold')
                ax.set_ylabel("Count")
                plt.xticks(rotation=0)
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches='tight')
                buf.seek(0)
                st.image(buf.getvalue(), use_column_width=True)
            else:
                st.info("No data for visualization yet.")
        
        with col2:
            callbacks_df = get_df(callbacks_sheet)
            agent_callbacks = callbacks_df[callbacks_df['Agent Name'] == st.session_state.agent_name]
            cb_types = agent_callbacks['CB Type'].value_counts()
            if not cb_types.empty:
                fig, ax = plt.subplots(figsize=(6, 4))
                cb_types.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=['#3B82F6', '#60A5FA', '#93C5FD'])
                ax.set_title("Callbacks by Type", fontsize=14, fontweight='bold')
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches='tight')
                buf.seek(0)
                st.image(buf.getvalue(), use_column_width=True)

# ---------------- Admin Page ----------------
elif st.session_state.page == 'admin':
    st.markdown('<div class="header">Admin Dashboard</div>', unsafe_allow_html=True)
    
    password = st.text_input("Enter Admin Password", type="password", help="Password: admin1234")
    
    if password == "admin1234":
        st.success("Access Granted!")
        
        agents_df = get_df(agents_sheet)
        selected_agent = st.selectbox("Select Agent", agents_df['Agent Name'].tolist())
        
        tab1, tab2, tab3 = st.tabs(["Callbacks", "Checks", "Analytics"])
        
        with tab1:
            st.markdown(f'<div class="subheader">{selected_agent}\'s Callbacks</div>', unsafe_allow_html=True)
            callbacks_df = get_df(callbacks_sheet)
            agent_callbacks = callbacks_df[callbacks_df['Agent Name'] == selected_agent]
            if not agent_callbacks.empty:
                st.dataframe(agent_callbacks, use_container_width=True, hide_index=True)
            else:
                st.info("No callbacks.")
        
        with tab2:
            st.markdown(f'<div class="subheader">{selected_agent}\'s Checks</div>', unsafe_allow_html=True)
            checks_df = get_df(checks_sheet)
            agent_checks = checks_df[checks_df['Agent Name'] == selected_agent]
            if not agent_checks.empty:
                st.dataframe(agent_checks, use_container_width=True, hide_index=True)
                
                total_checks = len(agent_checks)
                checks_per_plan = agent_checks['Plan'].value_counts().to_dict()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Total", total_checks)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("HMO", checks_per_plan.get('HMO', 0))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("PPO", checks_per_plan.get('PPO', 0))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col4:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("OPlan", checks_per_plan.get('OPlan', 0))
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No checks.")
        
        with tab3:
            st.markdown(f'<div class="subheader">{selected_agent}\'s Analytics</div>', unsafe_allow_html=True)
            checks_df = get_df(checks_sheet)
            agent_checks = checks_df[checks_df['Agent Name'] == selected_agent]
            if not agent_checks.empty:
                fig, ax = plt.subplots(figsize=(6, 4))
                agent_checks['Plan'].value_counts().plot(kind='bar', ax=ax, color=['#3B82F6', '#60A5FA', '#93C5FD'])
                ax.set_title("Checks by Plan", fontsize=14, fontweight='bold')
                ax.set_ylabel("Count")
                plt.xticks(rotation=0)
                st.pyplot(fig)
            else:
                st.info("No checks yet for visualization.")
    else:
        st.error("Invalid password.")
    
    if st.button("Back to Control Hub", use_container_width=True):
        st.session_state.page = 'control_hub'
        st.rerun()


