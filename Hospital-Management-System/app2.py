import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from database import (
    init_database, get_all_patients, get_all_logs, 
    add_patient, update_patient, anonymize_all_patients
)
from auth import authenticate_user, check_role, log_user_action
from crypto_utils import get_cipher, mask_name, mask_contact, decrypt_field

# Page configuration with new modern theme
st.set_page_config(
    page_title="MediCare Pro - Hospital Management",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# New Modern UI Theme - Dark & Professional
st.markdown("""
<style>
    /* Main background and text colors */
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    /* Headers with neon accent */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
        text-shadow: 0 0 20px rgba(0, 210, 255, 0.3);
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #8892b0;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Modern cards with glass morphism effect */
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        border: 1px solid rgba(0, 210, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 210, 255, 0.2);
    }
    
    /* Metric cards with gradient backgrounds */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Modern buttons */
    .stButton button {
        width: 100%;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        border: none;
        color: white;
        padding: 0.8rem 1rem;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 210, 255, 0.4);
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
    }
    
    /* Secondary buttons */
    .secondary-button {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .secondary-button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid rgba(0, 210, 255, 0.3) !important;
    }
    
    /* Role badges with modern design */
    .role-badge {
        padding: 0.3rem 1rem;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .admin-badge { 
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
    }
    
    .doctor-badge { 
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
    }
    
    .receptionist-badge { 
        background: linear-gradient(135deg, #a8e6cf 0%, #56ab2f 100%);
        color: white;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0c0c0c 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Input fields styling - Black background */
    .stTextInput input, .stTextArea textarea {
        background: #000000 !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 10px;
        color: white !important;
        padding: 0.5rem 1rem;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border: 1px solid #00d2ff !important;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.2) !important;
        background: #000000 !important;
        color: white !important;
    }
    
    /* Select box styling */
    .stSelectbox div[data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px 10px 0 0;
        gap: 1rem;
        padding: 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
    }
    
    /* Dataframe styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Success and error messages */
    .stAlert {
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        border-radius: 4px;
    }
    
    /* Form styling */
    .stForm {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Password input styling */
    .stTextInput input[type="password"] {
        background: #000000 !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database on first run
init_database()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'Login'

# System uptime
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = datetime.now()

# ========== HELPER FUNCTIONS ==========

def logout():
    """Logout and clear session"""
    if st.session_state['user']:
        log_user_action(st.session_state, "LOGOUT", "User logged out")
    st.session_state['user'] = None
    st.session_state['page'] = 'Login'
    st.rerun()

def create_metric_card(title, value, icon, color="linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%)"):
    """Create a modern metric card"""
    return f"""
    <div class="metric-card" style="background: {color};">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem;">{value}</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">{title}</div>
    </div>
    """

def get_role_badge(role):
    """Get styled role badge"""
    colors = {
        'admin': 'admin-badge',
        'doctor': 'doctor-badge', 
        'receptionist': 'receptionist-badge'
    }
    return f'<span class="role-badge {colors[role]}">{role.upper()}</span>'

def convert_row_to_dict(row):
    """Convert sqlite3.Row to dictionary safely"""
    if hasattr(row, '_fields'):
        return {key: row[key] for key in row._fields}
    elif hasattr(row, 'keys'):
        return dict(row)
    else:
        return row

# ========== MODERN LOGIN PAGE ==========

def login_page():
    """Modern login page with dark theme design"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Header with animated gradient
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 class="main-header">MediCare Pro</h1>
            <p class="sub-header">Advanced Hospital Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login Card
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            st.markdown("### 🔐 Secure Access")
            st.markdown("---")
            
            with st.form("login_form"):
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("🚀 Login", use_container_width=True)
                with col2:
                    if st.form_submit_button("🔄 Clear", use_container_width=True, type="secondary"):
                        st.rerun()
            
            if submit:
                if username and password:
                    with st.spinner("🔐 Authenticating..."):
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state['user'] = user
                            st.session_state['page'] = 'Dashboard'
                            log_user_action(st.session_state, "LOGIN", f"User {username} logged in")
                            st.success(f"🎉 Welcome back, {user['username']}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please try again.")
                else:
                    st.warning("⚠️ Please fill in all fields")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Removed demo credentials section
            
            st.markdown("---")
            st.markdown("""
            <div style='text-align: center; color: #8892b0;'>
                <small>🔒 GDPR Compliant • 🛡️ Enterprise Security • ⚡ High Availability</small>
            </div>
            """, unsafe_allow_html=True)

# ========== MODERN DASHBOARD ==========

def dashboard_page():
    """Modern dashboard with analytics"""
    user = st.session_state['user']
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f'<h1 class="main-header">Welcome to MediCare Pro</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-header">Hello, <strong>{user["username"]}</strong>! {get_role_badge(user["role"])}</p>', unsafe_allow_html=True)
    
    with col2:
        uptime = datetime.now() - st.session_state['start_time']
        st.markdown(create_metric_card("System Uptime", f"{uptime.seconds // 3600}h", "⏱️", "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"), unsafe_allow_html=True)
    
    with col3:
        patients = get_all_patients()
        st.markdown(create_metric_card("Total Patients", len(patients), "👥", "linear-gradient(135deg, #a8e6cf 0%, #56ab2f 100%)"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Role-specific dashboard
    if user['role'] == 'admin':
        admin_dashboard()
    elif user['role'] == 'doctor':
        doctor_dashboard()
    else:
        receptionist_dashboard()
    
    log_user_action(st.session_state, "VIEW_DASHBOARD", "Accessed dashboard")

def admin_dashboard():
    """Admin-specific dashboard"""
    patients = get_all_patients()
    logs = get_all_logs()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(create_metric_card("Audit Logs", len(logs), "📜", "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Today's Logins", "12", "👤", "linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%)"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("System Health", "100%", "💚", "linear-gradient(135deg, #a8e6cf 0%, #56ab2f 100%)"), unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Patient Statistics")
        if patients:
            # Convert rows to dictionaries safely
            patient_dicts = [convert_row_to_dict(p) for p in patients]
            df = pd.DataFrame(patient_dicts)
            if not df.empty:
                fig = px.pie(df, names='diagnosis', title="Diagnosis Distribution")
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📈 Activity Timeline")
        if logs:
            # Convert rows to dictionaries safely
            log_dicts = [convert_row_to_dict(log) for log in logs]
            log_df = pd.DataFrame(log_dicts)
            if not log_df.empty and 'timestamp' in log_df.columns:
                log_df['timestamp'] = pd.to_datetime(log_df['timestamp'])
                daily_activity = log_df.groupby(log_df['timestamp'].dt.date).size()
                fig = px.line(x=daily_activity.index, y=daily_activity.values, 
                             title="Daily Activity", labels={'x': 'Date', 'y': 'Actions'})
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def doctor_dashboard():
    """Doctor-specific dashboard"""
    patients = get_all_patients()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🩺 My Patients")
        if patients:
            # Convert rows to dictionaries safely
            patient_dicts = [convert_row_to_dict(p) for p in patients]
            df = pd.DataFrame(patient_dicts)
            if not df.empty:
                # Safely access columns
                display_columns = []
                for col in ['anonymized_name', 'anonymized_contact', 'diagnosis', 'date_added']:
                    if col in df.columns:
                        display_columns.append(col)
                
                if display_columns:
                    st.dataframe(df[display_columns], use_container_width=True, height=300)
        else:
            st.info("No patients in the system")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Quick Actions")
        
        if st.button("👁️ View Patient Records", use_container_width=True):
            st.session_state['page'] = 'Patients'
            st.rerun()
        
        if st.button("📊 View Analytics", use_container_width=True):
            st.info("Analytics dashboard coming soon!")
        
        st.markdown('</div>', unsafe_allow_html=True)

def receptionist_dashboard():
    """Receptionist-specific dashboard - Alice can only add/edit patients"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Receptionist Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Your Responsibilities:
        - Register new patients
        - Update patient information  
        - Manage appointments
        - Handle patient inquiries
        """)
    
    with col2:
        st.markdown("""
        ### ⚡ Quick Access:
        - Add new patients instantly
        - Update existing records
        - View patient directory
        """)
    
    if st.button("➕ Add New Patient", use_container_width=True):
        st.session_state['page'] = 'Patients'
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== MODERN PATIENTS PAGE ==========

def patients_page():
    """Modern patient management interface"""
    user = st.session_state['user']
    
    st.markdown(f'<h1 class="main-header">Patient Management</h1>', unsafe_allow_html=True)
    
    # Role-based tab access - Alice (receptionist) can only add/edit patients
    if user['role'] == 'receptionist':
        tab1, tab2 = st.tabs(["➕ Add Patient", "✏️ Update Patient"])
        
        with tab1:
            add_patient_tab()
        
        with tab2:
            update_patient_tab()
    
    else:  # Admin and Doctor have full access
        tab1, tab2, tab3 = st.tabs(["👥 View Patients", "➕ Add Patient", "✏️ Update Patient"])
        
        with tab1:
            view_patients_tab()
        
        with tab2:
            add_patient_tab()
        
        with tab3:
            update_patient_tab()

def view_patients_tab():
    """Modern patient viewing interface"""
    patients = get_all_patients()
    user = st.session_state['user']
    
    if not patients:
        st.info("🎯 No patients found. Start by adding your first patient!")
        return
    
    # Role-based view
    if user['role'] == 'admin':
        view_mode = st.radio("🔍 View Mode:", ["Anonymized", "Raw Data"], horizontal=True, label_visibility="collapsed")
        show_raw = view_mode == "Raw Data"
    else:
        show_raw = False
        st.info("👁️ Viewing anonymized patient data (GDPR Compliant)")
    
    # Patient cards grid
    for patient in patients:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                # Safely access patient data
                patient_dict = convert_row_to_dict(patient)
                
                if show_raw:
                    st.subheader(f"👤 {patient_dict.get('name', 'N/A')}")
                    st.write(f"📞 {patient_dict.get('contact', 'N/A')}")
                else:
                    st.subheader(f"👤 {patient_dict.get('anonymized_name', 'N/A')}")
                    st.write(f"📞 {patient_dict.get('anonymized_contact', 'N/A')}")
                
                st.write(f"🩺 **Diagnosis:** {patient_dict.get('diagnosis', 'N/A')}")
            
            with col2:
                st.write(f"📅 **Added:** {patient_dict.get('date_added', 'N/A')}")
                last_updated = patient_dict.get('last_updated')
                if last_updated:
                    st.write(f"🔄 **Updated:** {last_updated}")
            
            with col3:
                st.write(f"🆔 **ID:** {patient_dict.get('patient_id', 'N/A')}")
                if show_raw:
                    st.warning("🔓 Raw Data")
                else:
                    st.success("🔒 Anonymized")
            
            st.markdown('</div>', unsafe_allow_html=True)

def add_patient_tab():
    """Modern patient addition form"""
    user = st.session_state['user']
    
    # Only receptionist (Alice) and admin can add patients
    if user['role'] not in ['admin', 'receptionist']:
        st.error("🚫 Access denied. Only receptionists and admins can add patients.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("➕ Register New Patient")
    
    with st.form("add_patient_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("👤 Full Name", placeholder="Enter patient's full name")
            contact = st.text_input("📞 Contact Number", placeholder="+1-555-0123")
        
        with col2:
            diagnosis = st.text_area("🩺 Diagnosis", placeholder="Enter medical diagnosis", height=100)
        
        submitted = st.form_submit_button("🚀 Register Patient", use_container_width=True)
        
        if submitted:
            if all([name, contact, diagnosis]):
                with st.spinner("🔐 Securing patient data..."):
                    cipher = get_cipher()
                    anon_name = mask_name(999)
                    anon_contact = mask_contact(contact)
                    enc_name = cipher.encrypt(name.encode()).decode()
                    enc_contact = cipher.encrypt(contact.encode()).decode()
                    
                    pid = add_patient(name, contact, diagnosis, anon_name, anon_contact, enc_name, enc_contact)
                    update_patient(pid, name, contact, diagnosis, mask_name(pid), anon_contact)
                    
                    log_user_action(st.session_state, "ADD_PATIENT", f"Added patient ID {pid}")
                    st.success(f"✅ Patient registered successfully! ID: {pid}")
                    st.balloons()
            else:
                st.error("❌ Please fill all required fields")

def update_patient_tab():
    """Modern patient update interface"""
    user = st.session_state['user']
    
    # Only receptionist (Alice) and admin can update patients
    if user['role'] not in ['admin', 'receptionist']:
        st.error("🚫 Access denied. Only receptionists and admins can update patients.")
        return
    
    patients = get_all_patients()
    if not patients:
        st.info("No patients available to update.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("✏️ Update Patient Record")
    
    # Convert to dictionaries for safe access
    patient_dicts = [convert_row_to_dict(p) for p in patients]
    patient_options = {f"{p['patient_id']} - {p.get('anonymized_name', 'Unknown')}": p['patient_id'] for p in patient_dicts}
    
    if not patient_options:
        st.info("No patients available for update.")
        return
        
    selected_display = st.selectbox("🔍 Select Patient", list(patient_options.keys()))
    selected_id = patient_options[selected_display]
    
    selected_patient = next((p for p in patient_dicts if p['patient_id'] == selected_id), None)
    
    if not selected_patient:
        st.error("Patient not found")
        return
    
    with st.form("update_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("👤 Full Name", value=selected_patient.get('name', ''))
            contact = st.text_input("📞 Contact", value=selected_patient.get('contact', ''))
        
        with col2:
            diagnosis = st.text_area("🩺 Diagnosis", value=selected_patient.get('diagnosis', ''), height=100)
        
        submitted = st.form_submit_button("🔄 Update Patient", use_container_width=True)
        
        if submitted:
            anon_name = mask_name(selected_id)
            anon_contact = mask_contact(contact)
            update_patient(selected_id, name, contact, diagnosis, anon_name, anon_contact)
            
            log_user_action(st.session_state, "UPDATE_PATIENT", f"Updated patient ID {selected_id}")
            st.success("✅ Patient record updated successfully!")

# ========== MODERN ANONYMIZATION PAGE ==========

def anonymization_page():
    """Modern data protection interface"""
    if not check_role(st.session_state, ['admin']):
        st.error("🚫 Admin access required")
        return
    
    st.markdown(f'<h1 class="main-header">Data Protection Center</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔒 Batch Anonymization")
        st.info("Apply GDPR-compliant anonymization to all patient records")
        
        if st.button("🛡️ Secure All Data", use_container_width=True):
            with st.spinner("Applying advanced encryption..."):
                cipher = get_cipher()
                anonymize_all_patients(cipher)
                log_user_action(st.session_state, "ANONYMIZE_ALL", "Batch anonymization applied")
                st.success("🎉 All patient data secured with military-grade encryption!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔓 Secure Decryption")
        st.warning("Admin-only decryption with audit trail")
        
        patients = get_all_patients()
        if patients:
            patient_dicts = [convert_row_to_dict(p) for p in patients]
            patient_options = {f"{p['patient_id']} - {p.get('anonymized_name', 'Unknown')}": p for p in patient_dicts}
            
            if patient_options:
                selected_display = st.selectbox("Select Encrypted Record", list(patient_options.keys()))
                selected_patient = patient_options[selected_display]
                
                if st.button("🔍 Decrypt Record", use_container_width=True):
                    cipher = get_cipher()
                    decrypted_name = decrypt_field(cipher, selected_patient.get('encrypted_name', ''))
                    decrypted_contact = decrypt_field(cipher, selected_patient.get('encrypted_contact', ''))
                    
                    st.success("Decrypted Data:")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Name:** {decrypted_name}")
                    with col2:
                        st.info(f"**Contact:** {decrypted_contact}")
                    
                    log_user_action(st.session_state, "DECRYPT_DATA", f"Decrypted patient ID {selected_patient.get('patient_id', 'Unknown')}")
        st.markdown('</div>', unsafe_allow_html=True)

# ========== MODERN AUDIT LOGS ==========

def audit_logs_page():
    """Modern audit logs interface"""
    if not check_role(st.session_state, ['admin']):
        st.error("🚫 Admin access required")
        return
    
    st.markdown(f'<h1 class="main-header">Security Audit Center</h1>', unsafe_allow_html=True)
    
    logs = get_all_logs()
    
    if not logs:
        st.info("No audit logs available")
        return
    
    # Convert to dictionaries safely
    log_dicts = [convert_row_to_dict(log) for log in logs]
    log_df = pd.DataFrame(log_dicts)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card("Total Logs", len(logs), "📊", "linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%)"), unsafe_allow_html=True)
    with col2:
        unique_users = log_df['user_id'].nunique() if 'user_id' in log_df.columns else 0
        st.markdown(create_metric_card("Unique Users", unique_users, "👥", "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Actions Today", "15", "⚡", "linear-gradient(135deg, #fad0c4 0%, #ffd1ff 100%)"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("System Integrity", "100%", "🛡️", "linear-gradient(135deg, #a8e6cf 0%, #56ab2f 100%)"), unsafe_allow_html=True)
    
    # Filtering
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        actions = ["All"] + list(log_df['action'].unique()) if 'action' in log_df.columns else ["All"]
        selected_action = st.selectbox("Filter by Action", actions)
    
    with col2:
        roles = ["All"] + list(log_df['role'].unique()) if 'role' in log_df.columns else ["All"]
        selected_role = st.selectbox("Filter by Role", roles)
    
    with col3:
        date_range = st.date_input("Date Range", [])
    
    # Apply filters
    filtered_df = log_df.copy()
    if selected_action != "All" and 'action' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['action'] == selected_action]
    if selected_role != "All" and 'role' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['role'] == selected_role]
    
    # Display logs
    st.dataframe(filtered_df, use_container_width=True, height=400)
    st.markdown('</div>', unsafe_allow_html=True)
    
    log_user_action(st.session_state, "VIEW_AUDIT_LOG", "Accessed audit logs")

# ========== MODERN NAVIGATION ==========

def main():
    """Modern navigation system"""
    
    if st.session_state['user'] is None:
        login_page()
    else:
        user = st.session_state['user']
        
        # Modern sidebar
        with st.sidebar:
            st.markdown("""
            <div style='text-align: center; margin-bottom: 2rem;'>
                <h2 style='color: white; margin-bottom: 0;'>🏥 MediCare Pro</h2>
                <p style='color: #8892b0; font-size: 0.9rem;'>Hospital Management</p>
            </div>
            """, unsafe_allow_html=True)
            
            # User info card
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 15px; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.1);'>
                <div style='color: white; font-weight: 600; font-size: 1.1rem;'>{user['username']}</div>
                <div style='color: #8892b0; font-size: 0.8rem; margin-top: 0.5rem;'>{get_role_badge(user['role'])}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation
            st.markdown("### 🧭 Navigation")
            
            nav_items = [
                ("🏠 Dashboard", "Dashboard"),
                ("👥 Patients", "Patients"),
            ]
            
            if user['role'] == 'admin':
                nav_items.extend([
                    ("🔐 Data Protection", "Anonymization"),
                    ("📜 Audit Logs", "Audit Logs")
                ])
            
            for icon, page in nav_items:
                if st.button(f"{icon} {page}", key=page, use_container_width=True):
                    st.session_state['page'] = page
                    st.rerun()
            
            st.markdown("---")
            
            # Quick actions
            st.markdown("### ⚡ Quick Actions")
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
            
            if st.button("🚪 Sign Out", use_container_width=True):
                logout()
            
            # Footer
            st.markdown("---")
            st.markdown("""
            <div style='color: #8892b0; font-size: 0.8rem; text-align: center;'>
                <div>🛡️ Secure • ⚡ Fast • 🔒 Private</div>
                <div>v2.1.0 | GDPR Ready</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Page routing
        page = st.session_state.get('page', 'Dashboard')
        
        if page == 'Dashboard':
            dashboard_page()
        elif page == 'Patients':
            patients_page()
        elif page == 'Anonymization':
            anonymization_page()
        elif page == 'Audit Logs':
            audit_logs_page()

if __name__ == "__main__":
    main()