import streamlit as st
from utils.database import verify_doctor, verify_admin

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="CDSS — Login",
    page_icon="🏥",
    layout="centered"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    .login-box {
        background: #ffffff;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        margin-top: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.4rem 1.2rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# ALREADY LOGGED IN — REDIRECT
# ============================================================
if "doctor" in st.session_state and st.session_state.doctor:
    st.switch_page("pages/1_Dashboard.py")

if "admin" in st.session_state and st.session_state.admin:
    st.switch_page("pages/6_Admin_Panel.py")

# ============================================================
# HEADER
# ============================================================
st.markdown("""
    <div style='text-align:center; padding: 1.5rem 0 0.5rem 0;'>
        <div style='font-size:3rem'>🏥</div>
        <h2 style='margin:0.3rem 0; color:#1e293b'>Clinical Decision Support System</h2>
        <p style='color:#64748b; margin:0'>IoT-Enabled Diabetes Risk Prediction</p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# ============================================================
# LOGIN TABS — Doctor | Admin
# ============================================================
tab_doctor, tab_admin = st.tabs(["👨‍⚕️ Doctor Login", "🔧 Admin Login"])

# ── DOCTOR LOGIN ────────────────────────────────────────────
with tab_doctor:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("**Doctor Login**")
    st.caption("Enter your clinic-issued Doctor ID and password.")

    with st.form("doctor_login_form"):
        doctor_id = st.text_input("Doctor ID", placeholder="e.g. DOC001")
        password  = st.text_input("Password", type="password", placeholder="Enter your password")
        submit    = st.form_submit_button("Login", use_container_width=True, type="primary")

    if submit:
        if not doctor_id or not password:
            st.error("Please enter both Doctor ID and password.")
        else:
            with st.spinner("Verifying credentials..."):
                doctor = verify_doctor(doctor_id.strip(), password.strip())
            if doctor:
                st.session_state.doctor = doctor
                st.success(f"Welcome, {doctor['full_name']}!")
                st.switch_page("pages/1_Dashboard.py")
            else:
                st.error("Invalid Doctor ID or password. Please try again.")

    st.markdown("</div>", unsafe_allow_html=True)

# ── ADMIN LOGIN ─────────────────────────────────────────────
with tab_admin:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("**Clinic Administrator Login**")
    st.caption("Restricted to authorised clinic administrators only.")

    with st.form("admin_login_form"):
        admin_user = st.text_input("Admin Username", placeholder="e.g. admin")
        admin_pass = st.text_input("Password", type="password", placeholder="Enter admin password")
        admin_submit = st.form_submit_button("Admin Login", use_container_width=True, type="primary")

    if admin_submit:
        if not admin_user or not admin_pass:
            st.error("Please enter both username and password.")
        else:
            with st.spinner("Verifying admin credentials..."):
                admin = verify_admin(admin_user.strip(), admin_pass.strip())
            if admin:
                st.session_state.admin = admin
                st.success(f"Welcome, {admin['full_name']}!")
                st.switch_page("pages/6_Admin_Panel.py")
            else:
                st.error("Invalid admin credentials. Please try again.")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
    <div style='text-align:center; margin-top:2rem; color:#94a3b8; font-size:0.78rem;'>
        Access restricted to verified clinic staff only.<br/>
        FYP Prototype — CB013123 | APIIT / Staffordshire University
    </div>
""", unsafe_allow_html=True)