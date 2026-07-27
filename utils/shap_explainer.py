import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shap
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from utils.predictor import model, scaler, le, feature_columns

# ============================================================
# BUILD SHAP EXPLAINER
# ============================================================
explainer = shap.TreeExplainer(model)

# ============================================================
# GET SHAP VALUES FOR ONE PATIENT
# ============================================================
def get_shap_values(input_scaled, pred_encoded):
    shap_values = explainer.shap_values(input_scaled)
    pred_class_index = list(model.classes_).index(pred_encoded)

    if isinstance(shap_values, list):
        sv = shap_values[pred_class_index][0]
        ev = explainer.expected_value[pred_class_index]
    else:
        sv = shap_values[0, :, pred_class_index]
        ev = explainer.expected_value[pred_class_index]

    return sv, ev

# ============================================================
# GET TOP FEATURES — readable labels for display
# ============================================================
def get_top_features(shap_vals, n=3):
    """
    Returns top n features as clean readable strings.
    e.g. "HbA1c (High Risk)" or "AGE (Protective)"
    """
    indices = np.argsort(np.abs(shap_vals))[::-1][:n]
    top = []
    for i in indices:
        feature = feature_columns[i]
        direction = "High Risk" if shap_vals[i] > 0 else "Protective"
        top.append(f"{feature} ({direction})")
    return top

# ============================================================
# WATERFALL CHART
# ============================================================
def plot_waterfall(shap_vals, expected_value, prediction_label):
    """
    Horizontal bar chart showing each feature's contribution
    toward or away from the predicted class.
    Red = pushes toward predicted class.
    Green = pushes away (protective factor).
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    indices = np.argsort(np.abs(shap_vals))
    sorted_features = [feature_columns[i] for i in indices]
    sorted_vals     = [shap_vals[i] for i in indices]
    colors          = ['#e74c3c' if v > 0 else '#2ecc71' for v in sorted_vals]

    bars = ax.barh(sorted_features, sorted_vals, color=colors)
    ax.axvline(x=0, color='black', linewidth=0.8)
    ax.set_xlabel("SHAP Value (Impact on Prediction)", fontsize=11)
    ax.set_title(
        f"Feature Contributions — Predicted: {prediction_label}",
        fontsize=13, pad=12, fontweight='bold'
    )

    for bar, val in zip(bars, sorted_vals):
        ax.text(
            val + (0.002 if val >= 0 else -0.002),
            bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}",
            va='center',
            ha='left' if val >= 0 else 'right',
            fontsize=9
        )

    plt.tight_layout()
    return fig

# ============================================================
# FEATURE IMPORTANCE BAR CHART
# ============================================================
def plot_shap_bar(shap_vals, prediction_label):
    """
    Horizontal bar chart showing absolute SHAP values —
    how much each feature influenced the prediction,
    regardless of direction.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    abs_vals        = np.abs(shap_vals)
    indices         = np.argsort(abs_vals)
    sorted_features = [feature_columns[i] for i in indices]
    sorted_abs      = [abs_vals[i] for i in indices]

    ax.barh(sorted_features, sorted_abs, color='#3498db')
    ax.set_xlabel("Absolute SHAP Value (Overall Influence on Prediction)", fontsize=11)
    ax.set_title(
        f"Feature Importance — Predicted: {prediction_label}",
        fontsize=13, pad=12, fontweight='bold'
    )

    for i, val in enumerate(sorted_abs):
        ax.text(val + 0.001, i, f"{val:.3f}", va='center', fontsize=9)

    plt.tight_layout()
    return fig