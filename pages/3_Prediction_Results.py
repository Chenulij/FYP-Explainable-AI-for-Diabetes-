import streamlit as st
import matplotlib.pyplot as plt
from utils.predictor import predict
from utils.recommendations import get_recommendations, get_clinical_insight
from utils.shap_explainer import get_shap_values, get_top_features, plot_waterfall, plot_shap_bar
from utils.database import save_prediction, save_recommendations, get_previous_prediction
from utils.styles import load_css, render_sidebar

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
st.set_page_config(page_title="Prediction Results", page_icon="🩺", layout="wide")
load_css()
render_sidebar("Prediction Results")

# ============================================================
# DESIGN SYSTEM — same tokens as the other pages
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

    :root {
        --navy-900: #0B2C4A;
        --teal-500: #0F8B8D;
        --teal-bg:  #EAF6F6;
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

    .page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink-900); margin: 0; letter-spacing: -0.01em; }
    .page-sub   { color: var(--ink-600); font-size: 0.88rem; margin-top: 0.15rem; }
    .section-title { font-size: 1.02rem; font-weight: 700; color: var(--ink-900); margin: 0 0 0.9rem 0; }

    /* ---------- result card ---------- */
    .result-card {
        border-radius: var(--radius);
        padding: 1.5rem;
        text-align: center;
        background: #fff;
        border: 1px solid var(--line);
        border-top: 4px solid var(--result-accent, var(--navy-900));
    }
    .result-label { font-size: 1.9rem; font-weight: 700; color: var(--result-accent, var(--navy-900)); }
    .result-conf  { font-size: 1rem; color: var(--ink-600); margin-top: 0.3rem; }
    .result-prev  { margin-top: 0.6rem; font-size: 0.84rem; color: var(--ink-400); }

    /* ---------- change banner ---------- */
    .change-banner {
        border-radius: 9px;
        padding: 0.75rem 1.1rem;
        margin-bottom: 1.1rem;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid var(--banner-accent);
        background: var(--banner-bg);
        color: var(--banner-accent);
    }

    /* ---------- probability bars ---------- */
    .prob-row { margin-bottom: 0.7rem; }
    .prob-name { font-weight: 600; }
    .prob-pct { float: right; color: var(--ink-600); font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; }
    .prob-track { background: #F1F5F9; border-radius: 4px; height: 7px; margin-top: 5px; }
    .prob-fill  { height: 7px; border-radius: 4px; }

    /* ---------- risk factor list ---------- */
    .risk-factor-item {
        background: #fff;
        border: 1px solid var(--line);
        border-radius: 9px;
        padding: 0.55rem 0.9rem;
        margin-bottom: 0.4rem;
        font-size: 0.88rem;
        color: var(--ink-900);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .risk-tag {
        border-radius: 999px;
        padding: 0.12rem 0.6rem;
        font-size: 0.72rem;
        font-weight: 700;
    }
    .tag-high    { background: var(--danger-bg);  color: var(--danger); }
    .tag-protect { background: var(--success-bg); color: var(--success); }

    /* ---------- insight box ---------- */
    .insight-box {
        background: var(--teal-bg);
        border-left: 4px solid var(--teal-500);
        border-radius: 9px;
        padding: 1.1rem 1.4rem;
        font-size: 0.94rem;
        line-height: 1.75;
        color: var(--ink-900);
    }

    /* ---------- recommendation cards ---------- */
    .rec-card {
        background: #fff;
        border-radius: 9px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.55rem;
        border: 1px solid var(--line);
        border-left: 3px solid var(--navy-900);
    }
    .rec-category {
        font-size: 0.7rem;
        font-weight: 700;
        color: var(--teal-500);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.25rem;
    }
    .rec-text { font-size: 0.9rem; color: var(--ink-900); line-height: 1.6; }

    /* ---------- chart explainer ---------- */
    .chart-explainer {
        background: #F8FAFC;
        border-left: 3px solid var(--line);
        border-radius: 9px;
        padding: 0.85rem 1.2rem;
        margin-top: 0.8rem;
        font-size: 0.86rem;
        color: var(--ink-600);
        line-height: 1.7;
    }

    /* ---------- tabs -> segmented control ---------- */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0; background: #EAEFF5; padding: 4px; border-radius: 10px;
        width: fit-content; margin-bottom: 1.2rem;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 8px; padding: 0.5rem 1.2rem; font-weight: 600;
        font-size: 0.86rem; color: var(--ink-600);
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: #fff; color: var(--navy-900); box-shadow: 0 1px 3px rgba(16,24,40,0.12);
    }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"],
    [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }

    /* ---------- buttons ---------- */
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
    </style>
""", unsafe_allow_html=True)

RISK_TOKENS = {
    "Diabetic":     {"accent": "var(--danger)",  "bg": "var(--danger-bg)"},
    "Pre-diabetic": {"accent": "var(--warn)",     "bg": "var(--warn-bg)"},
    "Normal":       {"accent": "var(--success)",  "bg": "var(--success-bg)"},
}

with st.container(key="page-content"):

    # ============================================================
    # HEADER — no local Dashboard button here; the top nav already
    # covers navigation. (Bottom action row keeps a "Back to
    # Dashboard" button because it's part of the end-of-flow
    # actions, not a duplicate of the nav.)
    # ============================================================
    st.markdown(f"""
        <div class="page-title">Prediction Results</div>
        <div class="page-sub">Patient: <b>{patient_info['full_name']}</b> · Code: {patient_info['patient_code']}</div>
    """, unsafe_allow_html=True)
    st.write("")

    # ============================================================
    # RUN PREDICTION (only once per assessment)
    # ============================================================
    if "prediction_result" not in st.session_state:
        with st.spinner("Running prediction model..."):
            result = predict(patient_input)

            shap_vals, expected_val = get_shap_values(
                result["input_scaled"], result["pred_encoded"]
            )
            top_features = get_top_features(shap_vals)

            prediction_id = save_prediction(
                patient_db_id, doctor["id"], patient_input,
                result["prediction_label"], result["confidence"]
            )

            previous_prediction = get_previous_prediction(patient_db_id)

            recommendations = get_recommendations(
                patient_input, result["prediction_label"], previous_prediction
            )
            clinical_insight = get_clinical_insight(
                patient_input, result["prediction_label"], top_features, previous_prediction
            )

            save_recommendations(prediction_id, recommendations)

            st.session_state.prediction_result   = result
            st.session_state.shap_vals           = shap_vals
            st.session_state.expected_val        = expected_val
            st.session_state.top_features        = top_features
            st.session_state.recommendations     = recommendations
            st.session_state.clinical_insight    = clinical_insight
            st.session_state.prediction_id       = prediction_id
            st.session_state.previous_prediction = previous_prediction

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

    tokens = RISK_TOKENS.get(label, {"accent": "var(--navy-900)", "bg": "#F1F5F9"})

    # ============================================================
    # RISK CHANGE BANNER (if returning patient)
    # ============================================================
    if previous_prediction:
        prev_label = previous_prediction["prediction_label"]
        if prev_label != label:
            risk_order = {"Normal": 0, "Pre-diabetic": 1, "Diabetic": 2}
            worse = risk_order.get(label, 0) > risk_order.get(prev_label, 0)
            b_accent = "var(--danger)" if worse else "var(--success)"
            b_bg     = "var(--danger-bg)" if worse else "var(--success-bg)"
            verb     = "worsened" if worse else "improved"
            st.markdown(f"""
                <div class="change-banner" style="--banner-accent:{b_accent}; --banner-bg:{b_bg}">
                    Risk has {verb} since last visit: {prev_label} → {label}
                </div>
            """, unsafe_allow_html=True)

    # ============================================================
    # SECTION 1 — PREDICTION RESULT
    # ============================================================
    st.markdown('<div class="section-title">Risk Prediction</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        prev_html = (
            f"<div class='result-prev'>Previous: {previous_prediction['prediction_label']} "
            f"({previous_prediction['confidence']:.1f}%)</div>"
            if previous_prediction else ""
        )
        st.markdown(f"""
            <div class="result-card" style="--result-accent:{tokens['accent']}">
                <div class="result-label">{label}</div>
                <div class="result-conf">Model Confidence: <strong>{confidence:.1f}%</strong></div>
                {prev_html}
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("**Class Probabilities**")
        for class_name, prob in sorted(all_proba.items(), key=lambda x: x[1], reverse=True):
            bar_color = RISK_TOKENS.get(class_name, {}).get("accent", "var(--navy-900)")
            st.markdown(f"""
                <div class="prob-row">
                    <span class="prob-name" style="color:{bar_color}">{class_name}</span>
                    <span class="prob-pct">{prob:.1f}%</span>
                    <div class="prob-track"><div class="prob-fill" style="background:{bar_color}; width:{prob}%"></div></div>
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
                name, direction = feat, ""

            tag_class  = "tag-high" if direction == "High Risk" else "tag-protect"
            label_text = "Risk Factor" if direction == "High Risk" else "Protective"

            st.markdown(f"""
                <div class="risk-factor-item">
                    <span><strong>{i}.</strong> {name}</span>
                    <span class="risk-tag {tag_class}">{label_text}</span>
                </div>
            """, unsafe_allow_html=True)

    st.write("")

    # ============================================================
    # SECTION 2 — CLINICAL INSIGHT
    # ============================================================
    st.markdown('<div class="section-title">Clinical Insight</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='insight-box'>{clinical_insight}</div>", unsafe_allow_html=True)
    st.write("")

    # ============================================================
    # SECTION 3 — SHAP EXPLANATION
    # (Chart colors themselves come from utils/shap_explainer.py —
    # not editable here without that file.)
    # ============================================================
    st.markdown('<div class="section-title">Explainable AI — SHAP Analysis</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Waterfall Chart", "Feature Importance"])

    with tab1:
        st.caption("Shows how each feature pushed the prediction toward (red) or away from (green) the predicted risk class.")
        fig_waterfall = plot_waterfall(shap_vals, expected_val, label)
        st.pyplot(fig_waterfall)
        plt.close()
        st.markdown("""
            <div class='chart-explainer'>
                <strong>How to read this chart:</strong> each bar represents one patient feature.
                A red bar increased the likelihood of the predicted class; a green bar worked
                against it, acting as a protective factor. The longer the bar, the stronger the influence.
            </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.caption("Shows the overall importance of each feature in this prediction, regardless of direction.")
        fig_bar = plot_shap_bar(shap_vals, label)
        st.pyplot(fig_bar)
        plt.close()
        st.markdown("""
            <div class='chart-explainer'>
                <strong>How to read this chart:</strong> each bar shows how much a feature
                influenced the model's prediction for this patient, by absolute SHAP value.
                This view does not show direction — only how much each feature mattered overall.
            </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ============================================================
    # SECTION 4 — CLINICAL RECOMMENDATIONS
    # ============================================================
    st.markdown('<div class="section-title">Clinical Recommendations</div>', unsafe_allow_html=True)
    st.caption("Rule-based suggestions from established clinical thresholds — for clinician review only.")

    for rec in recommendations:
        st.markdown(f"""
            <div class="rec-card">
                <div class="rec-category">{rec['category']}</div>
                <div class="rec-text">{rec['text']}</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ============================================================
    # ACTION BUTTONS
    # ============================================================
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("What-If Simulation", use_container_width=True, type="primary"):
            st.switch_page("pages/4_What_If_Simulation.py")
    with col_b:
        if st.button("Generate PDF Report", use_container_width=True, type="secondary"):
            st.session_state.pop("pdf_bytes", None)
            st.switch_page("pages/5_Patient_Report.py")
    with col_c:
        if st.button("Back to Dashboard", use_container_width=True, type="secondary"):
            st.switch_page("pages/1_Dashboard.py")