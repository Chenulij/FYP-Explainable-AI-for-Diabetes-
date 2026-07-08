import streamlit as st
from datetime import date
from utils.database import get_patient_by_code, create_patient

# ============================================================
# AUTH GUARD
# ============================================================
if "doctor" not in st.session_state or not st.session_state.doctor:
    st.switch_page("app.py")

doctor = st.session_state.doctor

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Patient Assessment", page_icon="📋", layout="wide")

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
    <style>
    .section-box {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1a73e8;
    }
    .section-title {
        font-size: 1rem;
        font-weight: bold;
        color: #1a73e8;
        margin-bottom: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
col_title, col_back = st.columns([6, 1])
with col_title:
    st.title("📋 Patient Assessment")
    st.caption("Enter patient details and clinical data to generate a diabetes risk prediction.")
with col_back:
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

st.divider()

# ============================================================
# CHECK IF RETURNING PATIENT (selected from dashboard)
# ============================================================
returning_patient = st.session_state.get("selected_patient", None)

# ============================================================
# SECTION 1 — PATIENT IDENTIFICATION
# ============================================================
st.markdown("### 👤 Patient Information")
st.caption("Enter a unique Patient Code. If the patient exists in the system, their details will load automatically.")

col1, col2 = st.columns([2, 4])
with col1:
    patient_code = st.text_input(
        "Patient Code *",
        value=returning_patient["patient_code"] if returning_patient else "",
        placeholder="e.g. PAT001"
    )

# Auto-load existing patient
existing_patient = None
if patient_code:
    existing_patient = get_patient_by_code(patient_code.strip().upper())

if existing_patient:
    st.success(f"✅ Existing patient found: **{existing_patient['full_name']}**")
    full_name      = existing_patient["full_name"]
    dob            = existing_patient["date_of_birth"]
    gender_default = existing_patient["gender"]
    contact        = existing_patient["contact_number"]
    is_new_patient = False
else:
    if patient_code and len(patient_code) >= 3:
        st.info("🆕 New patient — please complete the details below.")
    full_name      = ""
    dob            = date(1990, 1, 1)
    gender_default = "Male"
    contact        = ""
    is_new_patient = True

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    full_name = st.text_input(
        "Full Name *",
        value=full_name,
        disabled=not is_new_patient
    )
with col_b:
    dob = st.date_input(
        "Date of Birth *",
        value=dob,
        disabled=not is_new_patient
    )
with col_c:
    gender_options = ["Male", "Female"]
    gender_index   = 0 if gender_default == "Male" else 1
    gender_label   = st.selectbox(
        "Gender *",
        gender_options,
        index=gender_index,
        disabled=not is_new_patient
    )
with col_d:
    contact = st.text_input(
        "Contact Number",
        value=contact,
        disabled=not is_new_patient
    )

st.divider()

# ============================================================
# SECTION 2 — CLINICAL DATA
# ============================================================
st.markdown("### 🩺 Clinical Measurements")
st.caption("Enter the patient's latest clinical test results.")

col1, col2, col3 = st.columns(3)
with col1:
    age   = st.number_input("Age (years) *", min_value=1, max_value=120, value=45)
    hba1c = st.number_input("HbA1c (%)", min_value=2.0, max_value=20.0, value=6.0, step=0.1,
                             help="Glycated haemoglobin — primary diabetes marker. Normal <5.7%, Pre-diabetic 5.7–6.4%, Diabetic ≥6.5%")
with col2:
    bmi = st.number_input("BMI (kg/m²)", min_value=10.0, max_value=70.0, value=27.0, step=0.1,
                           help="Body Mass Index. Normal 18.5–24.9, Overweight 25–29.9, Obese ≥30")
    tg  = st.number_input("Triglycerides (mg/dL)", min_value=0.0, max_value=1000.0, value=150.0, step=1.0,
                           help="Blood triglyceride level. Normal <150 mg/dL")
with col3:
    gender_num = 1 if gender_label == "Male" else 0
    st.info(f"**Gender encoding:** {gender_label} = {gender_num} *(used by model)*")
    st.markdown("<br/>", unsafe_allow_html=True)

st.divider()

# ============================================================
# SECTION 3 — IoT / WEARABLE DATA
# ============================================================
st.markdown("### 📱 IoT & Wearable Data")
st.caption("Enter data from the patient's fitness tracker or wearable device.")

col1, col2, col3 = st.columns(3)
with col1:
    total_steps = st.number_input("Total Steps (daily)", min_value=0, max_value=50000, value=6000, step=100,
                                   help="Average daily step count from wearable device")
    sedentary   = st.number_input("Sedentary Minutes (daily)", min_value=0, max_value=1440, value=600, step=10,
                                   help="Minutes spent sedentary per day")
with col2:
    calories      = st.number_input("Calories Burned (daily)", min_value=0, max_value=10000, value=2000, step=50,
                                     help="Total daily calories burned from wearable")
    sleep_minutes = st.number_input("Total Minutes Asleep", min_value=0, max_value=1440, value=420, step=10,
                                     help="Total sleep duration in minutes")
with col3:
    sleep_efficiency = st.number_input("Sleep Efficiency (0–1)", min_value=0.0, max_value=1.0, value=0.90, step=0.01,
                                        help="Ratio of time asleep to time in bed. Good sleep efficiency ≥0.85")

st.divider()

# ============================================================
# SUBMIT BUTTON
# ============================================================
col_btn, col_space = st.columns([2, 5])
with col_btn:
    predict_btn = st.button("🔍 Predict Diabetes Risk", type="primary", use_container_width=True)

if predict_btn:
    # --- Validation ---
    errors = []
    if not patient_code:
        errors.append("Patient Code is required.")
    if not full_name:
        errors.append("Full Name is required.")
    if not dob:
        errors.append("Date of Birth is required.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        # --- Create new patient in DB if first time ---
        if is_new_patient:
            patient_db_id = create_patient(
                patient_code  = patient_code.strip().upper(),
                full_name     = full_name.strip(),
                date_of_birth = dob,
                gender        = gender_label,
                contact_number= contact.strip(),
                doctor_id     = doctor['id']
            )
        else:
            patient_db_id = existing_patient['id']

        # --- Build patient input dict ---
        patient_input = {
            "Gender":             gender_num,
            "AGE":                age,
            "HbA1c":              hba1c,
            "TG":                 tg,
            "BMI":                bmi,
            "TotalSteps":         total_steps,
            "SedentaryMinutes":   sedentary,
            "Calories":           calories,
            "TotalMinutesAsleep": sleep_minutes,
            "SleepEfficiency":    sleep_efficiency,
        }

        # --- Store everything in session state ---
        st.session_state.patient_info = {
            "patient_code":    patient_code.strip().upper(),
            "full_name":       full_name.strip(),
            "date_of_birth":   str(dob),
            "gender":          gender_label,
            "contact_number":  contact.strip(),
            "AGE":             age,
            "HbA1c":           hba1c,
            "TG":              tg,
            "BMI":             bmi,
            "TotalSteps":      total_steps,
            "SedentaryMinutes":sedentary,
            "Calories":        calories,
            "TotalMinutesAsleep": sleep_minutes,
            "SleepEfficiency": sleep_efficiency,
        }
        st.session_state.patient_db_id  = patient_db_id
        st.session_state.patient_input  = patient_input

        st.success("✅ Patient data saved. Redirecting to results...")
        st.switch_page("pages/3_Prediction_Results.py")