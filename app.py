import streamlit as st
from utils.database import verify_doctor

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="CDSS Login",
    page_icon="🏥",
    layout="centered"
)

# ============================================================
# HIDE STREAMLIT SIDEBAR NAVIGATION UNTIL LOGGED IN
# ============================================================
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    .login-container {
        max-width: 420px;
        margin: auto;
        padding: 2rem;
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background-color: #1a73e8;
        color: white;
        font-weight: bold;
        padding: 0.6rem;
        border: none;
        margin-top: 0.5rem;
    }
    .stButton > button:hover {
        background-color: #1557b0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# IF ALREADY LOGGED IN — REDIRECT TO DASHBOARD
# ============================================================
if "doctor" in st.session_state and st.session_state.doctor:
    st.switch_page("pages/1_Dashboard.py")

# ============================================================
# LOGIN FORM
# ============================================================
st.markdown("""
    <div class='login-header'>
        <h1>🏥</h1>
        <h2>Clinical Decision Support System</h2>
        <p style='color: #7f8c8d;'>IoT-Enabled Diabetes Risk Prediction</p>
        <hr/>
    </div>
""", unsafe_allow_html=True)

st.subheader("Doctor Login")
st.caption("Enter your clinic-issued credentials to access the system.")

with st.form("login_form"):
    doctor_id = st.text_input("Doctor ID", placeholder="e.g. DOC001")
    password  = st.text_input("Password", type="password", placeholder="Enter your password")
    submit    = st.form_submit_button("Login", use_container_width=True)

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

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
    <div style='text-align:center; margin-top:3rem; color:#bdc3c7; font-size:0.8rem;'>
        Access restricted to verified clinic staff only.<br/>
        FYP Prototype — CB013123 | APIIT / Staffordshire University
    </div>
""", unsafe_allow_html=True)