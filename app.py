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

# Custom Components
def create_hero_header(title):
    """Create a beautiful hero header"""
    st.markdown(f"""
    <div style="
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
    ">
        {title}
    </div>
    <style>
    @keyframes glow {{
        from {{ filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.5)); }}
        to {{ filter: drop-shadow(0 0 40px rgba(255, 107, 107, 0.5)); }}
    }}
    @media (max-width: 768px) {{
        div[style*="4.5rem"] {{ font-size: 3rem !important; padding: 2rem 1rem !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

def create_subheader(title):
    """Create a beautiful subheader"""
    st.markdown(f"""
    <div style="
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #a8a8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        position: relative;
    ">
        {title}
    </div>
    <div style="
        position: absolute;
        bottom: -10px;
        left: 0;
        width: 60px;
        height: 4px;
        background: linear-gradient(135deg, #00d4ff, #ff6b6b);
        border-radius: 2px;
    "></div>
    """, unsafe_allow_html=True)

def create_card(title, content, card_class="elite-card"):
    """Create a beautiful card component"""
    st.markdown(f"""
    <div class="{card_class}" style="
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
    " onmouseover="this.style.transform='translateY(-12px) scale(1.02)'; this.style.boxShadow='0 20px 60px rgba(0, 0, 0, 0.4)'; this.style.borderColor='rgba(0, 212, 255, 0.3)'" 
       onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 8px 32px rgba(0, 0, 0, 0.3)'; this.style.borderColor='rgba(255, 255, 255, 0.1)'">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(135deg, #00d4ff, #ff6b6b, #ffd93d); transform: scaleX(0); transition: transform 0.4s ease;" 
             onmouseover="this.style.transform='scaleX(1)'"></div>
        <h3 style="color: #ffffff; font-family: 'Inter', sans-serif; font-weight: 600; margin-bottom: 1rem; font-size: 1.5rem;">
            {title}
        </h3>
        <div style="color: #ffffff; font-weight: 500; line-height: 1.6; font-family: 'Inter', sans-serif;">
            {content}
        </div>
    </div>
    <style>
    .{card_class} {{ animation: slideInUp 0.8s ease-out; }}
    @keyframes slideInUp {{
        from {{ transform: translateY(50px); opacity: 0; }}
        to {{ transform: translateY(0); opacity: 1; }}
    }}
    </style>
    """, unsafe_allow_html=True)

def create_metric_card(value, label, delay=0):
    """Create a beautiful metric card"""
    st.markdown(f"""
    <div class="metric-container" style="
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        margin: 1rem 0.5rem;
        animation: fadeIn 1s ease-out;
        animation-delay: {delay}s;
    " onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 12px 40px rgba(0, 212, 255, 0.2)'">
        <div class="metric-value" style="
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(135deg, #00d4ff, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        ">
            {value}
        </div>
        <div class="metric-label" style="
            font-size: 1.1rem;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 500;
        ">
            {label}
        </div>
    </div>
    <style>
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    .metric-container:hover {{
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2) !important;
    }}
    @media (max-width: 768px) {{
        .metric-container {{ margin: 0.5rem 0 !important; }}
    }}
    </style>
    """, unsafe_allow_html=True)

def create_callback_card(row_data, idx):
    """Create a beautiful callback card"""
    status_class = f"status-{row_data['CB Type']}"
    status_color = {"cold": "#ff6b6b", "warm": "#ffd93d", "hot": "#4caf50"}
    
    st.markdown(f"""
    <div class="callback-card fade-in" style="
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(255, 107, 107, 0.05) 100%);
        border-left: 5px solid #00d4ff;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        animation-delay: {idx * 0.1}s;
        font-family: 'Inter', sans-serif;
    " onmouseover="this.style.transform='translateX(8px)'; this.style.boxShadow='0 8px 30px rgba(0, 212, 255, 0.2)'; this.style.borderLeftColor='#ff6b6b'">
        <div class="callback-header" style="
            font-size: 1.3rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 10px;
        ">
            <strong>{row_data["Full Name"]}</strong>
            <span class="status-badge {status_class}" style="
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background: rgba(76, 175, 80, 0.2);
                color: {status_color.get(row_data['CB Type'], '#4caf50')};
                border: 1px solid rgba(76, 175, 80, 0.3);
            ">
                {row_data["CB Type"].capitalize()}
            </span>
        </div>
        <div class="callback-meta" style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.5rem;">
            Address: {row_data["Address"]} | Phone: {row_data["Number"]} | MCN: {row_data["MCN"]}
        </div>
        <div class="callback-meta" style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.5rem;">
            DOB: {row_data["DOB"]} | Date: {row_data["CB Date"]} | Time: {row_data["CB Timing"]}
        </div>
        <div class="callback-notes" style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); line-height: 1.4; max-height: 60px; overflow: hidden;">
            Notes: {row_data["Notes"][:150]}{"..." if len(str(row_data["Notes"])) > 150 else ""}
        </div>
        <div class="callback-notes" style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.6); line-height: 1.4; max-height: 60px; overflow: hidden;">
            Medical: {row_data["Medical Conditions"][:150]}{"..." if len(str(row_data["Medical Conditions"])) > 150 else ""}
        </div>
    </div>
    <style>
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateX(-20px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    .callback-card:hover {{
        transform: translateX(8px) !important;
        box-shadow: 0 8px 30px rgba(0, 212, 255, 0.2) !important;
        border-left-color: #ff6b6b !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def create_custom_button(label, key=None, on_click=None):
    """Create a beautiful custom button"""
    if on_click:
        if st.button(label, key=key, on_click=on_click):
            return True
    else:
        if st.button(label, key=key):
            return True
    return False

# Minimal CSS - Only for animations and backgrounds
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@400;700;900&display=swap');
    
    /* Minimal Background */
    .stApp {{
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%) !important;
    }}
    
    /* Sidebar Background */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(15, 15, 35, 0.95) 0%, rgba(26, 26, 46, 0.95) 100%) !important;
    }}
    
    /* Basic animations */
    @keyframes slideInUp {{
        from {{ transform: translateY(50px); opacity: 0; }}
        to {{ transform: translateY(0); opacity: 1; }}
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    @keyframes slideInLeft {{
        from {{ transform: translateX(-50px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    .slide-in-up {{ animation: slideInUp 0.8s ease-out; }}
    .fade-in {{ animation: fadeIn 1s ease-out; }}
    .slide-in-left {{ animation: slideInLeft 0.8s ease-out; }}
    
    /* Global text color */
    .stApp * {{
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }}
    
    /* Fix for dark text on white backgrounds */
    .stApp input, .stApp select, .stApp textarea {{
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }}
    
    .stApp input::placeholder {{
        color: rgba(255, 255, 255, 0.6) !important;
    }}
    
    /* DataFrame fix */
    .dataframe {{
        background: rgba(255, 255, 255, 0.05) !important;
        color: #ffffff !important;
    }}
    
    .dataframe th {{
        background: rgba(0, 212, 255, 0.2) !important;
        color: #ffffff !important;
    }}
    
    .dataframe td {{
        color: #ffffff !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Animated Background
st.markdown('<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; background: radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%); animation: float 20s ease-in-out infinite;"></div><style>@keyframes float {{0%, 100% {{ transform: translateY(0px) rotate(0deg); }}50% {{ transform: translateY(-20px) rotate(1deg); }}}}</style>', unsafe_allow_html=True)

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

# Control Hub Page
if st.session_state.page == 'control_hub':
    create_hero_header("Hunter Agents")
    st.markdown('<div style="text-align: center; color: rgba(255,255,255,0.8); font-size: 1.2rem; margin-bottom: 4rem; font-family: Inter, sans-serif;">Professional insurance management system</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        create_card("Agent Portal", """
        <div style="text-align: center;">
            <p style="color: rgba(255,255,255,0.8); margin-bottom: 2rem; font-family: Inter, sans-serif; line-height: 1.6;">
                Access your personalized dashboard, submit callbacks, 
                and track performance metrics
            </p>
        </div>
        """, "control-card fade-in")
        if create_custom_button("Enter Portal", key="user_portal"):
            st.session_state.page = 'login'
            st.rerun()
    
    with col2:
        create_card("Admin Console", """
        <div style="text-align: center;">
            <p style="color: rgba(255,255,255,0.8); margin-bottom: 2rem; font-family: Inter, sans-serif; line-height: 1.6;">
                Complete system control, agent management, 
                and performance analytics
            </p>
        </div>
        """, "control-card fade-in")
        if create_custom_button("Admin Access", key="admin_dashboard"):
            st.session_state.page = 'admin'
            st.rerun()

# Login Page
elif st.session_state.page == 'login':
    create_hero_header("Secure Access")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        create_card("Agent Authentication", """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h3 style="color: #00d4ff; margin-bottom: 0.5rem; font-family: Playfair Display, serif; font-size: 1.8rem;">
                Agent Authentication
            </h3>
            <p style="color: rgba(255,255,255,0.7); font-family: Inter, sans-serif;">
                Please verify your identity to access the portal
            </p>
        </div>
        """, "elite-card slide-in-up")
        
        agents_df = get_df(agents_sheet)
        if agents_df.empty:
            sample_agents = [['John Doe', 'JD123'], ['Jane Smith', 'JS456']]
            for row in sample_agents:
                agents_sheet.append_row(row)
            agents_df = get_df(agents_sheet)
        
        agent_names = agents_df['Agent Name'].tolist()
        selected_agent = st.selectbox("Select Your Name", agent_names, help="Choose your registered name")
        agent_code = st.text_input("Enter Your Access Code", type="password", help="Your unique agent code")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if create_custom_button("Login", key="login_submit"):
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
            if create_custom_button("Back to Hub", key="back_to_hub"):
                st.session_state.page = 'control_hub'
                st.rerun()

# Agent Dashboard
elif st.session_state.page == 'agent_dashboard':
    create_hero_header(f"Welcome, {st.session_state.agent_name}")
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div style="padding: 1rem; text-align: center;">', unsafe_allow_html=True)
        st.image("hunter logo-02.jpg", width=120)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if create_custom_button("Callbacks", key="menu_callbacks"):
            st.session_state.menu = "Callbacks"
            st.rerun()
        
        st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
        
        if create_custom_button("Logout", key="agent_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = 'control_hub'
            st.rerun()
        
        if create_custom_button("Control Hub", key="agent_back_hub"):
            st.session_state.page = 'control_hub'
            st.rerun()
        
        st.markdown('<div style="padding-top: 2rem; text-align: center; color: rgba(255,255,255,0.6); font-size: 0.8rem; font-family: Inter, sans-serif;">Powered by Advanced Technology</div>', unsafe_allow_html=True)

    menu = st.session_state.menu

    if menu == "Callbacks":
        create_subheader("Your Performance Dashboard")
        
        callbacks_df = get_df(callbacks_sheet)
        agent_callbacks = callbacks_df[callbacks_df['Agent Name'] == st.session_state.agent_name]
        total_callbacks = len(agent_callbacks)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            create_metric_card(total_callbacks, "Total Callbacks", 0)
        with col2:
            today = datetime.date.today()
            today_callbacks = len(agent_callbacks[agent_callbacks['CB Date'] == str(today)])
            create_metric_card(today_callbacks, "Today's Activity", 0.1)
        with col3:
            avg_rating = "N/A"
            if total_callbacks > 0:
                ratings = {'cold': 1, 'warm': 2, 'hot': 3}
                scores = [ratings.get(cb_type, 1) for cb_type in agent_callbacks['CB Type']]
                avg_rating = round(sum(scores) / len(scores), 1) if scores else "N/A"
            create_metric_card(avg_rating, "Lead Quality", 0.2)
        
        create_subheader("Submit New Callback")
        
        with st.form(key="callback_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<h4 style="color: #00d4ff; margin-bottom: 1.5rem; font-family: Inter, sans-serif;">Client Information</h4>')
                full_name = st.text_input("Full Name *", placeholder="Enter client full name")
                address = st.text_input("Address", placeholder="Client address")
                mcn = st.text_input("MCN", placeholder="Medical Coverage Number")
                dob = st.date_input("Date of Birth", help="Client date of birth")
                number = st.text_input("Phone Number", placeholder="Contact number")
            
            with col2:
                st.markdown('<h4 style="color: #ff6b6b; margin-bottom: 1.5rem; font-family: Inter, sans-serif;">Callback Details</h4>')
                cb_date = st.date_input("Callback Date *", help="Preferred callback date")
                cb_timing = st.text_input("Preferred Time", placeholder="e.g., 2:00 PM")
                cb_type = st.selectbox("Lead Temperature", ["cold", "warm", "hot"], 
                                     format_func=lambda x: x.capitalize(),
                                     help="Cold: New lead, Warm: Interested, Hot: Ready to proceed")
            
            col1, col2 = st.columns(2)
            with col1:
                notes = st.text_area("Additional Notes", height=100, 
                                   placeholder="Any additional information about the client...")
            with col2:
                medical_conditions = st.text_area("Medical Conditions", height=100,
                                                placeholder="List any relevant medical conditions...")
            
            col_submit, _ = st.columns([1, 3])
            with col_submit:
                submit = st.form_submit_button("Submit Callback")
        
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
        
        create_subheader("Your Callbacks")
        
        if not agent_callbacks.empty:
            for idx, row in agent_callbacks.iterrows():
                create_callback_card(row, idx)
        else:
            create_card("Ready to Get Started", """
            <div style="text-align: center; padding: 3rem;">
                <h3 style="color: #ffd93d; margin-bottom: 1rem; font-family: Inter, sans-serif; font-size: 1.8rem;">
                    Ready to Get Started
                </h3>
                <p style="color: rgba(255,255,255,0.7); font-family: Inter, sans-serif;">
                    No callbacks yet. Submit your first callback above!
                </p>
            </div>
            """, "elite-card fade-in")

# Admin Page
elif st.session_state.page == 'admin':
    create_hero_header("Admin Console")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        create_card("Admin Authentication", """
        <div style="text-align: center;">
            <h3 style="color: #00d4ff; margin-bottom: 2rem; font-family: Playfair Display, serif; font-size: 1.8rem;">
                Admin Access
            </h3>
            <p style="color: rgba(255,255,255,0.7); margin-bottom: 1rem; font-family: Inter, sans-serif;">
                Enter your admin access code
            </p>
        </div>
        """, "elite-card slide-in-up")
        
        password = st.text_input("Admin Access Code", type="password", 
                               placeholder="Enter admin credentials",
                               help="Contact IT for access code")
        
        if create_custom_button("Verify Access", key="admin_verify"):
            if password == "admin1234":
                st.session_state.admin_access = True
                st.success("Admin Access Granted!")
                st.rerun()
            else:
                st.error("Access Denied. Invalid credentials.")
    
    if hasattr(st.session_state, 'admin_access') and st.session_state.admin_access:
        st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
        
        agents_df = get_df(agents_sheet)
        selected_agent = st.selectbox("Select Agent", 
                                    ['All Agents'] + agents_df['Agent Name'].tolist())
        
        tab1, tab2 = st.tabs(["Analytics Dashboard", "Agent Management"])
        
        with tab1:
            create_subheader("Performance Analytics")
            
            callbacks_df = get_df(callbacks_sheet)
            if selected_agent == 'All Agents':
                agent_filter = callbacks_df
            else:
                agent_filter = callbacks_df[callbacks_df['Agent Name'] == selected_agent]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                create_metric_card(len(agent_filter), "Total Callbacks")
            with col2:
                today_count = len(agent_filter[agent_filter['CB Date'] == str(datetime.date.today())])
                create_metric_card(today_count, "Today's Leads")
            with col3:
                hot_leads = len(agent_filter[agent_filter['CB Type'] == 'hot'])
                create_metric_card(hot_leads, "Hot Leads")
            with col4:
                avg_response = round(len(agent_filter) / len(agents_df), 1) if agents_df.shape[0] > 0 else 0
                create_metric_card(avg_response, "Avg/Agent")
            
            create_subheader(f"{selected_agent}'s Callbacks")
            if not agent_filter.empty:
                create_card("Callback Data", "", "elite-card")
                st.dataframe(agent_filter, hide_index=True)
            else:
                st.info(f"No callbacks found for {selected_agent}")
        
        with tab2:
            create_subheader("Agent Management")
            
            create_card("Current Agents", "", "elite-card")
            st.markdown('<h4 style="color: #00d4ff; margin-bottom: 1.5rem; font-family: Inter, sans-serif;">Current Agents</h4>', unsafe_allow_html=True)
            
            if not agents_df.empty:
                for idx, agent in agents_df.iterrows():
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(255, 107, 107, 0.05) 100%);
                        border-left: 5px solid #00d4ff;
                        border-radius: 16px;
                        padding: 1.5rem;
                        margin-bottom: 1rem;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        font-family: Inter, sans-serif;
                    ">
                        <div>
                            <strong style="color: #ffffff;">{agent["Agent Name"]}</strong>
                            <span style="color: rgba(255,255,255,0.6); margin-left: 1rem;">Code: {agent["Agent Code"]}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: #4caf50; font-weight: 600;">ACTIVE</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No agents registered yet.")
            
            st.markdown('<h4 style="color: #ff6b6b; margin: 2rem 0 1rem 0; font-family: Inter, sans-serif;">Add New Agent</h4>', unsafe_allow_html=True)
            
            with st.form(key="agent_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    new_agent_name = st.text_input("Agent Name *", 
                                                 placeholder="Full name of new agent")
                with col2:
                    new_agent_code = st.text_input("Access Code *", 
                                                 type="password",
                                                 placeholder="Generate unique code")
                
                col_btn1, col_btn2 = st.columns(2)
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
        
        st.markdown('<div style="text-align: center; margin-top: 3rem;">', unsafe_allow_html=True)
        if create_custom_button("Logout Admin", key="admin_logout"):
            if hasattr(st.session_state, 'admin_access'):
                del st.session_state.admin_access
            st.session_state.page = 'control_hub'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if create_custom_button("Control Hub", key="admin_back_hub"):
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
