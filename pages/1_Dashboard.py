import streamlit as st
import pandas as pd
from utils.database import get_all_patients, get_patient_history
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
st.set_page_config(page_title="Dashboard", page_icon="🩺", layout="wide")
load_css()
render_sidebar("Dashboard")

# ============================================================
# DESIGN SYSTEM — same tokens as the login page
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

    :root {
        --navy-950: #071B2E;
        --navy-900: #0B2C4A;
        --navy-800: #0E3B63;
        --teal-500: #0F8B8D;
        --teal-400: #14A6A6;
        --ink-900:  #101828;
        --ink-600:  #475467;
        --ink-400:  #98A2B3;
        --line:     #E4E9F0;
        --bg:       #F4F7FB;
        --danger:   #D92D20;
        --danger-bg:#FEF2F1;
        --warn:     #B45309;
        --warn-bg:  #FEF6E7;
        --success:  #15803D;
        --success-bg:#EFFAF3;
        --radius:   12px;
    }

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', -apple-system, sans-serif; }
    [data-testid="stAppViewContainer"] { background: var(--bg); }

    /* ---------- header ---------- */
    .dash-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--ink-900);
        margin: 0;
        letter-spacing: -0.01em;
    }
    .dash-sub {
        color: var(--ink-600);
        font-size: 0.88rem;
        margin-top: 0.15rem;
    }

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
        transition: border-color 0.15s ease, color 0.15s ease;
    }
    [data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: var(--teal-500);
        color: var(--teal-500);
    }

    /* ---------- stat cards ---------- */
    .stat-card {
        background: #fff;
        border-radius: var(--radius);
        border: 1px solid var(--line);
        border-left: 4px solid var(--stat-accent, var(--navy-900));
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(16,24,40,0.05);
    }
    .stat-label {
        font-size: 0.76rem;
        color: var(--ink-600);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.35rem;
    }
    .stat-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: var(--ink-900);
        font-family: 'IBM Plex Mono', monospace;
    }

    /* ---------- tabs -> segmented control ---------- */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0;
        background: #EAEFF5;
        padding: 4px;
        border-radius: 10px;
        width: fit-content;
        margin-bottom: 1.4rem;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1.4rem;
        font-weight: 600;
        font-size: 0.86rem;
        color: var(--ink-600);
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: #fff;
        color: var(--navy-900);
        box-shadow: 0 1px 3px rgba(16,24,40,0.12);
    }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"],
    [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }

    /* ---------- patient table ---------- */
    [data-testid="stHorizontalBlock"] { align-items: center; }

    .col-header {
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: var(--ink-600);
    }
    .row-divider {
        border-bottom: 1px solid var(--line);
        margin: 0.5rem 0;
    }
    .patient-code { font-family: 'IBM Plex Mono', monospace; color: var(--ink-600); font-size: 0.84rem; }

    .risk-pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .risk-diabetic     { background: var(--danger-bg); color: var(--danger); }
    .risk-prediabetic  { background: var(--warn-bg);   color: var(--warn); }
    .risk-normal       { background: var(--success-bg);color: var(--success); }
    .risk-none         { background: #F1F5F9;           color: var(--ink-600); }

    /* compact row action button */
    [data-testid="stButton"] button { min-height: 2.1rem; padding: 0.3rem 0.8rem; }

    /* ---------- history cards ---------- */
    .history-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 0.8rem 1.1rem;
        margin-bottom: 0.5rem;
        border: 1px solid var(--line);
        border-left: 4px solid var(--hist-accent, var(--navy-900));
    }
    .history-date { font-size: 0.76rem; color: var(--ink-600); margin-bottom: 0.2rem; }
    .history-pred { font-size: 0.95rem; font-weight: 700; margin-bottom: 0.2rem; }
    .history-detail { font-size: 0.82rem; color: var(--ink-600); }

    /* ---------- selectbox ---------- */
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border-radius: 9px;
        border: 1.5px solid var(--line);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# PAGE TITLE
# (Logout and doctor identity now live in the top nav bar —
# rendered by render_sidebar() above. Don't add another logout
# control here.)
# ============================================================
st.markdown(f"""
    <div class="dash-title">Clinical Dashboard</div>
    <div class="dash-sub">{doctor['specialization']} · ID: {doctor['doctor_id']}</div>
""", unsafe_allow_html=True)

st.write("")

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

stat_defs = [
    ("Total Patients", total, "var(--navy-900)"),
    ("Diabetic", diabetic, "var(--danger)"),
    ("Pre-diabetic", prediab, "var(--warn)"),
    ("Normal", normal, "var(--success)"),
]
cols = st.columns(4)
for col, (label, value, accent) in zip(cols, stat_defs):
    with col:
        st.markdown(f"""
            <div class="stat-card" style="--stat-accent:{accent}">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{value}</div>
            </div>
        """, unsafe_allow_html=True)

st.write("")

# ============================================================
# NEW PATIENT BUTTON
# ============================================================
col_btn, _ = st.columns([2, 6])
with col_btn:
    if st.button("New Patient Assessment", use_container_width=True, type="primary"):
        for key in ["patient_info", "patient_db", "prediction_result",
                    "recommendations", "clinical_insight", "top_features",
                    "shap_vals", "expected_val", "selected_patient",
                    "patient_input", "pdf_bytes"]:
            st.session_state.pop(key, None)
        st.switch_page("pages/2_Patient_Assessment.py")

st.write("")

# ============================================================
# PATIENT LIST + HISTORY (two panel layout)
# ============================================================
RISK_CLASS = {
    "Diabetic": "risk-diabetic",
    "Pre-diabetic": "risk-prediabetic",
    "Normal": "risk-normal",
}

if not patients:
    st.info("No patients yet. Click **New Patient Assessment** to add your first patient.")
else:
    tab1, tab2 = st.tabs(["Patient List", "Patient History"])

    with tab1:
        COL_RATIOS = [1.6, 2.4, 1.4, 1.8, 1.4, 1.2]

        with st.container(border=True):
            hdr = st.columns(COL_RATIOS)
            for c, label in zip(hdr, ["Patient Code", "Full Name", "Gender", "Latest Risk", "Assessments", ""]):
                c.markdown(f'<span class="col-header">{label}</span>', unsafe_allow_html=True)
            st.markdown('<div class="row-divider"></div>', unsafe_allow_html=True)

            for i, patient in enumerate(patients):
                risk = patient.get("latest_risk", "Not assessed")
                pill_class = RISK_CLASS.get(risk, "risk-none")

                r = st.columns(COL_RATIOS)
                r[0].markdown(f'<span class="patient-code">{patient["patient_code"]}</span>', unsafe_allow_html=True)
                r[1].write(patient["full_name"])
                r[2].write(patient["gender"])
                r[3].markdown(f'<span class="risk-pill {pill_class}">{risk}</span>', unsafe_allow_html=True)
                r[4].write(str(patient.get("total_predictions", 0)))
                with r[5]:
                    if st.button("Assess", key=f"assess_{patient['id']}",
                                 use_container_width=True, type="secondary"):
                        st.session_state.selected_patient = patient
                        for key in ["prediction_result", "recommendations",
                                    "clinical_insight", "top_features",
                                    "shap_vals", "expected_val",
                                    "patient_input", "pdf_bytes"]:
                            st.session_state.pop(key, None)
                        st.switch_page("pages/2_Patient_Assessment.py")

                if i < len(patients) - 1:
                    st.markdown('<div class="row-divider"></div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("**Patient Risk History**")
        st.caption("Select a patient to view their full assessment history and risk trend over time.")

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
                st.markdown(f"#### {selected_name} — Risk History")
                st.caption(f"Patient Code: {selected_patient['patient_code']} · Total Assessments: {len(history)}")

                chart_data = []
                for h in reversed(history):
                    chart_data.append({
                        "Date": str(h["predicted_at"])[:10],
                        "Confidence %": round(float(h["confidence"]), 1),
                        "Risk": h["prediction_label"],
                        "HbA1c": h["hba1c"],
                        "BMI": h["bmi"],
                    })
                df = pd.DataFrame(chart_data)

                col_chart, col_detail = st.columns(2)
                with col_chart:
                    st.markdown("**Confidence Score Over Time**")
                    st.line_chart(df.set_index("Date")["Confidence %"])
                with col_detail:
                    st.markdown("**HbA1c & BMI Trend**")
                    st.line_chart(df.set_index("Date")[["HbA1c", "BMI"]])

                st.divider()
                st.markdown("**Full Assessment History**")

                accent_map = {
                    "Diabetic": "var(--danger)",
                    "Pre-diabetic": "var(--warn)",
                    "Normal": "var(--success)",
                }

                for h in history:
                    risk = h["prediction_label"]
                    accent = accent_map.get(risk, "var(--navy-900)")
                    date_str = str(h["predicted_at"])[:16]

                    st.markdown(f"""
                        <div class='history-card' style="--hist-accent:{accent}">
                            <div class='history-date'>{date_str}</div>
                            <div class='history-pred' style='color:{accent}'>{risk} — {h['confidence']:.1f}% confidence</div>
                            <div class='history-detail'>
                                HbA1c: {h['hba1c']}% &nbsp;|&nbsp;
                                BMI: {h['bmi']} &nbsp;|&nbsp;
                                Steps: {h['total_steps']:,} &nbsp;|&nbsp;
                                Sleep Efficiency: {h['sleep_efficiency']:.0%}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                st.write("")
                if st.button(f"New Assessment for {selected_name}", type="primary"):
                    st.session_state.selected_patient = selected_patient
                    for key in ["prediction_result", "recommendations",
                                "clinical_insight", "top_features",
                                "shap_vals", "expected_val",
                                "patient_input", "pdf_bytes"]:
                        st.session_state.pop(key, None)
                    st.switch_page("pages/2_Patient_Assessment.py")