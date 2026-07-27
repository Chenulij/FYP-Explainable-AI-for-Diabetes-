import streamlit as st
import pandas as pd
from utils.database import get_all_patients, get_patient_history

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
        background: #ffffff;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .history-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 0.8rem 1.1rem;
        margin-bottom: 0.5rem;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2563eb;
    }
    .history-date {
        font-size: 0.78rem;
        color: #64748b;
        margin-bottom: 0.2rem;
    }
    .history-pred {
        font-size: 0.95rem;
        font-weight: bold;
        margin-bottom: 0.2rem;
    }
    .history-detail {
        font-size: 0.82rem;
        color: #64748b;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
col_title, col_logout = st.columns([6, 1])
with col_title:
    st.title("🏥 Clinical Dashboard")
    st.caption(
        f"Logged in as **{doctor['full_name']}** · "
        f"{doctor['specialization']} · "
        f"ID: {doctor['doctor_id']}"
    )
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
total    = len(patients)
diabetic = sum(1 for p in patients if p.get("latest_risk") == "Diabetic")
prediab  = sum(1 for p in patients if p.get("latest_risk") == "Pre-diabetic")
normal   = sum(1 for p in patients if p.get("latest_risk") == "Normal")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("👥 Total Patients", total)
with col2:
    st.metric("🔴 Diabetic", diabetic)
with col3:
    st.metric("🟠 Pre-diabetic", prediab)
with col4:
    st.metric("🟢 Normal", normal)

st.divider()

# ============================================================
# NEW PATIENT BUTTON
# ============================================================
col_btn, _ = st.columns([2, 6])
with col_btn:
    if st.button("➕ New Patient Assessment", use_container_width=True, type="primary"):
        for key in ["patient_info", "patient_db", "prediction_result",
                    "recommendations", "clinical_insight", "top_features",
                    "shap_vals", "expected_val", "selected_patient",
                    "patient_input", "pdf_bytes"]:
            st.session_state.pop(key, None)
        st.switch_page("pages/2_Patient_Assessment.py")

st.divider()

# ============================================================
# PATIENT LIST + HISTORY (two panel layout)
# ============================================================
if not patients:
    st.info("No patients yet. Click **New Patient Assessment** to add your first patient.")
else:
    # Use tabs — Patients list and Patient History
    tab1, tab2 = st.tabs(["👥 Patient List", "📈 Patient History"])

    with tab1:
        # ── Table header ──────────────────────────────────────
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
                    st.session_state.selected_patient = patient
                    for key in ["prediction_result", "recommendations",
                                "clinical_insight", "top_features",
                                "shap_vals", "expected_val",
                                "patient_input", "pdf_bytes"]:
                        st.session_state.pop(key, None)
                    st.switch_page("pages/2_Patient_Assessment.py")

    with tab2:
        st.markdown("### 📈 Patient Risk History")
        st.caption("Select a patient to view their full assessment history and risk trend over time.")

        # Patient selector
        patient_names = {p["full_name"]: p for p in patients}
        selected_name = st.selectbox(
            "Select Patient",
            options=list(patient_names.keys()),
            index=0
        )

        if selected_name:
            selected_patient = patient_names[selected_name]
            history = get_patient_history(selected_patient["id"])

            if not history:
                st.info("No assessment history yet for this patient.")
            else:
                # ── Risk trend chart ──────────────────────────
                st.markdown(f"#### {selected_name} — Risk History")
                st.caption(f"Patient Code: {selected_patient['patient_code']} · Total Assessments: {len(history)}")

                # Build dataframe for chart
                chart_data = []
                for h in reversed(history):  # oldest first for chart
                    chart_data.append({
                        "Date": str(h["predicted_at"])[:10],
                        "Confidence %": round(float(h["confidence"]), 1),
                        "Risk": h["prediction_label"],
                        "HbA1c": h["hba1c"],
                        "BMI": h["bmi"],
                    })
                df = pd.DataFrame(chart_data)

                # Colour map for risk
                col_chart, col_detail = st.columns([1, 1])

                with col_chart:
                    st.markdown("**Confidence Score Over Time**")
                    st.line_chart(df.set_index("Date")["Confidence %"])

                with col_detail:
                    st.markdown("**HbA1c & BMI Trend**")
                    st.line_chart(df.set_index("Date")[["HbA1c", "BMI"]])

                st.divider()

                # ── Assessment history cards ──────────────────
                st.markdown("**Full Assessment History**")
                for i, h in enumerate(history):
                    risk = h["prediction_label"]
                    if risk == "Diabetic":
                        icon  = "🔴"
                        color = "#dc2626"
                    elif risk == "Pre-diabetic":
                        icon  = "🟠"
                        color = "#d97706"
                    else:
                        icon  = "🟢"
                        color = "#16a34a"

                    date_str = str(h["predicted_at"])[:16]

                    st.markdown(f"""
                        <div class='history-card'>
                            <div class='history-date'>📅 {date_str}</div>
                            <div class='history-pred' style='color:{color}'>
                                {icon} {risk} — {h['confidence']:.1f}% confidence
                            </div>
                            <div class='history-detail'>
                                HbA1c: {h['hba1c']}% &nbsp;|&nbsp;
                                BMI: {h['bmi']} &nbsp;|&nbsp;
                                Steps: {h['total_steps']:,} &nbsp;|&nbsp;
                                Sleep Efficiency: {h['sleep_efficiency']:.0%}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                # ── Assess again button ───────────────────────
                st.markdown("<br/>", unsafe_allow_html=True)
                if st.button(
                    f"➕ New Assessment for {selected_name}",
                    type="primary",
                    use_container_width=False
                ):
                    st.session_state.selected_patient = selected_patient
                    for key in ["prediction_result", "recommendations",
                                "clinical_insight", "top_features",
                                "shap_vals", "expected_val",
                                "patient_input", "pdf_bytes"]:
                        st.session_state.pop(key, None)
                    st.switch_page("pages/2_Patient_Assessment.py")