from google.oauth2.service_account import Credentials
import gspread
import streamlit as st
import pandas as pd
import datetime

# Setup Google Sheets connection
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Fix private_key formatting (replace \n with real newlines)
service_account_info = dict(st.secrets["gcp_service_account"])
if isinstance(service_account_info.get("private_key"), str):
    service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")

creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
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

agents_sheet = create_sheet_if_not_exists("Agents", AGENTS_HEADERS)
callbacks_sheet = create_sheet_if_not_exists("Callbacks", CALLBACKS_HEADERS)

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

# Custom CSS for styling with black bold text and glow effect
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;800;900&display=swap');
    .main {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
        background: #F9FAFB;
    }
    .header {
        font-size: 3rem;
        font-weight: 900;
        color: #000000;
        text-align: center;
        margin-bottom: 2.5rem;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.85) 100%);
        border-radius: 16px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
        text-shadow: 0 0 10px rgba(0, 0, 0, 0.3), 0 0 20px rgba(0, 0, 0, 0.2), 0 0 30px rgba(0, 0, 0, 0.1);
        animation: slideInDown 1s ease-out;
        border: 2px solid rgba(0, 0, 0, 0.1);
    }
    .subheader {
        font-size: 2rem;
        font-weight: 800;
        color: #000000;
        margin-bottom: 2rem;
        text-shadow: 0 0 8px rgba(0, 0, 0, 0.3), 0 0 16px rgba(0, 0, 0, 0.2);
        animation: fadeInUp 0.8s ease-out;
    }
    .card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 251, 0.9) 100%);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 2.5rem;
        border-left: 6px solid #000000;
        transition: all 0.4s ease;
        animation: slideInLeft 0.8s ease-out;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    .card:hover {
        transform: translateY(-6px);
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
        text-shadow: 0 0 12px rgba(0, 0, 0, 0.4);
    }
    .card-content {
        color: #000000;
        font-weight: 700;
        text-shadow: 0 0 6px rgba(0, 0, 0, 0.2);
    }
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F3F4F6 100%);
        color: #000000;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.4s ease;
        animation: fadeIn 1s ease-out;
        border: 2px solid rgba(0, 0, 0, 0.1);
        font-weight: 800;
        text-shadow: 0 0 8px rgba(0, 0, 0, 0.3);
    }
    .metric-card:hover {
        transform: scale(1.08);
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
        text-shadow: 0 0 12px rgba(0, 0, 0, 0.4);
    }
    .stButton > button {
        background: linear-gradient(135deg, #000000 0%, #333333 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 12px;
        padding: 1.4rem 3rem;
        font-weight: 700;
        font-size: 1.3rem;
        backdrop-filter: blur(5px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.4s ease, transform 0.2s ease;
        text-shadow: 0 0 6px rgba(0, 0, 0, 0.5);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #333333 0%, #555555 100%);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }
    .stButton > button:active {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    .stTextInput > div > div > input {
        color: #000000;
        font-weight: 700;
        text-shadow: 0 0 4px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        padding: 12px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #000000;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
    }
    .stSelectbox > div > div > select {
        color: #000000;
        font-weight: 700;
        text-shadow: 0 0 4px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        padding: 12px;
    }
    .stDateInput > div > div > input {
        color: #000000;
        font-weight: 700;
        text-shadow: 0 0 4px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        padding: 12px;
    }
    .stTextArea > div > div > textarea {
        color: #000000;
        font-weight: 700;
        text-shadow: 0 0 4px rgba(0, 0, 0, 0.1);
        border: 2px solid rgba(0, 0, 0, 0.1);
        border-radius: 10px;
        padding: 12px;
    }
    .stDataFrame {
        color: #000000;
        font-weight: 700;
        text-shadow: 0 0 4px rgba(0, 0, 0, 0.1);
    }
    .stError, .stWarning, .stSuccess, .stInfo {
        color: #000000;
        font-weight: 700;
        text-shadow: 0 0 4px rgba(0, 0, 0, 0.1);
    }
    @keyframes slideInDown {
        from { transform: translateY(-100px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    @keyframes fadeInUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    @keyframes slideInLeft {
        from { transform: translateX(-50px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
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
                        st.markdown(f'<div class="card-content"><strong>{row["Full Name"]}</strong></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card-content">{row["Address"]} | {row["Number"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card-content">MCN: {row["MCN"]} | DOB: {row["DOB"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card-content">Medical Conditions: {row["Medical Conditions"][:100]}...</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card-content">Notes: {row["Notes"][:100]}...</div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div class="card-content">CB Date: {row["CB Date"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card-content">CB Timing: {row["CB Timing"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card-content">CB Type: {row["CB Type"]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No callbacks yet.")

# ---------------- Admin Page ----------------
elif st.session_state.page == 'admin':
    st.markdown('<div class="header">Admin Dashboard</div>', unsafe_allow_html=True)
    
    password = st.text_input("Enter Admin Password", type="password", help="Password: admin1234")
    
    if password == "admin1234":
        st.success("Access Granted!")
        
        agents_df = get_df(agents_sheet)
        selected_agent = st.selectbox("Select Agent", agents_df['Agent Name'].tolist())
        
        tab1, tab2 = st.tabs(["Callbacks", "Manage Agents"])
        
        with tab1:
            st.markdown(f'<div class="subheader">{selected_agent}\'s Callbacks</div>', unsafe_allow_html=True)
            callbacks_df = get_df(callbacks_sheet)
            agent_callbacks = callbacks_df[callbacks_df['Agent Name'] == selected_agent]
            if not agent_callbacks.empty:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.dataframe(agent_callbacks, use_container_width=True, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No callbacks.")
        
        with tab2:
            st.markdown('<div class="subheader">Manage Agents</div>', unsafe_allow_html=True)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            # Display all agents
            st.subheader("Current Agents")
            st.dataframe(agents_df, use_container_width=True, hide_index=True)
            
            # Add new agent form
            st.markdown("### Add New Agent")
            with st.form(key="add_agent_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    new_agent_name = st.text_input("Agent Name")
                with col2:
                    new_agent_code = st.text_input("Agent Code", type="password")
                
                add_agent = st.form_submit_button("Add Agent", use_container_width=True)
            
            if add_agent:
                if new_agent_name and new_agent_code:
                    new_row = [new_agent_name, new_agent_code]
                    agents_sheet.append_row(new_row)
                    st.success(f"Agent {new_agent_name} added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in both fields.")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        st.error("Invalid password.")
    
    if st.button("Back to Control Hub", use_container_width=True):
        st.session_state.page = 'control_hub'
        st.rerun()
