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

# Enhanced Custom CSS - Professional & Stunning Design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@400;700;900&display=swap');
    
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    
    .stApp {
        background: transparent;
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
        font-family: 'Playfair Display', serif;
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff 0%, #ffffff 50%, #ff6b6b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 3rem;
        padding: 3rem 2rem;
        position: relative;
        animation: glow 3s ease-in-out infinite alternate;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.5)); }
        to { filter: drop-shadow(0 0 40px rgba(255, 107, 107, 0.5)); }
    }
    
    .subheader {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #a8a8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        position: relative;
    }
    
    .subheader::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 0;
        width: 60px;
        height: 4px;
        background: linear-gradient(135deg, #00d4ff, #ff6b6b);
        border-radius: 2px;
    }
    
    /* Enhanced Cards */
    .elite-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .elite-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #00d4ff, #ff6b6b, #ffd93d);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }
    
    .elite-card:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        border-color: rgba(0, 212, 255, 0.3);
    }
    
    .elite-card:hover::before {
        transform: scaleX(1);
    }
    
    .elite-card-content {
        color: #ffffff;
        font-weight: 500;
        line-height: 1.6;
    }
    
    /* Control Hub Cards */
    .control-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.4s ease;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    }
    
    .control-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(transparent, rgba(255, 255, 255, 0.1), transparent);
        animation: rotate 4s linear infinite;
        pointer-events: none;
    }
    
    @keyframes rotate {
        100% { transform: rotate(360deg); }
    }
    
    .control-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 60px rgba(0, 212, 255, 0.3);
        border-color: #00d4ff;
    }
    
    .control-card h3 {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    /* Enhanced Buttons - Fixed for deprecation */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 50%, #0077aa 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 0.8rem 2rem !important;
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
        margin: 0.5rem 0 !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 35px rgba(0, 212, 255, 0.4) !important;
        background: linear-gradient(135deg, #0099cc 0%, #00d4ff 50%, #00b3ff 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
    }
    
    /* Form Submit Buttons */
    div[data-testid="column"]:div > div > div > button,
    .stForm > div > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 50%, #0077aa 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 1rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3) !important;
        cursor: pointer !important;
        width: 100% !important;
        margin-top: 1rem !important;
    }
    
    div[data-testid="column"]:div > div > div > button:hover,
    .stForm > div > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 35px rgba(0, 212, 255, 0.4) !important;
        background: linear-gradient(135deg, #0099cc 0%, #00d4ff 50%, #00b3ff 100%) !important;
    }
    
    /* Form Elements */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        color: #ffffff;
        font-weight: 500;
        padding: 14px 16px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        width: 100%;
        margin-bottom: 1rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
        background: rgba(255, 255, 255, 0.15);
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: rgba(255, 255, 255, 0.6);
    }
    
    /* Sidebar Enhancement */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(15, 15, 35, 0.95) 0%, rgba(26, 26, 46, 0.95) 100%);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* DataFrame Enhancement */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Metric Cards */
    .metric-container {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.8);
        font-weight: 500;
    }
    
    /* Callback Cards */
    .callback-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(255, 107, 107, 0.05) 100%);
        border-left: 5px solid #00d4ff;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .callback-card:hover {
        transform: translateX(8px);
        box-shadow: 0 8px 30px rgba(0, 212, 255, 0.2);
        border-left-color: #ff6b6b;
    }
    
    .callback-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .callback-meta {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 0.5rem;
    }
    
    .callback-notes {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.6);
        line-height: 1.4;
        max-height: 60px;
        overflow: hidden;
    }
    
    /* Status Badges */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-cold { background: rgba(255, 107, 107, 0.2); color: #ff6b6b; border: 1px solid rgba(255, 107, 107, 0.3); }
    .status-warm { background: rgba(255, 217, 61, 0.2); color: #ffd93d; border: 1px solid rgba(255, 217, 61, 0.3); }
    .status-hot { background: rgba(76, 175, 80, 0.2); color: #4caf50; border: 1px solid rgba(76, 175, 80, 0.3); }
    
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
    
    .slide-in-up { animation: slideInUp 0.8s ease-out; }
    .fade-in { animation: fadeIn 1s ease-out; }
    .slide-in-left { animation: slideInLeft 0.8s ease-out; }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-header { font-size: 3rem; padding: 2rem 1rem; }
        .control-card { padding: 2rem 1rem; margin-bottom: 1.5rem; }
        .elite-card { padding: 2rem 1.5rem; }
    }
    
    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        border-left: 4px solid #00d4ff;
        background: rgba(0, 212, 255, 0.1);
        color: #ffffff;
        font-weight: 500;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stError { border-left-color: #ff6b6b; background: rgba(255, 107, 107, 0.1); }
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
    st.markdown('<div style="text-align: center; color: rgba(255,255,255,0.8); font-size: 1.2rem; margin-bottom: 4rem;">Professional insurance management system</div>', unsafe_allow_html=True)
    
    # Enhanced Control Cards
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="control-card fade-in">', unsafe_allow_html=True)
        st.markdown('<h3>Agent Portal</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(255,255,255,0.8); margin-bottom: 2rem;">Access your personalized dashboard, submit callbacks, and track performance metrics</p>', unsafe_allow_html=True)
        if st.button("Enter Portal", key="user_portal"):
            st.session_state.page = 'login'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="control-card fade-in" style="animation-delay: 0.2s;">', unsafe_allow_html=True)
        st.markdown('<h3>Admin Console</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(255,255,255,0.8); margin-bottom: 2rem;">Complete system control, agent management, and performance analytics</p>', unsafe_allow_html=True)
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
        st.markdown('<h3 style="color: #00d4ff; margin-bottom: 0.5rem;">Agent Authentication</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(255,255,255,0.7);">Please verify your identity to access the portal</p>', unsafe_allow_html=True)
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
        f'<div class="hero-header slide-in-up">Welcome, <span style="color: #00d4ff;">{st.session_state.agent_name}</span></div>', 
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
        
        st.markdown('<div style="padding-top: 2rem; text-align: center; color: rgba(255,255,255,0.6); font-size: 0.8rem;">', unsafe_allow_html=True)
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
                st.markdown('<div style="margin-bottom: 1.5rem;"><h4 style="color: #00d4ff; margin: 0;">Client Information</h4></div>', unsafe_allow_html=True)
                full_name = st.text_input("Full Name *", placeholder="Enter client full name")
                address = st.text_input("Address", placeholder="Client address")
                mcn = st.text_input("MCN", placeholder="Medical Coverage Number")
                dob = st.date_input("Date of Birth", help="Client date of birth")
                number = st.text_input("Phone Number", placeholder="Contact number")
            
            with col2:
                st.markdown('<div style="margin-bottom: 1.5rem;"><h4 style="color: #ff6b6b; margin: 0;">Callback Details</h4></div>', unsafe_allow_html=True)
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
            st.markdown('<div class="elite-card" style="background: rgba(255, 107, 107, 0.1); border-left: 4px solid #ff6b6b; padding: 1rem; margin-bottom: 1rem;">Please fill in required fields (Full Name & Callback Date)</div>', unsafe_allow_html=True)
        
        # Enhanced Callbacks Display
        st.markdown('<div class="subheader slide-in-left">Your Callbacks</div>', unsafe_allow_html=True)
        
        if not agent_callbacks.empty:
            for idx, row in agent_callbacks.iterrows():
                with st.container():
                    status_class = f"status-{row['CB Type']}"
                    st.markdown(f'''
                    <div class="callback-card fade-in" style="animation-delay: {idx * 0.1}s;">
                        <div class="callback-header">
                            <strong>{row["Full Name"]}</strong>
                            <span class="status-badge {status_class}">{row["CB Type"].capitalize()}</span>
                        </div>
                        <div class="callback-meta">
                            Address: {row["Address"]} | Phone: {row["Number"]} | MCN: {row["MCN"]}
                        </div>
                        <div class="callback-meta">
                            DOB: {row["DOB"]} | Date: {row["CB Date"]} | Time: {row["CB Timing"]}
                        </div>
                        <div class="callback-notes">
                            Notes: {row["Notes"][:150]}{"..." if len(row["Notes"]) > 150 else ""}
                        </div>
                        <div class="callback-notes">
                            Medical: {row["Medical Conditions"][:150]}{"..." if len(row["Medical Conditions"]) > 150 else ""}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Edit form for this callback
                    with st.expander("Edit Callback"):
                        with st.form(key=f"edit_callback_form_{idx}", clear_on_submit=True):
                            edit_full_name = st.text_input("Full Name", value=row["Full Name"])
                            edit_address = st.text_input("Address", value=row["Address"])
                            edit_mcn = st.text_input("MCN", value=row["MCN"])
                            edit_dob = st.date_input("DOB", value=datetime.datetime.strptime(row["DOB"], '%Y-%m-%d') if row["DOB"] else datetime.date.today())
                            edit_number = st.text_input("Number", value=row["Number"])
                            edit_notes = st.text_area("Notes", value=row["Notes"])
                            edit_medical_conditions = st.text_area("Medical Conditions", value=row["Medical Conditions"])
                            edit_cb_date = st.date_input("CB Date", value=datetime.datetime.strptime(row["CB Date"], '%Y-%m-%d') if row["CB Date"] else datetime.date.today())
                            edit_cb_timing = st.text_input("CB Timing", value=row["CB Timing"])
                            edit_cb_type = st.selectbox("CB Type", ["cold", "warm", "hot"], index=["cold", "warm", "hot"].index(row["CB Type"]))
                            
                            edit_submit = st.form_submit_button("Update Callback")
                            
                            if edit_submit:
                                updated_row = [
                                    st.session_state.agent_name, edit_full_name, edit_address, edit_mcn, str(edit_dob), 
                                    edit_number, edit_notes, edit_medical_conditions, str(edit_cb_date), edit_cb_timing, edit_cb_type
                                ]
                                # Update the row in Google Sheets
                                # row.name is the original index in callbacks_df, add 2 for worksheet row (1 for header, 1 for 0-index)
                                callbacks_sheet.update(range_name=f"A{row.name + 2}:K{row.name + 2}", values=[updated_row])
                                st.success("Callback updated successfully!")
                                st.rerun()
        else:
            st.markdown('<div class="elite-card fade-in" style="text-align: center; padding: 3rem;">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: #ffd93d; margin-bottom: 1rem;">Ready to Get Started</h3>', unsafe_allow_html=True)
            st.markdown('<p style="color: rgba(255,255,255,0.7);">No callbacks yet. Submit your first callback above!</p>', unsafe_allow_html=True)
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
                avg_response = round(len(agent_filter) / len(agents_df), 1) if len(agents_df) > 0 else 0
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
            st.markdown('<h4 style="color: #00d4ff; margin-bottom: 1.5rem;">Current Agents</h4>', unsafe_allow_html=True)
            if not agents_df.empty:
                for idx, agent in agents_df.iterrows():
                    with st.container():
                        st.markdown(f'''
                        <div class="callback-card" style="margin-bottom: 1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong style="color: #ffffff;">{agent["Agent Name"]}</strong>
                                    <span style="color: rgba(255,255,255,0.6); margin-left: 1rem;">Code: {agent["Agent Code"]}</span>
                                </div>
                                <div style="text-align: right;">
                                    <span style="color: #4caf50; font-weight: 600;">ACTIVE</span>
                                </div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
            else:
                st.warning("No agents registered yet.")
            
            # Enhanced Agent Creation
            st.markdown('<h4 style="color: #ff6b6b; margin: 2rem 0 1rem 0;">Add New Agent</h4>', unsafe_allow_html=True)
            
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
    text-align: center; 
    padding: 3rem 1rem 1rem 1rem; 
    color: rgba(255,255,255,0.4); 
    font-size: 0.9rem;
    border-top: 1px solid rgba(255,255,255,0.1);
    margin-top: 3rem;
">
    <div style="margin-bottom: 1rem;">
        <strong>Hunter Agents</strong> | Professional Management System
    </div>
    <div>
        © 2025 Powered by Advanced Technology | All Rights Reserved
    </div>
</div>
''', unsafe_allow_html=True)
