import streamlit as st
import matplotlib.pyplot as plt
from utils.predictor import predict
from utils.recommendations import get_recommendations, get_clinical_insight
from utils.shap_explainer import get_shap_values, get_top_features, plot_waterfall, plot_shap_bar
from utils.database import save_prediction, save_recommendations, get_previous_prediction

# ============================================================
# AUTH GUARD
# ============================================================
if "doctor" not in st.session_state or not st.session_state.doctor:
    st.switch_page("app.py")

if "patient_input" not in st.session_state:
    st.switch_page("pages/2_Patient_Assessment.py")

doctor        = st.session_state.doctor
patient_info  = st.session_state.patient_info
patient_input = st.session_state.patient_input
patient_db_id = st.session_state.patient_db_id

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
    .diabetic-card    { background: #fef2f2; border: 2px solid #dc2626; }
    .prediabetic-card { background: #fffbeb; border: 2px solid #d97706; }
    .normal-card      { background: #f0fdf4; border: 2px solid #16a34a; }
    .insight-box {
        background: #eff6ff;
        border-left: 4px solid #2563eb;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
        font-size: 0.95rem;
        line-height: 1.8;
        color: #1e293b;
    }
    .rec-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
        border-left: 3px solid #2563eb;
        border: 1px solid #e2e8f0;
    }
    .rec-category {
        font-size: 0.72rem;
        font-weight: 700;
        color: #2563eb;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.3rem;
    }
    .rec-text {
        font-size: 0.92rem;
        color: #1e293b;
        line-height: 1.6;
    }
    .risk-factor-item {
        background: #ffffff;
        border-radius: 8px;
        padding: 0.5rem 0.9rem;
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
        color: #1e293b;
        border: 1px solid #e2e8f0;
    }
    .risk-tag {
        display: inline-block;
        border-radius: 4px;
        padding: 0.1rem 0.5rem;
        font-size: 0.72rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .tag-high    { background: #fef2f2; color: #dc2626; }
    .tag-protect { background: #f0fdf4; color: #16a34a; }
    .chart-explainer {
        background: #f8fafc;
        border-radius: 8px;
        padding: 0.9rem 1.2rem;
        margin-top: 0.8rem;
        font-size: 0.88rem;
        color: #64748b;
        line-height: 1.7;
        border-left: 3px solid #cbd5e1;
    }
    .change-banner-worse {
        background: #fef2f2;
        border: 1px solid #dc2626;
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1rem;
        color: #dc2626;
        font-weight: 600;
    }
    .change-banner-better {
        background: #f0fdf4;
        border: 1px solid #16a34a;
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1rem;
        color: #16a34a;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
col_title, col_back = st.columns([6, 1])
with col_title:
    st.title("📊 Prediction Results")
    st.caption(
        f"Patient: **{patient_info['full_name']}** · "
        f"Code: {patient_info['patient_code']}"
    )
with col_back:
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

st.divider()

# ============================================================
# RUN PREDICTION (only once per assessment)
# ============================================================
if "prediction_result" not in st.session_state:
    with st.spinner("Running prediction model..."):

        # Step 1 — Run prediction
        result = predict(patient_input)

        # Step 2 — SHAP
        shap_vals, expected_val = get_shap_values(
            result["input_scaled"],
            result["pred_encoded"]
        )
        top_features = get_top_features(shap_vals)

        # Step 3 — Save prediction to DB first
        prediction_id = save_prediction(
            patient_db_id,
            doctor["id"],
            patient_input,
            result["prediction_label"],
            result["confidence"]
        )

        # Step 4 — Get previous prediction (second most recent)
        # OFFSET 1 skips the one we just saved
        previous_prediction = get_previous_prediction(patient_db_id)

        # Step 5 — Generate recommendations and insight
        # with previous context now available
        recommendations = get_recommendations(
            patient_input,
            result["prediction_label"],
            previous_prediction
        )
        clinical_insight = get_clinical_insight(
            patient_input,
            result["prediction_label"],
            top_features,
            previous_prediction
        )

        # Step 6 — Save recommendations
        save_recommendations(prediction_id, recommendations)

        # Store everything in session
        st.session_state.prediction_result   = result
        st.session_state.shap_vals           = shap_vals
        st.session_state.expected_val        = expected_val
        st.session_state.top_features        = top_features
        st.session_state.recommendations     = recommendations
        st.session_state.clinical_insight    = clinical_insight
        st.session_state.prediction_id       = prediction_id
        st.session_state.previous_prediction = previous_prediction

# Load from session
result              = st.session_state.prediction_result
shap_vals           = st.session_state.shap_vals
expected_val        = st.session_state.expected_val
top_features        = st.session_state.top_features
recommendations     = st.session_state.recommendations
clinical_insight    = st.session_state.clinical_insight
previous_prediction = st.session_state.get("previous_prediction", None)
label               = result["prediction_label"]
confidence          = result["confidence"]
all_proba           = result["all_probabilities"]

# ============================================================
# RISK CHANGE BANNER (if returning patient)
# ============================================================
if previous_prediction:
    prev_label = previous_prediction["prediction_label"]
    if prev_label != label:
        risk_order = {"Normal": 0, "Pre-diabetic": 1, "Diabetic": 2}
        if risk_order.get(label, 0) > risk_order.get(prev_label, 0):
            st.markdown(f"""
                <div class='change-banner-worse'>
                    ⚠️ Risk has worsened since last visit: {prev_label} → {label}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='change-banner-better'>
                    ✅ Risk has improved since last visit: {prev_label} → {label}
                </div>
            """, unsafe_allow_html=True)

# ============================================================
# SECTION 1 — PREDICTION RESULT
# ============================================================
st.markdown("### 🎯 Risk Prediction")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if label == "Diabetic":
        card_class = "diabetic-card"
        icon       = "🔴"
        color      = "#dc2626"
    elif label == "Pre-diabetic":
        card_class = "prediabetic-card"
        icon       = "🟠"
        color      = "#d97706"
    else:
        card_class = "normal-card"
        icon       = "🟢"
        color      = "#16a34a"

    prev_html = (
        f"<div style='margin-top:0.5rem; font-size:0.85rem; color:#64748b'>"
        f"Previous: {previous_prediction['prediction_label']} "
        f"({previous_prediction['confidence']:.1f}%)</div>"
        if previous_prediction else ""
    )

    st.markdown(f"""
        <div class='result-card {card_class}'>
            <div style='font-size:3rem'>{icon}</div>
            <div style='font-size:2rem; font-weight:bold; color:{color}'>{label}</div>
            <div style='font-size:1.1rem; color:#64748b; margin-top:0.3rem'>
                Model Confidence: <strong>{confidence:.1f}%</strong>
            </div>
            {prev_html}
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("**Class Probabilities**")
    for class_name, prob in sorted(all_proba.items(), key=lambda x: x[1], reverse=True):
        if class_name == "Diabetic":
            bar_color = "#dc2626"
        elif class_name == "Pre-diabetic":
            bar_color = "#d97706"
        else:
            bar_color = "#16a34a"
        st.markdown(f"""
            <div style='margin-bottom:0.6rem'>
                <span style='color:{bar_color}; font-weight:bold'>{class_name}</span>
                <span style='float:right'>{prob:.1f}%</span>
                <div style='background:#f1f5f9; border-radius:4px; height:8px; margin-top:4px'>
                    <div style='background:{bar_color}; width:{prob}%;
                                height:8px; border-radius:4px'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

with col3:
    st.markdown("**Top Contributing Factors**")
    for i, feat in enumerate(top_features, 1):
        if "(" in feat:
            name, direction = feat.rsplit("(", 1)
            direction = direction.rstrip(")")
            name = name.strip()
        else:
            name = feat
            direction = ""

        tag_class  = "tag-high" if direction == "High Risk" else "tag-protect"
        label_text = "⚠ Risk Factor" if direction == "High Risk" else "✓ Protective"

        st.markdown(f"""
            <div class='risk-factor-item'>
                <strong>{i}. {name}</strong>
                <span class='risk-tag {tag_class}'>{label_text}</span>
            </div>
        """, unsafe_allow_html=True)

st.divider()

# ============================================================
# SECTION 2 — CLINICAL INSIGHT
# ============================================================
st.markdown("### 💡 Clinical Insight")
st.markdown(
    f"<div class='insight-box'>{clinical_insight}</div>",
    unsafe_allow_html=True
)

st.divider()

# ============================================================
# SECTION 3 — SHAP EXPLANATION
# ============================================================
st.markdown("### 🔍 Explainable AI — SHAP Analysis")

tab1, tab2 = st.tabs(["📊 Waterfall Chart", "📈 Feature Importance"])

with tab1:
    st.caption("Shows how each feature pushed the prediction toward (red) or away from (green) the predicted risk class.")
    fig_waterfall = plot_waterfall(shap_vals, expected_val, label)
    st.pyplot(fig_waterfall)
    plt.close()
    st.markdown("""
        <div class='chart-explainer'>
            <strong>How to read this chart:</strong> Each bar represents one patient feature.
            A <span style='color:#dc2626; font-weight:bold'>red bar</span> means that feature
            increased the likelihood of the predicted class.
            A <span style='color:#16a34a; font-weight:bold'>green bar</span> means that feature
            worked against the predicted class, acting as a protective factor.
            The longer the bar, the stronger the influence.
        </div>
    """, unsafe_allow_html=True)

with tab2:
    st.caption("Shows the overall importance of each feature in this prediction, regardless of direction.")
    fig_bar = plot_shap_bar(shap_vals, label)
    st.pyplot(fig_bar)
    plt.close()
    st.markdown("""
        <div class='chart-explainer'>
            <strong>How to read this chart:</strong> Each bar shows how much a feature
            influenced the model's prediction for this patient by its absolute SHAP value.
            This view does not show direction — only how much each feature mattered overall.
        </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================
# SECTION 4 — CLINICAL RECOMMENDATIONS
# ============================================================
st.markdown("### 📋 Clinical Recommendations")
st.caption("Rule-based suggestions from established clinical thresholds — for clinician review only.")

for rec in recommendations:
    st.markdown(f"""
        <div class='rec-card'>
            <div class='rec-category'>{rec['category']}</div>
            <div class='rec-text'>{rec['text']}</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================
# ACTION BUTTONS
# ============================================================
col_a, col_b, col_c = st.columns(3)
with col_a:
    if st.button("🔄 What-If Simulation", use_container_width=True, type="primary"):
        st.switch_page("pages/4_What_If_Simulation.py")
with col_b:
    if st.button("📄 Generate PDF Report", use_container_width=True):
        st.session_state.pop("pdf_bytes", None)
        st.switch_page("pages/5_Patient_Report.py")
with col_c:
    if st.button("👥 Back to Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")