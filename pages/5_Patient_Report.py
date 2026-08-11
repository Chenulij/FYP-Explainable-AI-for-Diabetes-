import streamlit as st
import matplotlib.pyplot as plt
from utils.report_generator import generate_report
from utils.shap_explainer import plot_waterfall
from utils.styles import load_css, render_sidebar

# ============================================================
# AUTH GUARD
# ============================================================
if "doctor" not in st.session_state or not st.session_state.doctor:
    st.switch_page("app.py")

if "prediction_result" not in st.session_state:
    st.switch_page("pages/2_Patient_Assessment.py")

doctor           = st.session_state.doctor
patient_info     = st.session_state.patient_info
patient_input    = st.session_state.patient_input
result           = st.session_state.prediction_result
shap_vals        = st.session_state.shap_vals
expected_val     = st.session_state.expected_val
top_features     = st.session_state.top_features
recommendations  = st.session_state.recommendations
clinical_insight = st.session_state.clinical_insight

label      = result["prediction_label"]
confidence = result["confidence"]
all_proba  = result["all_probabilities"]

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Patient Report", page_icon="🩺", layout="wide")
load_css()
render_sidebar("Patient Report")

# ============================================================
# DESIGN SYSTEM — same tokens as the other pages. Report content
# gets a narrower centered column for readability (overrides the
# page-content width just on this page).
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

    :root {
        --navy-900: #0B2C4A;
        --teal-500: #0F8B8D;
        --ink-900:  #101828;
        --ink-600:  #475467;
        --line:     #E4E9F0;
        --danger:   #D92D20;
        --warn:     #B45309;
        --success:  #15803D;
        --radius:   12px;
    }

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', -apple-system, sans-serif; }

    .st-key-page-content { max-width: 800px; margin: 0 auto; }

    .page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink-900); margin: 0; letter-spacing: -0.01em; }
    .page-sub   { color: var(--ink-600); font-size: 0.88rem; margin-top: 0.15rem; }

    .summary-card {
        border-radius: var(--radius);
        padding: 1.6rem;
        text-align: center;
        background: #fff;
        border: 1px solid var(--line);
        border-top: 4px solid var(--card-accent, var(--navy-900));
        margin: 1.2rem 0;
    }
    .summary-card .sc-label { font-size: 1.7rem; font-weight: 700; color: var(--card-accent, var(--navy-900)); }
    .summary-card .sc-conf  { color: var(--ink-600); margin-top: 0.3rem; }

    [data-testid="stButton"] button[kind="primary"] {
        background: var(--navy-900); border: none; border-radius: 9px; font-weight: 600;
    }
    [data-testid="stButton"] button[kind="primary"]:hover { background: var(--teal-500); }
    [data-testid="stButton"] button[kind="secondary"] {
        border: 1.5px solid var(--line); border-radius: 9px; color: var(--navy-900);
        font-weight: 600; background: #fff;
    }
    [data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: var(--teal-500); color: var(--teal-500);
    }
    [data-testid="stAlert"] { border-radius: 9px; font-size: 0.9rem; }
    [data-testid="stDownloadButton"] button {
        background: var(--teal-500); border: none; border-radius: 9px; font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

RISK_TOKENS = {
    "Diabetic":     "var(--danger)",
    "Pre-diabetic": "var(--warn)",
    "Normal":       "var(--success)",
}

with st.container(key="page-content"):

    # ============================================================
    # HEADER
    # (No back-to-Results button here — the bottom nav row already
    # has one, and having both was a genuine duplicate.)
    # ============================================================
    st.markdown(f"""
        <div class="page-title">Generate Patient Report</div>
        <div class="page-sub">Patient: <b>{patient_info.get('full_name', '—')}</b> · Code: {patient_info.get('patient_code', '—')} · Doctor: {doctor['full_name']}</div>
    """, unsafe_allow_html=True)

    # ============================================================
    # RISK SUMMARY CARD
    # ============================================================
    st.markdown(f"""
        <div class="summary-card" style="--card-accent:{RISK_TOKENS.get(label, 'var(--navy-900)')}">
            <div class="sc-label">{label}</div>
            <div class="sc-conf">Confidence: <strong>{confidence:.1f}%</strong></div>
        </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # WHAT'S IN THE PDF
    # ============================================================
    st.markdown("### This report includes:")
    st.markdown("""
- Patient details and clinical input data
- Prediction result with class probabilities
- Top contributing features (SHAP)
- SHAP explanation chart
- Clinical insight summary
- Rule-based clinical recommendations
- Disclaimer
    """)

    st.info("You have already reviewed the full prediction and explanation on the Results page. Click below to generate the PDF for your records.")

    st.write("")

    # ============================================================
    # GENERATE & DOWNLOAD
    # ============================================================
    if "pdf_bytes" not in st.session_state:
        if st.button("Generate PDF Report", type="primary", use_container_width=True):
            with st.spinner("Building PDF report..."):
                pdf_fig           = plot_waterfall(shap_vals, expected_val, label)
                full_patient_data = {**patient_input, **patient_info}

                pdf_bytes = generate_report(
                    patient_info      = full_patient_data,
                    doctor_info       = doctor,
                    prediction_label  = label,
                    confidence        = confidence,
                    all_probabilities = all_proba,
                    clinical_insight  = clinical_insight,
                    recommendations   = recommendations,
                    top_features      = top_features,
                    shap_fig          = pdf_fig
                )
                plt.close('all')
                st.session_state.pdf_bytes = pdf_bytes
                st.rerun()
    else:
        st.success("PDF report is ready to download!")
        st.download_button(
            label               = "Download PDF Report",
            data                = st.session_state.pdf_bytes,
            file_name           = f"CDSS_Report_{patient_info.get('patient_code', 'patient')}.pdf",
            mime                = "application/pdf",
            use_container_width = True
        )
        if st.button("Regenerate Report", use_container_width=True, type="secondary"):
            st.session_state.pop("pdf_bytes", None)
            st.rerun()

    st.write("")

    # ============================================================
    # NAVIGATION — single set of "next step" actions
    # ============================================================
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("What-If Simulation", use_container_width=True, type="secondary"):
            st.session_state.pop("pdf_bytes", None)
            st.switch_page("pages/4_What_If_Simulation.py")
    with col_b:
        if st.button("Back to Results", use_container_width=True, type="secondary"):
            st.session_state.pop("pdf_bytes", None)
            st.switch_page("pages/3_Prediction_Results.py")
    with col_c:
        if st.button("Dashboard", use_container_width=True, type="secondary"):
            st.session_state.pop("pdf_bytes", None)
            st.switch_page("pages/1_Dashboard.py")