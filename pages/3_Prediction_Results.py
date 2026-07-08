import streamlit as st
import matplotlib.pyplot as plt
from utils.predictor import predict
from utils.recommendations import get_recommendations, get_clinical_insight
from utils.shap_explainer import get_shap_values, get_top_features, plot_waterfall, plot_shap_bar
from utils.database import save_prediction, save_recommendations

# ============================================================
# AUTH GUARD
# ============================================================
if "doctor" not in st.session_state or not st.session_state.doctor:
    st.switch_page("app.py")

if "patient_input" not in st.session_state:
    st.switch_page("pages/2_Patient_Assessment.py")

doctor       = st.session_state.doctor
patient_info = st.session_state.patient_info
patient_input= st.session_state.patient_input
patient_db_id= st.session_state.patient_db_id

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Prediction Results", page_icon="📊", layout="wide")

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
    <style>
    .result-card {
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .diabetic-card   { background: #fdecea; border: 2px solid #e74c3c; }
    .prediabetic-card{ background: #fef9e7; border: 2px solid #f39c12; }
    .normal-card     { background: #eafaf1; border: 2px solid #27ae60; }
    .insight-box {
        background: #f0f4ff;
        border-left: 4px solid #1a73e8;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        font-size: 0.95rem;
        line-height: 1.7;
        color: #2c3e50;
    }
    .rec-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #1a73e8;
    }
    .rec-category {
        font-size: 0.75rem;
        font-weight: bold;
        color: #1a73e8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .rec-text {
        font-size: 0.9rem;
        color: #2c3e50;
        margin-top: 0.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
col_title, col_back = st.columns([6, 1])
with col_title:
    st.title("📊 Prediction Results")
    st.caption(f"Patient: **{patient_info['full_name']}** · Code: {patient_info['patient_code']}")
with col_back:
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

st.divider()

# ============================================================
# RUN PREDICTION (only once, cache in session state)
# ============================================================
if "prediction_result" not in st.session_state:
    with st.spinner("Running prediction model..."):
        result = predict(patient_input)

    # SHAP
    shap_vals, expected_val = get_shap_values(
        result["input_scaled"],
        result["pred_encoded"]
    )
    top_features = get_top_features(shap_vals)

    # Recommendations + clinical insight
    recommendations  = get_recommendations(patient_input, result["prediction_label"])
    clinical_insight = get_clinical_insight(patient_input, result["prediction_label"], top_features)

    # Save to database
    prediction_id = save_prediction(
        patient_db_id,
        doctor["id"],
        patient_input,
        result["prediction_label"],
        result["confidence"]
    )
    save_recommendations(prediction_id, recommendations)

    # Store in session state
    st.session_state.prediction_result  = result
    st.session_state.shap_vals          = shap_vals
    st.session_state.expected_val       = expected_val
    st.session_state.top_features       = top_features
    st.session_state.recommendations    = recommendations
    st.session_state.clinical_insight   = clinical_insight
    st.session_state.prediction_id      = prediction_id

# Load from session
result          = st.session_state.prediction_result
shap_vals       = st.session_state.shap_vals
expected_val    = st.session_state.expected_val
top_features    = st.session_state.top_features
recommendations = st.session_state.recommendations
clinical_insight= st.session_state.clinical_insight
label           = result["prediction_label"]
confidence      = result["confidence"]
all_proba       = result["all_probabilities"]

# ============================================================
# SECTION 1 — PREDICTION RESULT
# ============================================================
st.markdown("### 🎯 Risk Prediction")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
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
        <div class='result-card {card_class}'>
            <div style='font-size:3rem'>{icon}</div>
            <div style='font-size:2rem; font-weight:bold; color:{color}'>{label}</div>
            <div style='font-size:1.1rem; color:#7f8c8d; margin-top:0.3rem'>
                Confidence: <strong>{confidence:.1f}%</strong>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("**Class Probabilities**")
    for class_name, prob in sorted(all_proba.items(), key=lambda x: x[1], reverse=True):
        if class_name == "Diabetic":
            color = "#e74c3c"
        elif class_name == "Pre-diabetic":
            color = "#f39c12"
        else:
            color = "#27ae60"
        st.markdown(f"""
            <div style='margin-bottom:0.5rem'>
                <span style='color:{color}; font-weight:bold'>{class_name}</span>
                <span style='float:right'>{prob:.1f}%</span>
                <div style='background:#ecf0f1; border-radius:4px; height:8px; margin-top:3px'>
                    <div style='background:{color}; width:{prob}%; height:8px; border-radius:4px'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with col3:
    st.markdown("**Top Risk Factors (SHAP)**")
    for i, feat in enumerate(top_features, 1):
        st.markdown(f"**{i}.** {feat}")

st.divider()

# ============================================================
# SECTION 2 — CLINICAL INSIGHT
# ============================================================
st.markdown("### 💡 Clinical Insight")
st.markdown(f"<div class='insight-box'>{clinical_insight}</div>", unsafe_allow_html=True)

st.divider()

# ============================================================
# SECTION 3 — SHAP EXPLANATION
# ============================================================
st.markdown("### 🔍 Explainable AI — SHAP Analysis")
st.caption("Shows which features contributed most to this prediction. Red = pushes toward predicted class. Green = pushes away.")

tab1, tab2 = st.tabs(["Waterfall Chart", "Feature Importance Bar"])

with tab1:
    fig_waterfall = plot_waterfall(shap_vals, expected_val, label)
    st.pyplot(fig_waterfall)
    plt.close()

with tab2:
    fig_bar = plot_shap_bar(shap_vals, label)
    st.pyplot(fig_bar)
    plt.close()

st.divider()

# ============================================================
# SECTION 4 — CLINICAL RECOMMENDATIONS
# ============================================================
st.markdown("### 📋 Clinical Recommendations")
st.caption("Rule-based suggestions for clinician review only — not autonomous diagnosis or prescription.")

for rec in recommendations:
    st.markdown(f"""
        <div class='rec-card'>
            <div class='rec-category'>{rec['category']}</div>
            <div class='rec-text'>{rec['text']}</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================
# SECTION 5 — ACTION BUTTONS
# ============================================================
col_a, col_b, col_c = st.columns(3)

with col_a:
    if st.button("🔄 What-If Simulation", use_container_width=True, type="primary"):
        st.switch_page("pages/4_What_If_Simulation.py")

with col_b:
    if st.button("📄 Generate PDF Report", use_container_width=True):
        st.switch_page("pages/5_Patient_Report.py")

with col_c:
    if st.button("👥 Back to Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")