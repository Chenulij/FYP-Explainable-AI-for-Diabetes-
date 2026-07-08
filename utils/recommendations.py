# ============================================================
# RULE-BASED CLINICAL RECOMMENDATION ENGINE
# This is NOT a machine learning model.
# All recommendations are fixed clinical rules based on
# established medical thresholds (WHO, ADA guidelines).
# Output is for clinician review only — not autonomous diagnosis.
# ============================================================

def get_recommendations(patient: dict, prediction_label: str):
    """
    Takes patient input data and prediction label,
    returns a list of clinical recommendations based on
    fixed rule thresholds.
    """
    recs = []

    hba1c     = patient["HbA1c"]
    bmi       = patient["BMI"]
    tg        = patient["TG"]
    steps     = patient["TotalSteps"]
    sedentary = patient["SedentaryMinutes"]
    sleep_eff = patient["SleepEfficiency"]
    sleep_min = patient["TotalMinutesAsleep"]
    calories  = patient["Calories"]
    age       = patient["AGE"]

    # --- Prediction-level flag (always first) ---
    if prediction_label == "Diabetic":
        recs.append({
            "category": "Risk Alert",
            "text": "Model predicts Diabetic risk — recommend immediate full clinical workup. This is a decision-support flag only, not a diagnosis."
        })
    elif prediction_label == "Pre-diabetic":
        recs.append({
            "category": "Risk Alert",
            "text": "Model predicts Pre-diabetic risk — recommend early lifestyle intervention and close monitoring."
        })
    else:
        recs.append({
            "category": "Risk Alert",
            "text": "Model predicts Normal risk — recommend routine monitoring and continued healthy lifestyle."
        })

    # --- HbA1c rules ---
    if hba1c > 6.5:
        recs.append({
            "category": "Glycaemic Control",
            "text": "HbA1c above diabetic threshold (>6.5%) — recommend confirmatory HbA1c retest and referral to endocrinologist."
        })
    elif hba1c >= 5.7:
        recs.append({
            "category": "Glycaemic Control",
            "text": "HbA1c in pre-diabetic range (5.7–6.5%) — recommend lifestyle counselling and repeat HbA1c testing in 3–6 months."
        })

    # --- BMI rules ---
    if bmi >= 30:
        recs.append({
            "category": "Weight Management",
            "text": "BMI indicates obesity (≥30) — recommend structured weight management programme and dietary referral."
        })
    elif bmi >= 25:
        recs.append({
            "category": "Weight Management",
            "text": "BMI indicates overweight (25–29.9) — recommend dietary counselling and increased physical activity."
        })

    # --- Combined HbA1c + BMI ---
    if hba1c > 6.5 and bmi >= 30:
        recs.append({
            "category": "Medication Review",
            "text": "Combined elevated HbA1c and obesity — recommend Metformin initiation review in consultation with physician."
        })

    # --- Triglycerides ---
    if tg > 200:
        recs.append({
            "category": "Lipid Profile",
            "text": "Elevated triglycerides (>200 mg/dL) — recommend full lipid panel review and dietary fat intake assessment."
        })
    elif tg > 150:
        recs.append({
            "category": "Lipid Profile",
            "text": "Borderline high triglycerides (150–200 mg/dL) — recommend dietary review and repeat lipid panel in 3 months."
        })

    # --- Physical activity rules ---
    if steps < 5000:
        recs.append({
            "category": "Physical Activity",
            "text": "Low daily step count (<5,000 steps) — recommend gradual increase targeting 7,000–10,000 steps per day."
        })
    elif steps < 7500:
        recs.append({
            "category": "Physical Activity",
            "text": "Moderately low step count — recommend encouraging patient to increase daily walking activity."
        })

    # --- Sedentary behaviour ---
    if sedentary > 600:
        recs.append({
            "category": "Sedentary Behaviour",
            "text": "High sedentary time (>600 min/day) — recommend reducing prolonged sitting with regular movement breaks every hour."
        })

    # --- Sleep rules ---
    if sleep_eff < 0.85:
        recs.append({
            "category": "Sleep Health",
            "text": "Reduced sleep efficiency (<85%) — recommend sleep hygiene assessment; poor sleep is associated with insulin resistance."
        })
    if sleep_min < 360:
        recs.append({
            "category": "Sleep Health",
            "text": "Short sleep duration (<6 hours) — recommend sleep assessment; insufficient sleep is linked to increased diabetes risk."
        })

    # --- Age-based screening ---
    if age >= 45:
        recs.append({
            "category": "Screening",
            "text": "Patient aged 45 or above — recommend annual diabetes screening as per ADA guidelines regardless of risk level."
        })

    # --- Caloric intake ---
    if calories > 3000:
        recs.append({
            "category": "Dietary Review",
            "text": "High daily caloric intake (>3,000 kcal) — recommend dietary assessment and nutritionist referral."
        })

    # --- Fallback ---
    if len(recs) == 1:
        recs.append({
            "category": "General",
            "text": "No major clinical flags triggered — recommend maintaining current healthy lifestyle and routine annual check-up."
        })

    return recs


def get_clinical_insight(patient: dict, prediction_label: str, top_features: list):
    """
    Generates a readable clinical summary paragraph based on
    prediction, top SHAP features, and patient values.
    This is a rule-based text summary — NOT AI generated text.
    """
    hba1c = patient["HbA1c"]
    bmi   = patient["BMI"]
    steps = patient["TotalSteps"]
    age   = patient["AGE"]

    risk_phrase = {
        "Diabetic": "a high probability of Type 2 Diabetes",
        "Pre-diabetic": "an elevated risk of developing Type 2 Diabetes",
        "Normal": "a low current risk of Type 2 Diabetes"
    }.get(prediction_label, "an undetermined risk level")

    top_str = ", ".join(top_features[:3]) if top_features else "key clinical indicators"

    insight = (
        f"Based on the patient's clinical and lifestyle data, the model indicates {risk_phrase}. "
        f"The most influential factors in this prediction were {top_str}. "
    )

    if hba1c > 6.5:
        insight += f"The patient's HbA1c of {hba1c}% exceeds the diabetic diagnostic threshold of 6.5%, which is a primary clinical concern. "
    elif hba1c >= 5.7:
        insight += f"The patient's HbA1c of {hba1c}% falls within the pre-diabetic range, warranting close monitoring. "

    if bmi >= 30:
        insight += f"Obesity (BMI {bmi}) is a significant contributing lifestyle factor. "
    elif bmi >= 25:
        insight += f"The patient is overweight (BMI {bmi}), which contributes to metabolic risk. "

    if steps < 5000:
        insight += "Physical inactivity is also a notable risk factor for this patient. "

    if age >= 45:
        insight += f"At age {age}, the patient falls within the higher-risk age group for Type 2 Diabetes as per ADA screening guidelines. "

    insight += "All findings should be reviewed by the attending clinician before any clinical decision is made."

    return insight