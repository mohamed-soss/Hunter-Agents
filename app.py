from google.oauth2.service_account import Credentials
import gspread
import streamlit as st
import pandas as pd
import datetime
import time

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
    page_title="Hunter Agents - Professional Portal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# BULLETPROOF CSS - Universal Selectors
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@400;700;900&display=swap');
    
    /* Universal Reset */
    * {
        box-sizing: border-box;
    }
    
    /* Global Styles */
    .stApp {
        background: transparent !important;
    }
    
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%) !important;
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }
    
    /* Animated Background */
    .animated-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        background: 
            radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
        animation: float 20s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(1deg); }
    }
    
    /* Header Styles */
    .hero-header {
        font-family: 'Playfair Display', serif !important;
        font-size: 4.5rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #00d4ff 0%, #ffffff 50%, #ff6b6b 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-align: center !important;
        margin-bottom: 3rem !important;
        padding: 3rem 2rem !important;
        position: relative !important;
        animation: glow 3s ease-in-out infinite alternate !important;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.5) !important;
    }
    
    @media (max-width: 768px) {
        .hero-header { font-size: 3rem !important; padding: 2rem 1rem !important; }
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.5)); }
        to { filter: drop-shadow(0 0 40px rgba(255, 107, 107, 0.5)); }
    }
    
    .subheader {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #ffffff 0%, #a8a8ff 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 2rem !important;
        position: relative !important;
    }
    
    .subheader::after {
        content: '' !important;
        position: absolute !important;
        bottom: -10px !important;
        left: 0 !important;
        width: 60px !important;
        height: 4px !important;
        background: linear-gradient(135deg, #00d4ff, #ff6b6b) !important;
        border-radius: 2px !important;
    }
    
    /* Universal Card Styling */
    [data-testid="column"] > div > div,
    .block-container > div,
    .stAlert,
    .stTabs,
    .stForm {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important;
        padding: 2rem !important;
        margin-bottom: 2rem !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Control Hub Cards - Specific */
    .control-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 2px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 3rem 2rem !important;
        text-align: center !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2) !important;
        margin: 1rem 0 !important;
    }
    
    .control-card::before {
        content: '' !important;
        position: absolute !important;
        top: -50% !important;
        left: -50% !important;
        width: 200% !important;
        height: 200% !important;
        background: conic-gradient(transparent, rgba(255, 255, 255, 0.1), transparent) !important;
        animation: rotate 4s linear infinite !important;
        pointer-events: none !important;
    }
    
    @keyframes rotate {
        100% { transform: rotate(360deg); }
    }
    
    .control-card:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 20px 60px rgba(0, 212, 255, 0.3) !important;
        border-color: #00d4ff !important;
    }
    
    .control-card h3 {
        font-family: 'Playfair Display', serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #ffffff, #00d4ff) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 1rem !important;
        color: transparent !important;
    }
    
    /* BULLETPROOF BUTTON STYLING */
    button, 
    [role="button"], 
    input[type="submit"], 
    .stButton button,
    div[role="button"] button,
    .css-1omf2se button,
    .css-1d391kg button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 50%, #0077aa 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3) !important;
        cursor: pointer !important;
        width: 100% !important;
        margin: 8px 0 !important;
        min-height: 48px !important;
        display: block !important;
        text-align: center !important;
    }
    
    /* All possible button hover states */
    button:hover, 
    [role="button"]:hover, 
    input[type="submit"]:hover,
    .stButton button:hover,
    div[role="button"] button:hover,
    .css-1omf2se button:hover,
    .css-1d391kg button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 35px rgba(0, 212, 255, 0.4) !important;
        background: linear-gradient(135deg, #0099cc 0%, #00d4ff 50%, #00b3ff 100%) !important;
    }
    
    button:active, 
    [role="button"]:active, 
    input[type="submit"]:active,
    .stButton button:active,
    div[role="button"] button:active,
    .css-1omf2se button:active,
    .css-1d391kg button:active {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
    }
    
    /* Form Elements - Universal */
    input, 
    select, 
    textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        padding: 14px 16px !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin-bottom: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
    }
    
    input:focus, 
    select:focus, 
    textarea:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1) !important;
        background: rgba(255, 255, 255, 0.15) !important;
        outline: none !important;
    }
    
    input::placeholder, 
    textarea::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Selectbox dropdown */
    [role="listbox"], 
    .rc-virtual-list {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Sidebar - Universal */
    section[data-testid="stSidebar"], 
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(15, 15, 35, 0.95) 0%, rgba(26, 26, 46, 0.95) 100%) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* DataFrame - Universal */
    .dataframe, 
    table {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .dataframe th, 
    table th {
        background: rgba(0, 212, 255, 0.2) !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
    }
    
    .dataframe td, 
    table td {
        border-color: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
    }
    
    /* Metric Cards */
    .metric-container {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        text-align: center !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
        margin: 1rem 0 !important;
    }
    
    .metric-container:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2) !important;
    }
    
    .metric-value {
        font-size: 3rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #00d4ff, #ff6b6b) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin-bottom: 0.5rem !important;
        color: transparent !important;
    }
    
    .metric-label {
        font-size: 1.1rem !important;
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 500 !important;
    }
    
    /* Callback Cards */
    .callback-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(255, 107, 107, 0.05) 100%) !important;
        border-left: 5px solid #00d4ff !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
    }
    
    .callback-card:hover {
        transform: translateX(8px) !important;
        box-shadow: 0 8px 30px rgba(0, 212, 255, 0.2) !important;
        border-left-color: #ff6b6b !important;
    }
    
    .callback-header {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin-bottom: 0.8rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }
    
    .callback-meta {
        font-size: 0.9rem !important;
        color: rgba(255, 255, 255, 0.7) !important;
        margin-bottom: 0.5rem !important;
    }
    
    .callback-notes {
        font-size: 0.85rem !important;
        color: rgba(255, 255, 255, 0.6) !important;
        line-height: 1.4 !important;
        max-height: 60px !important;
        overflow: hidden !important;
    }
    
    /* Status Badges */
    .status-badge {
        padding: 4px 12px !important;
        border-radius: 20px !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        display: inline-block !important;
    }
    
    .status-cold { background: rgba(255, 107, 107, 0.2) !important; color: #ff6b6b !important; border: 1px solid rgba(255, 107, 107, 0.3) !important; }
    .status-warm { background: rgba(255, 217, 61, 0.2) !important; color: #ffd93d !important; border: 1px solid rgba(255, 217, 61, 0.3) !important; }
    .status-hot { background: rgba(76, 175, 80, 0.2) !important; color: #4caf50 !important; border: 1px solid rgba(76, 175, 80, 0.3) !important; }
    
    /* Animations */
    @keyframes slideInUp {
        from { transform: translateY(50px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-50px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .slide-in-up { animation: slideInUp 0.8s ease-out !important; }
    .fade-in { animation: fadeIn 1s ease-out !important; }
    .slide-in-left { animation: slideInLeft 0.8s ease-out !important; }
    
    /* Success/Error Messages */
    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        border-left: 4px solid #00d4ff !important;
        background: rgba(0, 212, 255, 0.1) !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        padding: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        margin: 1rem 0 !important;
    }
    
    div[data-testid="stAlert"] [data-testid="stAlertMessage"] {
        color: #ffffff !important;
    }
    
    /* Tabs - Universal */
    div[data-testid="stTab"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        margin: 1rem 0 !important;
    }
    
    div[data-testid="stTab"] button {
        background: transparent !important;
        border-radius: 8px !important;
        color: rgba(255, 255, 255, 0.7) !important;
        margin: 2px !important;
        padding: 12px 24px !important;
        border: none !important;
    }
    
    div[data-testid="stTab"] button:hover {
        color: #00d4ff !important;
        background: rgba(0, 212, 255, 0.1) !important;
    }
    
    div[data-testid="stTab"] button[aria-selected="true"] {
        color: #00d4ff !important;
        background: rgba(0, 212, 255, 0.2) !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Animated Background
st.markdown('<div class="animated-bg"></div>', unsafe_allow_html=True)

# Session state
if 'page' not in st.session_state:
    st.session_state.page = 'control_hub'
if 'agent_name' not in st.session_state:
    st.session_state.agent_name = None
if 'menu' not in st.session_state:
    st.session_state.menu = "Callbacks"

# Loading Animation
with st.spinner('Initializing Hunter Agents Portal...'):
    time.sleep(0.5)

# Control Hub Page - Enhanced
if st.session_state.page == 'control_hub':
    # Hero Section
    st.markdown('<div class="hero-header slide-in-up">Hunter Agents</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: rgba(255,255,255,0.8); font-size: 1.2rem; margin-bottom: 4rem; font-family: Inter, sans-serif;">Professional insurance management system</div>', unsafe_allow_html=True)
    
    # Enhanced Control Cards
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="control-card fade-in">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: transparent !important; background: linear-gradient(135deg, #ffffff, #00d4ff) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; background-clip: text !important; font-family: Playfair Display, serif !important; font-size: 2rem !important; font-weight: 700 !important; margin-bottom: 1rem !important;">Agent Portal</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(255,255,255,0.8); margin-bottom: 2rem; font-family: Inter, sans-serif;">Access your personalized dashboard, submit callbacks, and track performance metrics</p>', unsafe_allow_html=True)
        if st.button("Enter Portal", key="user_portal"):
            st.session_state.page = 'login'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="control-card fade-in" style="animation-delay: 0.2s;">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: transparent !important; background: linear-gradient(135deg, #ffffff, #00d4ff) !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; background-clip: text !important; font-family: Playfair Display, serif !important; font-size: 2rem !important; font-weight: 700 !important; margin-bottom: 1rem !important;">Admin Console</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(255,255,255,0.8); margin-bottom: 2rem; font-family: Inter, sans-serif;">Complete system control, agent management, and performance analytics</p>', unsafe_allow_html=True)
        if st.button("Admin Access", key="admin_dashboard"):
            st.session_state.page = 'admin'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Login Page (User Portal) - Enhanced
elif st.session_state.page == 'login':
    st.markdown('<div class="hero-header slide-in-up">Secure Access</div>', unsafe_allow_html=True)
    
    # Enhanced login card
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="elite-card slide-in-up">', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; margin-bottom: 2rem;">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #00d4ff !important; margin-bottom: 0.5rem !important; font-family: Playfair Display, serif !important;">Agent Authentication</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(255,255,255,0.7) !important; font-family: Inter, sans-serif !important;">Please verify your identity to access the portal</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        agents_df = get_df(agents_sheet)
        if agents_df.empty:
            sample_agents = [['John Doe', 'JD123'], ['Jane Smith', 'JS456']]
            for row in sample_agents:
                agents_sheet.append_row(row)
            agents_df = get_df(agents_sheet)
        
        agent_names = agents_df['Agent Name'].tolist()
        selected_agent = st.selectbox("Select Your Name", agent_names, help="Choose your registered name")
        agent_code = st.text_input("Enter Your Access Code", type="password", help="Your unique agent code")
        
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("Login", key="login_submit"):
                matching_row = agents_df[
                    (agents_df['Agent Name'] == selected_agent) & 
                    (agents_df['Agent Code'] == agent_code)
                ]
                if not matching_row.empty:
                    st.session_state.agent_name = selected_agent
                    st.session_state.page = 'agent_dashboard'
                    st.success("Welcome back, Agent!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
        
        with col_btn2:
            if st.button("Back to Hub", key="back_to_hub"):
                st.session_state.page = 'control_hub'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Agent Dashboard - Enhanced
elif st.session_state.page == 'agent_dashboard':
    # Enhanced Header with Agent Info
    st.markdown(
        f'<div class="hero-header slide-in-up">Welcome, <span style="color: #00d4ff !important;">{st.session_state.agent_name}</span></div>', 
        unsafe_allow_html=True
    )
    
    # Enhanced Sidebar - Clean with just logo and navigation
    with st.sidebar:
        st.markdown('<div style="padding: 1rem; text-align: center;">', unsafe_allow_html=True)
        st.image("hunter logo-02.jpg", width=120)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Callbacks", key="menu_callbacks"):
            st.session_state.menu = "Callbacks"
            st.rerun()
        
        st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
        
        if st.button("Logout", key="agent_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = 'control_hub'
            st.rerun()
        
        if st.button("Control Hub", key="agent_back_hub"):
            st.session_state.page = 'control_hub'
            st.rerun()
        
        st.markdown('<div style="padding-top: 2rem; text-align: center; color: rgba(255,255,255,0.6); font-size: 0.8rem; font-family: Inter, sans-serif;">', unsafe_allow_html=True)
        st.markdown('Powered by Advanced Technology', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    menu = st.session_state.menu

    # Enhanced Callbacks Section
    if menu == "Callbacks":
        # Performance Metrics
        st.markdown('<div class="subheader slide-in-left">Your Performance Dashboard</div>', unsafe_allow_html=True)
        
        callbacks_df = get_df(callbacks_sheet)
        agent_callbacks = callbacks_df[callbacks_df['Agent Name'] == st.session_state.agent_name]
        total_callbacks = len(agent_callbacks)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown('<div class="metric-container fade-in">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{total_callbacks}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Callbacks</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-container fade-in" style="animation-delay: 0.1s;">', unsafe_allow_html=True)
            today = datetime.date.today()
            today_callbacks = len(agent_callbacks[agent_callbacks['CB Date'] == str(today)])
            st.markdown(f'<div class="metric-value">{today_callbacks}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Today\'s Activity</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-container fade-in" style="animation-delay: 0.2s;">', unsafe_allow_html=True)
            avg_rating = "N/A"
            if total_callbacks > 0:
                # Simple rating calculation based on CB type
                ratings = {'cold': 1, 'warm': 2, 'hot': 3}
                scores = [ratings.get(cb_type, 1) for cb_type in agent_callbacks['CB Type']]
                avg_rating = round(sum(scores) / len(scores), 1) if scores else "N/A"
            st.markdown(f'<div class="metric-value">{avg_rating}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Lead Quality</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit New Callback - Enhanced Form
        st.markdown('<div class="subheader slide-in-up">Submit New Callback</div>', unsafe_allow_html=True)
        
        with st.form(key="callback_form", clear_on_submit=True):
            st.markdown('<div class="elite-card slide-in-up">', unsafe_allow_html=True)
            
            # Enhanced form layout
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown('<div style="margin-bottom: 1.5rem;"><h4 style="color: #00d4ff !important; margin: 0 !important; font-family: Inter, sans-serif !important;">Client Information</h4></div>', unsafe_allow_html=True)
                full_name = st.text_input("Full Name *", placeholder="Enter client full name")
                address = st.text_input("Address", placeholder="Client address")
                mcn = st.text_input("MCN", placeholder="Medical Coverage Number")
                dob = st.date_input("Date of Birth", help="Client date of birth")
                number = st.text_input("Phone Number", placeholder="Contact number")
            
            with col2:
                st.markdown('<div style="margin-bottom: 1.5rem;"><h4 style="color: #ff6b6b !important; margin: 0 !important; font-family: Inter, sans-serif !important;">Callback Details</h4></div>', unsafe_allow_html=True)
                cb_date = st.date_input("Callback Date *", help="Preferred callback date")
                cb_timing = st.text_input("Preferred Time", placeholder="e.g., 2:00 PM")
                cb_type = st.selectbox("Lead Temperature", ["cold", "warm", "hot"], 
                                     format_func=lambda x: x.capitalize(),
                                     help="Cold: New lead, Warm: Interested, Hot: Ready to proceed")
            
            # Notes sections
            col1, col2 = st.columns([1, 1])
            with col1:
                notes = st.text_area("Additional Notes", height=100, 
                                   placeholder="Any additional information about the client...")
            with col2:
                medical_conditions = st.text_area("Medical Conditions", height=100,
                                                placeholder="List any relevant medical conditions...")
            
            # Submit section
            st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
            submit = st.form_submit_button("Submit Callback")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle form submission
        if submit and full_name and cb_date:
            new_row = [
                st.session_state.agent_name, full_name, address, mcn, str(dob), 
                number, notes, medical_conditions, str(cb_date), cb_timing, cb_type
            ]
            callbacks_sheet.append_row(new_row)
            st.success(f"Callback submitted successfully for {full_name}!")
            st.balloons()
            st.rerun()
        elif submit:
            st.warning("Please fill in required fields (Full Name & Callback Date)")
        
        # Enhanced Callbacks Display
        st.markdown('<div class="subheader slide-in-left">Your Callbacks</div>', unsafe_allow_html=True)
        
        if not agent_callbacks.empty:
            for idx, row in agent_callbacks.iterrows():
                status_class = f"status-{row['CB Type']}"
                with st.container():
                    st.markdown(f'''
                    <div class="callback-card fade-in" style="animation-delay: {idx * 0.1}s;">
                        <div class="callback-header">
                            <strong style="color: #ffffff !important;">{row["Full Name"]}</strong>
                            <span class="status-badge {status_class}">{row["CB Type"].capitalize()}</span>
                        </div>
                        <div class="callback-meta" style="color: rgba(255, 255, 255, 0.7) !important;">
                            Address: {row["Address"]} | Phone: {row["Number"]} | MCN: {row["MCN"]}
                        </div>
                        <div class="callback-meta" style="color: rgba(255, 255, 255, 0.7) !important;">
                            DOB: {row["DOB"]} | Date: {row["CB Date"]} | Time: {row["CB Timing"]}
                        </div>
                        <div class="callback-notes" style="color: rgba(255, 255, 255, 0.6) !important;">
                            Notes: {row["Notes"][:150]}{"..." if len(row["Notes"]) > 150 else ""}
                        </div>
                        <div class="callback-notes" style="color: rgba(255, 255, 255, 0.6) !important;">
                            Medical: {row["Medical Conditions"][:150]}{"..." if len(row["Medical Conditions"]) > 150 else ""}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            st.markdown('<div class="elite-card fade-in" style="text-align: center; padding: 3rem;">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #ffd93d !important; margin-bottom: 1rem !important; font-family: Inter, sans-serif !important;">Ready to Get Started</h3>', unsafe_allow_html=True)
            st.markdown('<p style="color: rgba(255,255,255,0.7) !important; font-family: Inter, sans-serif !important;">No callbacks yet. Submit your first callback above!</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Admin Page
elif st.session_state.page == 'admin':
    st.markdown('<div class="hero-header slide-in-up">Admin Console</div>', unsafe_allow_html=True)
    
    # Enhanced admin authentication
    auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])
    with auth_col2:
        st.markdown('<div class="elite-card slide-in-up">', unsafe_allow_html=True)
        password = st.text_input("Admin Access Code", type="password", 
                               placeholder="Enter admin credentials",
                               help="Contact IT for access code")
        
        if st.button("Verify Access", key="admin_verify"):
            if password == "admin1234":
                st.session_state.admin_access = True
                st.success("Admin Access Granted!")
                st.rerun()
            else:
                st.error("Access Denied. Invalid credentials.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Admin Dashboard Content
    if hasattr(st.session_state, 'admin_access') and st.session_state.admin_access:
        st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
        
        agents_df = get_df(agents_sheet)
        selected_agent = st.selectbox("Select Agent", 
                                    ['All Agents'] + agents_df['Agent Name'].tolist())
        
        tab1, tab2 = st.tabs(["Analytics Dashboard", "Agent Management"])
        
        with tab1:
            st.markdown('<div class="subheader">Performance Analytics</div>', unsafe_allow_html=True)
            st.markdown('<div class="elite-card">', unsafe_allow_html=True)
            
            callbacks_df = get_df(callbacks_sheet)
            if selected_agent == 'All Agents':
                agent_filter = callbacks_df
            else:
                agent_filter = callbacks_df[callbacks_df['Agent Name'] == selected_agent]
            
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            with col1:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{len(agent_filter)}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Total Callbacks</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                today_count = len(agent_filter[agent_filter['CB Date'] == str(datetime.date.today())])
                st.markdown(f'<div class="metric-value">{today_count}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Today\'s Leads</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                hot_leads = len(agent_filter[agent_filter['CB Type'] == 'hot'])
                st.markdown(f'<div class="metric-value">{hot_leads}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Hot Leads</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col4:
                st.markdown('<div class="metric-container">', unsafe_allow_html=True)
                avg_response = round(len(agent_filter) / len(agents_df), 1) if agents_df.shape[0] > 0 else 0
                st.markdown(f'<div class="metric-value">{avg_response}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Avg/Agent</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced Data Display
            st.markdown(f'<div class="subheader">{selected_agent}\'s Callbacks</div>', unsafe_allow_html=True)
            if not agent_filter.empty:
                st.markdown('<div class="elite-card">', unsafe_allow_html=True)
                st.dataframe(agent_filter, hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info(f"No callbacks found for {selected_agent}")
        
        with tab2:
            st.markdown('<div class="subheader">Agent Management</div>', unsafe_allow_html=True)
            st.markdown('<div class="elite-card">', unsafe_allow_html=True)
            
            # Enhanced Agent Display
            st.markdown('<h4 style="color: #00d4ff !important; margin-bottom: 1.5rem !important; font-family: Inter, sans-serif !important;">Current Agents</h4>', unsafe_allow_html=True)
            if not agents_df.empty:
                for idx, agent in agents_df.iterrows():
                    with st.container():
                        st.markdown(f'''
                        <div class="callback-card" style="margin-bottom: 1rem !important;">
                            <div style="display: flex !important; justify-content: space-between !important; align-items: center !important;">
                                <div>
                                    <strong style="color: #ffffff !important;">{agent["Agent Name"]}</strong>
                                    <span style="color: rgba(255,255,255,0.6) !important; margin-left: 1rem !important; font-family: Inter, sans-serif !important;">Code: {agent["Agent Code"]}</span>
                                </div>
                                <div style="text-align: right !important;">
                                    <span style="color: #4caf50 !important; font-weight: 600 !important; font-family: Inter, sans-serif !important;">ACTIVE</span>
                                </div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
            else:
                st.warning("No agents registered yet.")
            
            # Enhanced Agent Creation
            st.markdown('<h4 style="color: #ff6b6b !important; margin: 2rem 0 1rem 0 !important; font-family: Inter, sans-serif !important;">Add New Agent</h4>', unsafe_allow_html=True)
            
            with st.form(key="agent_form", clear_on_submit=True):
                col1, col2 = st.columns([1, 1])
                with col1:
                    new_agent_name = st.text_input("Agent Name *", 
                                                 placeholder="Full name of new agent")
                with col2:
                    new_agent_code = st.text_input("Access Code *", 
                                                 type="password",
                                                 placeholder="Generate unique code")
                
                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    add_agent = st.form_submit_button("Add Agent")
                with col_btn2:
                    if st.form_submit_button("Reset Form"):
                        st.rerun()
                
                if add_agent and new_agent_name and new_agent_code:
                    new_row = [new_agent_name, new_agent_code]
                    agents_sheet.append_row(new_row)
                    st.success(f"Welcome aboard, {new_agent_name}! Agent added successfully!")
                    st.balloons()
                    st.rerun()
                elif add_agent:
                    st.error("Please complete all required fields")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Admin Controls
        st.markdown('<div style="text-align: center; margin-top: 3rem;">', unsafe_allow_html=True)
        if st.button("Logout Admin", key="admin_logout"):
            if hasattr(st.session_state, 'admin_access'):
                del st.session_state.admin_access
            st.session_state.page = 'control_hub'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Back to hub button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Control Hub", key="admin_back_hub"):
            st.session_state.page = 'control_hub'
            st.rerun()

# Footer
st.markdown('''
<div style="
    text-align: center !important; 
    padding: 3rem 1rem 1rem 1rem !important; 
    color: rgba(255,255,255,0.4) !important; 
    font-size: 0.9rem !important;
    border-top: 1px solid rgba(255,255,255,0.1) !important;
    margin-top: 3rem !important;
    font-family: Inter, sans-serif !important;
">
    <div style="margin-bottom: 1rem !important;">
        <strong style="color: #ffffff !important;">Hunter Agents</strong> | Professional Management System
    </div>
    <div style="color: rgba(255,255,255,0.6) !important;">
        © 2025 Powered by Advanced Technology | All Rights Reserved
    </div>
</div>
''', unsafe_allow_html=True)
