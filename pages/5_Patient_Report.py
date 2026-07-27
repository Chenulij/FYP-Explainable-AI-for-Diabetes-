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

doctor          = st.session_state.doctor
patient_info    = st.session_state.patient_info
patient_input   = st.session_state.patient_input
result          = st.session_state.prediction_result
shap_vals       = st.session_state.shap_vals
expected_val    = st.session_state.expected_val
top_features    = st.session_state.top_features
recommendations = st.session_state.recommendations
clinical_insight= st.session_state.clinical_insight

label      = result["prediction_label"]
confidence = result["confidence"]
all_proba  = result["all_probabilities"]

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Patient Report", page_icon="📄", layout="centered")
from utils.styles import load_css
load_css()
render_sidebar("patient_report")

# ============================================================
# HEADER
# ============================================================
col_title, col_back = st.columns([5, 1])
with col_title:
    st.title("📄 Generate Patient Report")
    st.caption(
        f"Patient: **{patient_info.get('full_name', '—')}** · "
        f"Code: {patient_info.get('patient_code', '—')} · "
        f"Doctor: {doctor['full_name']}"
    )
with col_back:
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("← Results", use_container_width=True):
        st.switch_page("pages/3_Prediction_Results.py")

st.divider()

# ============================================================
# RISK SUMMARY CARD
# ============================================================
if label == "Diabetic":
    card_class = "diabetic-card"
    icon       = "🔴"
    color      = "#e74c3c"
elif label == "Pre-diabetic":
    card_class = "prediabetic-card"
    icon       = "🟠"
    color      = "#f39c12"
else:
    card_class = "normal-card"
    icon       = "🟢"
    color      = "#27ae60"

st.markdown(f"""
    <div class='summary-card {card_class}'>
        <div style='font-size:2.5rem'>{icon}</div>
        <div style='font-size:1.6rem; font-weight:bold; color:{color}; margin-top:0.3rem'>
            {label}
        </div>
        <div style='color:#7f8c8d; margin-top:0.3rem'>
            Confidence: <strong>{confidence:.1f}%</strong>
        </div>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# WHAT'S IN THE PDF
# ============================================================
st.markdown("### 📋 This report includes:")
st.markdown("""
- Patient details and clinical input data
- Prediction result with class probabilities
- Top contributing features (SHAP)
- SHAP explanation chart
- Clinical insight summary
- Rule-based clinical recommendations
- Disclaimer
""")

st.info("💡 You have already reviewed the full prediction and explanation on the Results page. Click below to generate the PDF for your records.")

st.divider()

# ============================================================
# GENERATE & DOWNLOAD
# ============================================================
if "pdf_bytes" not in st.session_state:
    if st.button("⚙️ Generate PDF Report", type="primary", use_container_width=True):
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
    st.success("✅ PDF report is ready to download!")
    st.download_button(
        label               = "📄 Download PDF Report",
        data                = st.session_state.pdf_bytes,
        file_name           = f"CDSS_Report_{patient_info.get('patient_code', 'patient')}.pdf",
        mime                = "application/pdf",
        use_container_width = True
    )
    if st.button("🔄 Regenerate Report", use_container_width=True):
        st.session_state.pop("pdf_bytes", None)
        st.rerun()

st.divider()

# ============================================================
# NAVIGATION
# ============================================================
col_a, col_b, col_c = st.columns(3)
with col_a:
    if st.button("🔄 What-If Simulation", use_container_width=True):
        st.session_state.pop("pdf_bytes", None)
        st.switch_page("pages/4_What_If_Simulation.py")
with col_b:
    if st.button("📊 Back to Results", use_container_width=True):
        st.session_state.pop("pdf_bytes", None)
        st.switch_page("pages/3_Prediction_Results.py")
with col_c:
    if st.button("👥 Dashboard", use_container_width=True):
        st.session_state.pop("pdf_bytes", None)
        st.switch_page("pages/1_Dashboard.py")