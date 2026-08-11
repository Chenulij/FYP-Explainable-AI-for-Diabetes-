import streamlit as st
import matplotlib.pyplot as plt
from utils.predictor import predict_whatif
from utils.shap_explainer import get_shap_values, get_top_features, plot_waterfall
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

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="What-If Simulation", page_icon="🩺", layout="wide")
load_css()
render_sidebar("What-If Simulation")

# ============================================================
# DESIGN SYSTEM — same tokens as the other pages
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
    .section-title { font-size: 1.02rem; font-weight: 700; color: var(--ink-900); margin: 0 0 0.6rem 0; }

    /* ---------- prediction cards ---------- */
    .result-card {
        border-radius: var(--radius);
        padding: 1rem 1.3rem;
        background: #fff;
        border: 1px solid var(--line);
        border-left: 4px solid var(--card-accent, var(--navy-900));
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .result-card .rc-label { font-size: 1.25rem; font-weight: 700; color: var(--card-accent, var(--navy-900)); }
    .result-card .rc-conf  { color: var(--ink-600); font-size: 0.9rem; }

    /* ---------- inputs ---------- */
    [data-testid="stSlider"] label { font-size: 0.85rem; font-weight: 600; color: var(--ink-900); }

    /* ---------- probability comparison ---------- */
    .prob-compare { font-size: 0.92rem; margin-bottom: 0.4rem; color: var(--ink-900); }
    .prob-better { color: var(--success); font-weight: 700; }
    .prob-worse  { color: var(--danger); font-weight: 700; }
    .prob-same   { color: var(--ink-600); font-weight: 700; }

    /* ---------- tabs / buttons ---------- */
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

    [data-testid="stAlert"] { border-radius: 9px; font-size: 0.88rem; }
    </style>
""", unsafe_allow_html=True)

RISK_TOKENS = {
    "Diabetic":     "var(--danger)",
    "Pre-diabetic": "var(--warn)",
    "Normal":       "var(--success)",
}

with st.container(key="page-content"):

    # ============================================================
    # HEADER — "Results" isn't reachable from the top nav, so this
    # contextual back button stays (not a duplicate).
    # ============================================================
    col_title, col_back = st.columns([6, 1])
    with col_title:
        st.markdown(f"""
            <div class="page-title">What-If Simulation</div>
            <div class="page-sub">Patient: <b>{patient_info['full_name']}</b> · Adjust values below to see how lifestyle or clinical changes affect the predicted risk.</div>
        """, unsafe_allow_html=True)
    with col_back:
        st.write("")
        if st.button("← Results", use_container_width=True, type="secondary"):
            st.switch_page("pages/3_Prediction_Results.py")

    st.write("")

    # ============================================================
    # ORIGINAL PREDICTION (from session)
    # ============================================================
    original_result = st.session_state.prediction_result
    original_label  = original_result["prediction_label"]
    original_conf   = original_result["confidence"]

    # ============================================================
    # LAYOUT — Controls left, Results right
    # ============================================================
    col_controls, col_results = st.columns(2)

    with col_controls:
        with st.container(border=True):
            st.markdown('<div class="section-title">Adjust Patient Values</div>', unsafe_allow_html=True)
            st.caption("Modify any value and click **Run Simulation** to see the updated prediction.")

            st.markdown("**Clinical Measurements**")
            sim_hba1c = st.slider(
                "HbA1c (%)", min_value=2.0, max_value=20.0,
                value=float(patient_input["HbA1c"]), step=0.1,
                help="Normal <5.7% | Pre-diabetic 5.7–6.4% | Diabetic ≥6.5%"
            )
            sim_bmi = st.slider(
                "BMI (kg/m²)", min_value=10.0, max_value=70.0,
                value=float(patient_input["BMI"]), step=0.1,
                help="Normal 18.5–24.9 | Overweight 25–29.9 | Obese ≥30"
            )
            sim_tg = st.slider(
                "Triglycerides (mg/dL)", min_value=0.0, max_value=1000.0,
                value=float(patient_input["TG"]), step=1.0
            )

            st.markdown("**Lifestyle & IoT Data**")
            sim_steps = st.slider(
                "Daily Steps", min_value=0, max_value=30000,
                value=int(patient_input["TotalSteps"]), step=100
            )
            sim_sedentary = st.slider(
                "Sedentary Minutes", min_value=0, max_value=1440,
                value=int(patient_input["SedentaryMinutes"]), step=10
            )
            sim_sleep_eff = st.slider(
                "Sleep Efficiency (0–1)", min_value=0.0, max_value=1.0,
                value=float(patient_input["SleepEfficiency"]), step=0.01
            )
            sim_sleep_min = st.slider(
                "Total Minutes Asleep", min_value=0, max_value=1440,
                value=int(patient_input["TotalMinutesAsleep"]), step=10
            )
            sim_calories = st.slider(
                "Calories Burned", min_value=0, max_value=10000,
                value=int(patient_input["Calories"]), step=50
            )

            run_btn = st.button("Run Simulation", type="primary", use_container_width=True)

    with col_results:
        with st.container(border=True):
            st.markdown('<div class="section-title">Simulation Results</div>', unsafe_allow_html=True)

            st.markdown("**Original Prediction**")
            st.markdown(f"""
                <div class="result-card" style="--card-accent:{RISK_TOKENS.get(original_label, 'var(--navy-900)')}">
                    <span class="rc-label">{original_label}</span>
                    <span class="rc-conf">Confidence: {original_conf:.1f}%</span>
                </div>
            """, unsafe_allow_html=True)

            if run_btn:
                sim_input = {
                    "Gender":             patient_input["Gender"],
                    "AGE":                patient_input["AGE"],
                    "HbA1c":              sim_hba1c,
                    "TG":                 sim_tg,
                    "BMI":                sim_bmi,
                    "TotalSteps":         sim_steps,
                    "SedentaryMinutes":   sim_sedentary,
                    "Calories":           sim_calories,
                    "TotalMinutesAsleep": sim_sleep_min,
                    "SleepEfficiency":    sim_sleep_eff,
                }

                with st.spinner("Running simulation..."):
                    sim_result = predict_whatif(sim_input)

                sim_label = sim_result["prediction_label"]
                sim_conf  = sim_result["confidence"]
                sim_proba = sim_result["all_probabilities"]

                st.write("")
                st.markdown("**Updated Prediction**")
                st.markdown(f"""
                    <div class="result-card" style="--card-accent:{RISK_TOKENS.get(sim_label, 'var(--navy-900)')}">
                        <span class="rc-label">{sim_label}</span>
                        <span class="rc-conf">Confidence: {sim_conf:.1f}%</span>
                    </div>
                """, unsafe_allow_html=True)

                conf_diff = sim_conf - original_conf
                if sim_label != original_label:
                    st.success(f"Risk classification changed: **{original_label} → {sim_label}**")
                else:
                    if conf_diff < 0:
                        st.info(f"Same classification but confidence reduced by **{abs(conf_diff):.1f}%** — risk is trending better.")
                    elif conf_diff > 0:
                        st.warning(f"Same classification but confidence increased by **{conf_diff:.1f}%** — risk is trending worse.")
                    else:
                        st.info("No change in prediction or confidence.")

                st.write("")
                st.markdown("**Probability Comparison**")
                orig_proba = original_result["all_probabilities"]

                for class_name in ["Normal", "Pre-diabetic", "Diabetic"]:
                    orig_p = orig_proba.get(class_name, 0)
                    sim_p  = sim_proba.get(class_name, 0)
                    diff   = sim_p - orig_p

                    if diff < -1:
                        arrow = "▼"
                        css   = "prob-better" if class_name == "Diabetic" else "prob-worse"
                    elif diff > 1:
                        arrow = "▲"
                        css   = "prob-worse" if class_name == "Diabetic" else "prob-better"
                    else:
                        arrow = "→"
                        css   = "prob-same"

                    st.markdown(
                        f"<div class='prob-compare'>{class_name}: {orig_p:.1f}% → "
                        f"<span class='{css}'>{sim_p:.1f}% {arrow} ({diff:+.1f}%)</span></div>",
                        unsafe_allow_html=True
                    )

                st.write("")
                st.markdown("**Feature Contributions (Simulated)**")
                sim_shap, sim_ev = get_shap_values(
                    sim_result["input_scaled"], sim_result["pred_encoded"]
                )
                fig = plot_waterfall(sim_shap, sim_ev, sim_label)
                st.pyplot(fig)
                plt.close()

            else:
                st.info("Adjust the sliders on the left and click **Run Simulation** to see the updated prediction.")

    st.write("")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Generate Report", use_container_width=True, type="secondary"):
            st.switch_page("pages/5_Patient_Report.py")
    with col_b:
        if st.button("Back to Dashboard", use_container_width=True, type="secondary"):
            st.switch_page("pages/1_Dashboard.py")