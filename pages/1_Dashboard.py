import streamlit as st
from utils.database import get_all_patients

# ============================================================
# AUTH GUARD
# ============================================================
if "doctor" not in st.session_state or not st.session_state.doctor:
    st.switch_page("app.py")

doctor = st.session_state.doctor

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Dashboard", page_icon="🏥", layout="wide")

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
    <style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border-left: 4px solid #1a73e8;
    }
    .risk-high   { color: #e74c3c; font-weight: bold; }
    .risk-pre    { color: #f39c12; font-weight: bold; }
    .risk-normal { color: #27ae60; font-weight: bold; }
    .section-header {
        font-size: 1.1rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
col_title, col_logout = st.columns([6, 1])
with col_title:
    st.title("🏥 Clinical Dashboard")
    st.caption(f"Logged in as **{doctor['full_name']}** · {doctor['specialization']} · ID: {doctor['doctor_id']}")
with col_logout:
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.divider()

# ============================================================
# LOAD PATIENTS
# ============================================================
patients = get_all_patients(doctor['id'])

# ============================================================
# SUMMARY METRICS
# ============================================================
total     = len(patients)
diabetic  = sum(1 for p in patients if p.get("latest_risk") == "Diabetic")
prediab   = sum(1 for p in patients if p.get("latest_risk") == "Pre-diabetic")
normal    = sum(1 for p in patients if p.get("latest_risk") == "Normal")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Patients", total)
with col2:
    st.metric("🔴 Diabetic", diabetic)
with col3:
    st.metric("🟠 Pre-diabetic", prediab)
with col4:
    st.metric("🟢 Normal", normal)

st.divider()

# ============================================================
# ACTION BUTTONS
# ============================================================
col_a, col_b = st.columns([2, 6])
with col_a:
    if st.button("➕ New Patient Assessment", use_container_width=True, type="primary"):
        # Clear any previous patient session data
        for key in ["patient_info", "patient_db", "prediction_result",
                    "recommendations", "clinical_insight", "top_features"]:
            st.session_state.pop(key, None)
        st.switch_page("pages/2_Patient_Assessment.py")

st.divider()

# ============================================================
# PATIENT TABLE
# ============================================================
st.markdown("### 👥 Your Patients")

if not patients:
    st.info("No patients yet. Click **New Patient Assessment** to add your first patient.")
else:
    # Table header
    h1, h2, h3, h4, h5, h6 = st.columns([2, 3, 2, 2, 2, 2])
    h1.markdown("**Patient Code**")
    h2.markdown("**Full Name**")
    h3.markdown("**Gender**")
    h4.markdown("**Latest Risk**")
    h5.markdown("**Assessments**")
    h6.markdown("**Action**")

    st.markdown("---")

    for patient in patients:
        c1, c2, c3, c4, c5, c6 = st.columns([2, 3, 2, 2, 2, 2])

        risk = patient.get("latest_risk", "Not assessed")

        # Risk badge colour
        if risk == "Diabetic":
            risk_display = "🔴 Diabetic"
        elif risk == "Pre-diabetic":
            risk_display = "🟠 Pre-diabetic"
        elif risk == "Normal":
            risk_display = "🟢 Normal"
        else:
            risk_display = "⚪ Not assessed"

        c1.write(patient["patient_code"])
        c2.write(patient["full_name"])
        c3.write(patient["gender"])
        c4.write(risk_display)
        c5.write(str(patient.get("total_predictions", 0)))

        with c6:
            if st.button("Assess", key=f"assess_{patient['id']}",
                         use_container_width=True):
                # Store selected patient in session and go to assessment
                st.session_state.selected_patient = patient
                for key in ["prediction_result", "recommendations",
                            "clinical_insight", "top_features"]:
                    st.session_state.pop(key, None)
                st.switch_page("pages/2_Patient_Assessment.py")