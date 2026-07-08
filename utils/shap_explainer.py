import shap
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend, required for Streamlit
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.predictor import model, scaler, le, feature_columns

# ============================================================
# BUILD SHAP EXPLAINER (once, reused across all calls)
# ============================================================
explainer = shap.TreeExplainer(model)

# ============================================================
# GET SHAP VALUES FOR ONE PATIENT
# ============================================================
def get_shap_values(input_scaled, pred_encoded):
    """
    Calculates SHAP values for a single patient prediction.
    Returns shap_values array and expected_value for the predicted class.
    """
    shap_values = explainer.shap_values(input_scaled)
    pred_class_index = list(model.classes_).index(pred_encoded)

    # Handle both old (list) and new (array) shap output formats
    if isinstance(shap_values, list):
        sv = shap_values[pred_class_index][0]
        ev = explainer.expected_value[pred_class_index]
    else:
        sv = shap_values[0, :, pred_class_index]
        ev = explainer.expected_value[pred_class_index]

    return sv, ev

# ============================================================
# GET TOP CONTRIBUTING FEATURES (for clinical insight text)
# ============================================================
def get_top_features(shap_vals, n=3):
    """
    Returns the names of the top n features by absolute SHAP value.
    Used by recommendations.py to build the clinical insight paragraph.
    """
    indices = np.argsort(np.abs(shap_vals))[::-1][:n]
    top = []
    for i in indices:
        feature = feature_columns[i]
        direction = "↑" if shap_vals[i] > 0 else "↓"
        top.append(f"{feature} {direction}")
    return top

# ============================================================
# WATERFALL CHART
# ============================================================
def plot_waterfall(shap_vals, expected_value, prediction_label):
    """
    Generates a SHAP waterfall chart for a single patient.
    Returns a matplotlib figure ready to display in Streamlit.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    # Sort features by absolute SHAP value for readability
    indices = np.argsort(np.abs(shap_vals))
    sorted_features = [feature_columns[i] for i in indices]
    sorted_vals = [shap_vals[i] for i in indices]

    colors = ['#e74c3c' if v > 0 else '#2ecc71' for v in sorted_vals]

    bars = ax.barh(sorted_features, sorted_vals, color=colors)

    ax.axvline(x=0, color='black', linewidth=0.8)
    ax.set_xlabel("SHAP Value (Impact on Prediction)", fontsize=11)
    ax.set_title(
        f"Feature Contributions — Predicted: {prediction_label}\n"
        f"Red = pushes toward this class  |  Green = pushes away",
        fontsize=12, pad=12
    )

    # Add value labels on bars
    for bar, val in zip(bars, sorted_vals):
        ax.text(
            val + (0.001 if val >= 0 else -0.001),
            bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}",
            va='center',
            ha='left' if val >= 0 else 'right',
            fontsize=9
        )

    plt.tight_layout()
    return fig

# ============================================================
# SHAP BAR CHART (global-style for a single patient)
# ============================================================
def plot_shap_bar(shap_vals, prediction_label):
    """
    Generates a horizontal bar chart of absolute SHAP values.
    Simpler than waterfall — good for a quick overview.
    Returns a matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    abs_vals = np.abs(shap_vals)
    indices = np.argsort(abs_vals)
    sorted_features = [feature_columns[i] for i in indices]
    sorted_abs = [abs_vals[i] for i in indices]

    ax.barh(sorted_features, sorted_abs, color='#3498db')
    ax.set_xlabel("Mean |SHAP Value| (Feature Importance for this Patient)", fontsize=11)
    ax.set_title(
        f"Feature Importance — Predicted: {prediction_label}",
        fontsize=12, pad=12
    )
    plt.tight_layout()
    return fig