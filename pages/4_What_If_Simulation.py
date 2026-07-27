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
st.set_page_config(page_title="What-If Simulation", page_icon="🔄", layout="wide")
from utils.styles import load_css
load_css()
render_sidebar("What-If Simulation")
# ============================================================
# CUSTOM CSS
# ============================================================


# ============================================================
# HEADER
# ============================================================
col_title, col_back = st.columns([6, 1])
with col_title:
    st.title("🔄 What-If Simulation")
    st.caption(
        f"Patient: **{patient_info['full_name']}** · "
        f"Adjust values below to see how lifestyle or clinical changes affect the predicted risk."
    )
with col_back:
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("← Results", use_container_width=True):
        st.switch_page("pages/3_Prediction_Results.py")

st.divider()

# ============================================================
# ORIGINAL PREDICTION (from session)
# ============================================================
original_result = st.session_state.prediction_result
original_label  = original_result["prediction_label"]
original_conf   = original_result["confidence"]

# ============================================================
# LAYOUT — Controls left, Results right
# ============================================================
col_controls, col_results = st.columns([1, 1])

with col_controls:
    st.markdown("### ⚙️ Adjust Patient Values")
    st.caption("Modify any value and click **Run Simulation** to see the updated prediction.")

    # --- Clinical sliders ---
    st.markdown("**Clinical Measurements**")

    sim_hba1c = st.slider(
        "HbA1c (%)",
        min_value=2.0, max_value=20.0,
        value=float(patient_input["HbA1c"]),
        step=0.1,
        help="Normal <5.7% | Pre-diabetic 5.7–6.4% | Diabetic ≥6.5%"
    )
    sim_bmi = st.slider(
        "BMI (kg/m²)",
        min_value=10.0, max_value=70.0,
        value=float(patient_input["BMI"]),
        step=0.1,
        help="Normal 18.5–24.9 | Overweight 25–29.9 | Obese ≥30"
    )
    sim_tg = st.slider(
        "Triglycerides (mg/dL)",
        min_value=0.0, max_value=1000.0,
        value=float(patient_input["TG"]),
        step=1.0
    )

    st.markdown("**Lifestyle & IoT Data**")

    sim_steps = st.slider(
        "Daily Steps",
        min_value=0, max_value=30000,
        value=int(patient_input["TotalSteps"]),
        step=100
    )
    sim_sedentary = st.slider(
        "Sedentary Minutes",
        min_value=0, max_value=1440,
        value=int(patient_input["SedentaryMinutes"]),
        step=10
    )
    sim_sleep_eff = st.slider(
        "Sleep Efficiency (0–1)",
        min_value=0.0, max_value=1.0,
        value=float(patient_input["SleepEfficiency"]),
        step=0.01
    )
    sim_sleep_min = st.slider(
        "Total Minutes Asleep",
        min_value=0, max_value=1440,
        value=int(patient_input["TotalMinutesAsleep"]),
        step=10
    )
    sim_calories = st.slider(
        "Calories Burned",
        min_value=0, max_value=10000,
        value=int(patient_input["Calories"]),
        step=50
    )

    run_btn = st.button("▶ Run Simulation", type="primary", use_container_width=True)

with col_results:
    st.markdown("### 📊 Simulation Results")

    # --- Always show original ---
    st.markdown("**Original Prediction**")
    if original_label == "Diabetic":
        orig_color = "#e74c3c"
        orig_icon  = "🔴"
    elif original_label == "Pre-diabetic":
        orig_color = "#f39c12"
        orig_icon  = "🟠"
    else:
        orig_color = "#27ae60"
        orig_icon  = "🟢"

    st.markdown(f"""
        <div class='original-card'>
            <span style='font-size:1.5rem'>{orig_icon}</span>
            <span style='font-size:1.3rem; font-weight:bold; color:{orig_color}; margin-left:0.5rem'>
                {original_label}
            </span>
            <span style='color:#7f8c8d; margin-left:1rem'>Confidence: {original_conf:.1f}%</span>
        </div>
    """, unsafe_allow_html=True)

    if run_btn:
        # Build simulated input (keep non-adjusted values from original)
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

        # --- Updated prediction card ---
        st.markdown("**Updated Prediction**")

        if sim_label == "Diabetic":
            sim_card  = "diabetic-card"
            sim_color = "#e74c3c"
            sim_icon  = "🔴"
        elif sim_label == "Pre-diabetic":
            sim_card  = "prediabetic-card"
            sim_color = "#f39c12"
            sim_icon  = "🟠"
        else:
            sim_card  = "normal-card"
            sim_color = "#27ae60"
            sim_icon  = "🟢"

        st.markdown(f"""
            <div class='updated-card {sim_card}'>
                <span style='font-size:1.5rem'>{sim_icon}</span>
                <span style='font-size:1.3rem; font-weight:bold; color:{sim_color}; margin-left:0.5rem'>
                    {sim_label}
                </span>
                <span style='color:#7f8c8d; margin-left:1rem'>Confidence: {sim_conf:.1f}%</span>
            </div>
        """, unsafe_allow_html=True)

        # --- Confidence change ---
        conf_diff = sim_conf - original_conf
        if sim_label != original_label:
            st.success(f"✅ Risk classification changed: **{original_label} → {sim_label}**")
        else:
            if conf_diff < 0:
                st.info(f"📉 Same classification but confidence reduced by **{abs(conf_diff):.1f}%** — risk is trending better.")
            elif conf_diff > 0:
                st.warning(f"📈 Same classification but confidence increased by **{conf_diff:.1f}%** — risk is trending worse.")
            else:
                st.info("No change in prediction or confidence.")

        # --- Probability comparison table ---
        st.markdown("**Probability Comparison**")
        orig_proba = original_result["all_probabilities"]

        for class_name in ["Normal", "Pre-diabetic", "Diabetic"]:
            orig_p = orig_proba.get(class_name, 0)
            sim_p  = sim_proba.get(class_name, 0)
            diff   = sim_p - orig_p

            if diff < -1:
                arrow = "⬇️"
                css   = "change-better" if class_name == "Diabetic" else "change-worse"
            elif diff > 1:
                arrow = "⬆️"
                css   = "change-worse" if class_name == "Diabetic" else "change-better"
            else:
                arrow = "➡️"
                css   = "change-same"

            st.markdown(
                f"**{class_name}:** {orig_p:.1f}% → "
                f"<span class='{css}'>{sim_p:.1f}% {arrow} ({diff:+.1f}%)</span>",
                unsafe_allow_html=True
            )

        # --- SHAP for simulated input ---
        st.markdown("**Feature Contributions (Simulated)**")
        sim_shap, sim_ev = get_shap_values(
            sim_result["input_scaled"],
            sim_result["pred_encoded"]
        )
        fig = plot_waterfall(sim_shap, sim_ev, sim_label)
        st.pyplot(fig)
        plt.close()

    else:
        st.info("Adjust the sliders on the left and click **▶ Run Simulation** to see the updated prediction.")

st.divider()

col_a, col_b = st.columns(2)
with col_a:
    if st.button("📄 Generate Report", use_container_width=True):
        st.switch_page("pages/5_Patient_Report.py")
with col_b:
    if st.button("👥 Back to Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")