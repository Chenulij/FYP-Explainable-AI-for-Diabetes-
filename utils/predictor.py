import joblib
import json
import numpy as np
import pandas as pd
import os

# ============================================================
# LOAD MODEL ARTIFACTS
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

model = joblib.load(os.path.join(MODELS_DIR, "rf_model.pkl"))
scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
le = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))

with open(os.path.join(MODELS_DIR, "feature_columns.json"), "r") as f:
    feature_columns = json.load(f)

# ============================================================
# PREDICT FUNCTION
# ============================================================
def predict(input_data: dict):
    """
    Takes a dictionary of patient input values,
    scales them, runs the RF model, and returns:
    - prediction_label (Diabetic / Normal / Pre-diabetic)
    - confidence (% for the predicted class)
    - all_probabilities (dict of all 3 class probabilities)
    - input_scaled (for SHAP explanation)
    - input_df (for reference)
    """

    # Build dataframe in the exact column order the model expects
    input_df = pd.DataFrame([input_data])[feature_columns]

    # Scale using the same scaler from training
    input_scaled = scaler.transform(input_df)

    # Predict
    pred_encoded = model.predict(input_scaled)[0]
    pred_proba = model.predict_proba(input_scaled)[0]

    # Decode label back to readable string
    prediction_label = le.inverse_transform([pred_encoded])[0]

    # Confidence = probability of the predicted class
    confidence = round(float(np.max(pred_proba)) * 100, 2)

    # All class probabilities as a readable dict
    all_probabilities = {
        le.inverse_transform([i])[0]: round(float(p) * 100, 2)
        for i, p in enumerate(pred_proba)
    }

    return {
        "prediction_label": prediction_label,
        "confidence": confidence,
        "all_probabilities": all_probabilities,
        "input_scaled": input_scaled,
        "input_df": input_df,
        "pred_encoded": pred_encoded
    }

# ============================================================
# WHAT-IF PREDICT (same as predict, just a named alias
# so pages can distinguish a what-if call from a real one)
# ============================================================
def predict_whatif(input_data: dict):
    """Same as predict() but used for what-if simulation calls."""
    return predict(input_data)

# ============================================================
# GET MODEL INFO (useful for displaying in the UI)
# ============================================================
def get_model_info():
    return {
        "model_type": "Random Forest Classifier",
        "n_estimators": model.n_estimators,
        "max_depth": model.max_depth,
        "features": feature_columns,
        "classes": list(le.classes_)
    }