import streamlit as st
import pandas as pd
from datetime import date
from utils.database import get_patient_by_code, create_patient, get_last_prediction, get_next_patient_code
from dateutil.relativedelta import relativedelta
from utils.styles import load_css, render_sidebar

# ============================================================
# AUTH GUARD
# ============================================================
if "doctor" not in st.session_state or not st.session_state.doctor:
    st.switch_page("app.py")

doctor = st.session_state.doctor

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Patient Assessment", page_icon="🩺", layout="wide")
load_css()
render_sidebar("Patient Assessment")

# ============================================================
# DESIGN SYSTEM — same tokens as Login / Dashboard
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

    :root {
        --navy-900: #0B2C4A;
        --teal-500: #0F8B8D;
        --ink-900:  #101828;
        --ink-600:  #475467;
        --ink-400:  #98A2B3;
        --line:     #E4E9F0;
        --bg:       #F4F7FB;
        --radius:   12px;
    }

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', -apple-system, sans-serif; }

    .page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink-900); margin: 0; letter-spacing: -0.01em; }
    .page-sub   { color: var(--ink-600); font-size: 0.88rem; margin-top: 0.15rem; }

    .section-title { font-size: 1.02rem; font-weight: 700; color: var(--ink-900); margin: 0 0 0.15rem 0; }
    .section-sub   { color: var(--ink-600); font-size: 0.84rem; margin-bottom: 1rem; }

    /* ---------- buttons ---------- */
    [data-testid="stButton"] button[kind="primary"] {
        background: var(--navy-900);
        border: none;
        border-radius: 9px;
        font-weight: 600;
        transition: background 0.15s ease;
    }
    [data-testid="stButton"] button[kind="primary"]:hover { background: var(--teal-500); }
    [data-testid="stButton"] button[kind="secondary"] {
        border: 1.5px solid var(--line);
        border-radius: 9px;
        color: var(--navy-900);
        font-weight: 600;
        background: #fff;
    }
    [data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: var(--teal-500);
        color: var(--teal-500);
    }

    /* ---------- inputs ---------- */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input {
        border: 1.5px solid var(--line);
        border-radius: 9px;
        background: #fff;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stDateInput"] input:focus {
        border-color: var(--teal-500);
        box-shadow: 0 0 0 3px rgba(15,139,141,0.15);
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border-radius: 9px;
        border: 1.5px solid var(--line);
    }
    [data-testid="stTextInput"] label,
    [data-testid="stNumberInput"] label,
    [data-testid="stDateInput"] label,
    [data-testid="stSelectbox"] label {
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--ink-900);
    }

    /* ---------- alerts ---------- */
    [data-testid="stAlert"] { border-radius: 9px; font-size: 0.88rem; }

    /* ---------- file uploader ---------- */
    [data-testid="stFileUploaderDropzone"] {
        border-radius: 9px;
        border: 1.5px dashed var(--line);
        background: #FAFBFD;
    }

    /* ---------- expander ---------- */
    [data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 9px;
    }

    /* ---------- metric ---------- */
    [data-testid="stMetric"] {
        background: #F8FAFC;
        border-radius: 9px;
        border: 1px solid var(--line);
        padding: 0.8rem 1rem;
    }
    </style>
""", unsafe_allow_html=True)

with st.container(key="page-content"):

    # ============================================================
    # HEADER — no local Dashboard button; the top nav already
    # provides that link, avoiding a duplicate-navigation control.
    # ============================================================
    st.markdown("""
        <div class="page-title">Patient Assessment</div>
        <div class="page-sub">Enter patient details and clinical data to generate a diabetes risk prediction.</div>
    """, unsafe_allow_html=True)
    st.write("")

    # ============================================================
    # SECTION 1 — PATIENT IDENTIFICATION
    # ============================================================
    with st.container(border=True):
        st.markdown("""
            <div class="section-title">Patient Information</div>
            <div class="section-sub">Enter a unique Patient Code. If the patient exists, their personal details and last recorded clinical values will load automatically.</div>
        """, unsafe_allow_html=True)

        returning_patient = st.session_state.get("selected_patient", None)

        if returning_patient:
            suggested_code = returning_patient["patient_code"]
        else:
            suggested_code = get_next_patient_code(doctor["id"])

        col1, col2 = st.columns([2, 4])
        with col1:
            patient_code = st.text_input(
                "Patient Code *",
                value=suggested_code,
                placeholder="e.g. DOC001-P001",
                help="Auto-generated based on your Doctor ID. You can edit this if needed."
            )

        existing_patient = None
        if patient_code:
            existing_patient = get_patient_by_code(patient_code.strip().upper())

        if existing_patient:
            last_pred = get_last_prediction(existing_patient['id'])

            st.success(f"Existing patient found: **{existing_patient['full_name']}**")
            if last_pred:
                st.info("Last recorded clinical values loaded — update any that have changed for this visit.")

            full_name      = existing_patient["full_name"]
            dob            = existing_patient["date_of_birth"]
            gender_default = existing_patient["gender"]
            contact        = existing_patient["contact_number"] or ""
            is_new_patient = False

            if last_pred:
                default_hba1c     = float(last_pred["hba1c"])
                default_bmi       = float(last_pred["bmi"])
                default_tg        = float(last_pred["tg"])
                default_steps     = int(last_pred["total_steps"])
                default_sedentary = int(last_pred["sedentary_minutes"])
                default_calories  = int(last_pred["calories"])
                default_sleep_min = int(last_pred["total_minutes_asleep"])
                default_sleep_eff = float(last_pred["sleep_efficiency"])
            else:
                default_hba1c     = 6.0
                default_bmi       = 27.0
                default_tg        = 150.0
                default_steps     = 6000
                default_sedentary = 600
                default_calories  = 2000
                default_sleep_min = 420
                default_sleep_eff = 0.90
        else:
            if patient_code and len(patient_code) >= 3:
                st.info("New patient — please complete the details below.")

            full_name         = ""
            dob               = date(1990, 1, 1)
            gender_default    = "Male"
            contact           = ""
            is_new_patient    = True
            last_pred         = None
            default_hba1c     = 6.0
            default_bmi       = 27.0
            default_tg        = 150.0
            default_steps     = 6000
            default_sedentary = 600
            default_calories  = 2000
            default_sleep_min = 420
            default_sleep_eff = 0.90

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            full_name = st.text_input(
                "Full Name *", value=full_name, disabled=not is_new_patient
            )
        with col_b:
            dob = st.date_input(
                "Date of Birth *", value=dob,
                min_value=date(1900, 1, 1), max_value=date.today(),
                disabled=not is_new_patient
            )
        with col_c:
            gender_options = ["Male", "Female"]
            gender_index   = 0 if gender_default == "Male" else 1
            gender_label   = st.selectbox(
                "Gender *", gender_options, index=gender_index, disabled=not is_new_patient
            )
        with col_d:
            contact = st.text_input(
                "Contact Number", value=contact, disabled=not is_new_patient
            )

    if dob:
        calculated_age = relativedelta(date.today(), dob).years
    else:
        calculated_age = 0

    gender_num = 1 if gender_label == "Male" else 0

    st.write("")

    # ============================================================
    # SECTION 2 — CLINICAL DATA
    # ============================================================
    with st.container(border=True):
        st.markdown("""
            <div class="section-title">Clinical Measurements</div>
            <div class="section-sub">Enter the patient's latest clinical test results for this visit.</div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Calculated Age", f"{calculated_age} years", help="Auto-calculated from date of birth")
            hba1c = st.number_input(
                "HbA1c (%)", min_value=2.0, max_value=20.0, value=default_hba1c, step=0.1,
                help="Normal <5.7% | Pre-diabetic 5.7–6.4% | Diabetic ≥6.5%"
            )
        with col2:
            bmi = st.number_input(
                "BMI (kg/m²)", min_value=10.0, max_value=70.0, value=default_bmi, step=0.1,
                help="Normal 18.5–24.9 | Overweight 25–29.9 | Obese ≥30"
            )
            tg = st.number_input(
                "Triglycerides (mg/dL)", min_value=0.0, max_value=1000.0, value=default_tg, step=1.0,
                help="Normal <150 mg/dL"
            )
        with col3:
            st.write("")
            st.info(f"**Gender:** {gender_label} · **Age:** {calculated_age} yrs")

    st.write("")

    # ============================================================
    # SECTION 3 — IoT / WEARABLE DATA
    # ============================================================
    with st.container(border=True):
        st.markdown("""
            <div class="section-title">IoT & Wearable Data</div>
            <div class="section-sub">Enter data manually or import directly from a Fitbit CSV export.</div>
        """, unsafe_allow_html=True)

        with st.expander("Import from Fitbit CSV Export", expanded=False):
            st.markdown("""
                **How to export your Fitbit data:**
                1. Go to [fitbit.com](https://www.fitbit.com) → Account → Settings → Data Export
                2. Download your data archive
                3. Find `dailyActivity_merged.csv` and/or `sleepDay_merged.csv`
                4. Upload them below — the system will auto-fill the IoT fields using the average values across all recorded days
            """)

            col_act, col_sleep = st.columns(2)
            with col_act:
                activity_file = st.file_uploader(
                    "Upload dailyActivity_merged.csv", type=["csv"], key="activity_csv"
                )
            with col_sleep:
                sleep_file = st.file_uploader(
                    "Upload sleepDay_merged.csv", type=["csv"], key="sleep_csv"
                )

            imported_steps     = None
            imported_sedentary = None
            imported_calories  = None
            imported_sleep_min = None
            imported_sleep_eff = None

            if activity_file is not None:
                try:
                    activity_df   = pd.read_csv(activity_file)
                    steps_col     = next((c for c in activity_df.columns if 'totalsteps' in c.lower() or c.lower() == 'steps'), None)
                    sedentary_col = next((c for c in activity_df.columns if 'sedentary' in c.lower()), None)
                    calories_col  = next((c for c in activity_df.columns if 'calories' in c.lower()), None)

                    if steps_col:
                        imported_steps = int(activity_df[steps_col].mean())
                    if sedentary_col:
                        imported_sedentary = int(activity_df[sedentary_col].mean())
                    if calories_col:
                        imported_calories = int(activity_df[calories_col].mean())

                    st.success(
                        f"Activity data imported — "
                        f"Avg Steps: **{imported_steps:,}** | "
                        f"Avg Sedentary: **{imported_sedentary} min** | "
                        f"Avg Calories: **{imported_calories}**"
                    )
                except Exception as e:
                    st.error(f"Could not read activity file: {e}")

            if sleep_file is not None:
                try:
                    sleep_df      = pd.read_csv(sleep_file)
                    sleep_min_col = next((c for c in sleep_df.columns if 'minutesasleep' in c.lower() or 'totalminutesasleep' in c.lower()), None)
                    sleep_eff_col = next((c for c in sleep_df.columns if 'efficiency' in c.lower()), None)

                    if sleep_min_col:
                        imported_sleep_min = int(sleep_df[sleep_min_col].mean())
                    if sleep_eff_col:
                        raw_eff = sleep_df[sleep_eff_col].mean()
                        imported_sleep_eff = round(raw_eff / 100, 2) if raw_eff > 1 else round(float(raw_eff), 2)

                    st.success(
                        f"Sleep data imported — "
                        f"Avg Sleep: **{imported_sleep_min} min** | "
                        f"Avg Efficiency: **{imported_sleep_eff:.0%}**"
                    )
                except Exception as e:
                    st.error(f"Could not read sleep file: {e}")

            if activity_file or sleep_file:
                imported_fields = []
                if imported_steps is not None:     imported_fields.append("Total Steps")
                if imported_sedentary is not None: imported_fields.append("Sedentary Minutes")
                if imported_calories is not None:  imported_fields.append("Calories")
                if imported_sleep_min is not None: imported_fields.append("Minutes Asleep")
                if imported_sleep_eff is not None: imported_fields.append("Sleep Efficiency")
                if imported_fields:
                    st.info(f"Auto-filled fields: {', '.join(imported_fields)}. You can still edit them below.")

        col1, col2, col3 = st.columns(3)
        with col1:
            total_steps = st.number_input(
                "Total Steps (daily)", min_value=0, max_value=50000,
                value=imported_steps if imported_steps is not None else default_steps, step=100,
                help="Average daily step count from wearable"
            )
            sedentary = st.number_input(
                "Sedentary Minutes (daily)", min_value=0, max_value=1440,
                value=imported_sedentary if imported_sedentary is not None else default_sedentary, step=10,
                help="Minutes spent sedentary per day"
            )
        with col2:
            calories = st.number_input(
                "Calories Burned (daily)", min_value=0, max_value=10000,
                value=imported_calories if imported_calories is not None else default_calories, step=50,
                help="Total daily calories burned"
            )
            sleep_minutes = st.number_input(
                "Total Minutes Asleep", min_value=0, max_value=1440,
                value=imported_sleep_min if imported_sleep_min is not None else default_sleep_min, step=10,
                help="Total sleep duration in minutes"
            )
        with col3:
            sleep_efficiency = st.number_input(
                "Sleep Efficiency (0–1)", min_value=0.0, max_value=1.0,
                value=imported_sleep_eff if imported_sleep_eff is not None else default_sleep_eff, step=0.01,
                help="Good sleep efficiency ≥0.85"
            )

    st.write("")

    # ============================================================
    # SUBMIT
    # ============================================================
    col_btn, col_space = st.columns([2, 5])
    with col_btn:
        predict_btn = st.button("Predict Diabetes Risk", type="primary", use_container_width=True)

    if predict_btn:
        errors = []
        if not patient_code:
            errors.append("Patient Code is required.")
        if not full_name:
            errors.append("Full Name is required.")
        if calculated_age < 1:
            errors.append("Date of Birth appears invalid — please check.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            if is_new_patient:
                patient_db_id = create_patient(
                    patient_code   = patient_code.strip().upper(),
                    full_name      = full_name.strip(),
                    date_of_birth  = dob,
                    gender         = gender_label,
                    contact_number = contact.strip(),
                    doctor_id      = doctor['id']
                )
            else:
                patient_db_id = existing_patient['id']

            patient_input = {
                "Gender":             gender_num,
                "AGE":                calculated_age,
                "HbA1c":              hba1c,
                "TG":                 tg,
                "BMI":                bmi,
                "TotalSteps":         total_steps,
                "SedentaryMinutes":   sedentary,
                "Calories":           calories,
                "TotalMinutesAsleep": sleep_minutes,
                "SleepEfficiency":    sleep_efficiency,
            }

            st.session_state.patient_info = {
                "patient_code":       patient_code.strip().upper(),
                "full_name":          full_name.strip(),
                "date_of_birth":      str(dob),
                "gender":             gender_label,
                "contact_number":     contact.strip(),
                "AGE":                calculated_age,
                "HbA1c":              hba1c,
                "TG":                 tg,
                "BMI":                bmi,
                "TotalSteps":         total_steps,
                "SedentaryMinutes":   sedentary,
                "Calories":           calories,
                "TotalMinutesAsleep": sleep_minutes,
                "SleepEfficiency":    sleep_efficiency,
            }
            st.session_state.patient_db_id = patient_db_id
            st.session_state.patient_input = patient_input

            for key in ["prediction_result", "recommendations",
                        "clinical_insight", "top_features",
                        "shap_vals", "expected_val",
                        "prediction_id", "previous_prediction", "pdf_bytes"]:
                st.session_state.pop(key, None)

            st.success("Patient data saved. Redirecting to results...")
            st.switch_page("pages/3_Prediction_Results.py")