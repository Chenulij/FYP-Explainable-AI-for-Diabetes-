# ============================================================
# RULE-BASED CLINICAL RECOMMENDATION ENGINE
# All recommendations are fixed clinical rules based on
# established medical thresholds (WHO, ADA guidelines).
# Output is for clinician review only — not autonomous diagnosis.
# ============================================================

def get_recommendations(patient: dict, prediction_label: str, previous_prediction: dict = None):
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

    # ── Risk change alert (if returning patient) ─────────────
    if previous_prediction:
        prev_label = previous_prediction["prediction_label"]
        if prev_label != prediction_label:
            # Determine if improved or worsened
            risk_order = {"Normal": 0, "Pre-diabetic": 1, "Diabetic": 2}
            prev_rank  = risk_order.get(prev_label, 0)
            curr_rank  = risk_order.get(prediction_label, 0)

            if curr_rank > prev_rank:
                recs.append({
                    "category": "⚠ Risk Change Detected",
                    "text": (
                        f"This patient's risk classification has worsened since their last visit — "
                        f"previously recorded as {prev_label}, now predicted as {prediction_label}. "
                        f"Immediate clinical review is recommended to identify contributing factors "
                        f"and initiate appropriate intervention."
                    )
                })
            else:
                recs.append({
                    "category": "✅ Risk Improvement Detected",
                    "text": (
                        f"This patient's risk classification has improved since their last visit — "
                        f"previously recorded as {prev_label}, now predicted as {prediction_label}. "
                        f"Current lifestyle and treatment approach appears to be effective. "
                        f"Continue monitoring and reinforce positive changes."
                    )
                })

            # Highlight which values changed significantly
            changes = []
            if abs(hba1c - float(previous_prediction["hba1c"])) >= 0.3:
                direction = "increased" if hba1c > float(previous_prediction["hba1c"]) else "decreased"
                changes.append(f"HbA1c {direction} from {previous_prediction['hba1c']}% to {hba1c}%")
            if abs(bmi - float(previous_prediction["bmi"])) >= 0.5:
                direction = "increased" if bmi > float(previous_prediction["bmi"]) else "decreased"
                changes.append(f"BMI {direction} from {previous_prediction['bmi']} to {bmi}")
            if abs(steps - int(previous_prediction["total_steps"])) >= 500:
                direction = "increased" if steps > int(previous_prediction["total_steps"]) else "decreased"
                changes.append(f"Daily steps {direction} from {previous_prediction['total_steps']:,} to {steps:,}")
            if abs(sleep_eff - float(previous_prediction["sleep_efficiency"])) >= 0.05:
                direction = "improved" if sleep_eff > float(previous_prediction["sleep_efficiency"]) else "declined"
                changes.append(f"Sleep efficiency {direction} from {previous_prediction['sleep_efficiency']:.0%} to {sleep_eff:.0%}")

            if changes:
                recs.append({
                    "category": "Notable Changes Since Last Visit",
                    "text": "Key changes observed compared to the previous assessment: " + "; ".join(changes) + "."
                })

    # ── Prediction-level flag ────────────────────────────────
    if prediction_label == "Diabetic":
        recs.append({
            "category": "Risk Alert",
            "text": "This patient has been flagged as high risk for Type 2 Diabetes. A full clinical workup is recommended. This is a decision-support flag only and does not constitute a clinical diagnosis."
        })
    elif prediction_label == "Pre-diabetic":
        recs.append({
            "category": "Risk Alert",
            "text": "This patient has been flagged as Pre-diabetic. Early lifestyle intervention and close monitoring are recommended to prevent progression to Type 2 Diabetes."
        })
    else:
        recs.append({
            "category": "Risk Alert",
            "text": "This patient currently shows a low risk of Type 2 Diabetes. Routine monitoring and maintenance of a healthy lifestyle are advised."
        })

    # ── HbA1c rules ──────────────────────────────────────────
    if hba1c > 6.5:
        recs.append({
            "category": "Glycaemic Control",
            "text": f"This patient's HbA1c is {hba1c}%, which is above the diabetic diagnostic threshold of 6.5%. A confirmatory HbA1c retest and referral to an endocrinologist are recommended."
        })
    elif hba1c >= 5.7:
        recs.append({
            "category": "Glycaemic Control",
            "text": f"This patient's HbA1c is {hba1c}%, which falls within the pre-diabetic range (5.7–6.4%). Lifestyle counselling and a repeat HbA1c test in 3–6 months are recommended."
        })

    # ── BMI rules ────────────────────────────────────────────
    if bmi >= 30:
        recs.append({
            "category": "Weight Management",
            "text": f"This patient's BMI is {bmi}, which indicates obesity (≥30). A structured weight management programme and dietary referral are recommended."
        })
    elif bmi >= 25:
        recs.append({
            "category": "Weight Management",
            "text": f"This patient's BMI is {bmi}, which indicates overweight (25–29.9). Dietary counselling and an increase in physical activity are recommended."
        })

    # ── Combined HbA1c + BMI ─────────────────────────────────
    if hba1c > 6.5 and bmi >= 30:
        recs.append({
            "category": "Medication Review",
            "text": f"The combination of elevated HbA1c ({hba1c}%) and obesity (BMI {bmi}) suggests a high metabolic burden. Metformin initiation should be reviewed in consultation with the attending physician."
        })

    # ── Triglycerides ────────────────────────────────────────
    if tg > 200:
        recs.append({
            "category": "Lipid Profile",
            "text": f"This patient's triglyceride level is {tg} mg/dL, which is elevated (normal <150 mg/dL). A full lipid panel review and dietary fat intake assessment are recommended."
        })
    elif tg > 150:
        recs.append({
            "category": "Lipid Profile",
            "text": f"This patient's triglyceride level is {tg} mg/dL, which is borderline high (150–200 mg/dL). A dietary review and repeat lipid panel in 3 months are recommended."
        })

    # ── Physical activity ────────────────────────────────────
    if steps < 5000:
        recs.append({
            "category": "Physical Activity",
            "text": f"This patient is recording only {steps:,} steps per day, which is below the recommended minimum of 7,500 steps. A gradual increase in daily walking activity is advised."
        })
    elif steps < 7500:
        recs.append({
            "category": "Physical Activity",
            "text": f"This patient's daily step count of {steps:,} is moderately low. Encouraging an increase in daily walking and light activity is recommended."
        })

    # ── Sedentary behaviour ──────────────────────────────────
    if sedentary > 600:
        recs.append({
            "category": "Sedentary Behaviour",
            "text": f"This patient spends approximately {sedentary} minutes per day sedentary. Regular movement breaks every hour and a reduction in prolonged sitting are advised."
        })

    # ── Sleep ────────────────────────────────────────────────
    if sleep_eff < 0.85:
        recs.append({
            "category": "Sleep Health",
            "text": f"This patient's sleep efficiency is {sleep_eff:.0%}, which is below the healthy threshold of 85%. A sleep hygiene assessment is recommended."
        })
    if sleep_min < 360:
        recs.append({
            "category": "Sleep Health",
            "text": f"This patient is sleeping approximately {sleep_min} minutes per night, which is less than the recommended 6–8 hours."
        })

    # ── Age-based screening ──────────────────────────────────
    if age >= 45:
        recs.append({
            "category": "Screening",
            "text": f"At age {age}, this patient falls within the higher-risk age group for Type 2 Diabetes. Annual diabetes screening is recommended as per ADA guidelines."
        })

    # ── Fallback ─────────────────────────────────────────────
    if len(recs) <= 2:
        recs.append({
            "category": "General",
            "text": "No major clinical flags were triggered for this patient. Maintaining the current healthy lifestyle and attending routine annual check-ups are advised."
        })

    return recs


def get_clinical_insight(patient: dict, prediction_label: str, top_features: list, previous_prediction: dict = None):
    """
    Generates a readable clinical summary paragraph.
    Includes comparison with previous visit if available.
    """
    hba1c     = patient["HbA1c"]
    bmi       = patient["BMI"]
    steps     = patient["TotalSteps"]
    age       = patient["AGE"]
    sleep_eff = patient["SleepEfficiency"]
    sedentary = patient["SedentaryMinutes"]

    clean_features = [
        f.replace(" (High Risk)", "").replace(" (Protective)", "")
        for f in top_features[:3]
    ]
    top_str = ", ".join(clean_features) if clean_features else "key clinical indicators"

    risk_phrase = {
        "Diabetic":     "a high probability of Type 2 Diabetes",
        "Pre-diabetic": "an elevated risk of developing Type 2 Diabetes",
        "Normal":       "a low current risk of Type 2 Diabetes"
    }.get(prediction_label, "an undetermined risk level")

    insight = (
        f"Based on this patient's clinical measurements and IoT wearable data, "
        f"the model predicts {risk_phrase}. "
        f"The three features that most influenced this prediction were {top_str}. "
    )

    # ── Previous visit comparison ─────────────────────────────
    if previous_prediction:
        prev_label = previous_prediction["prediction_label"]
        if prev_label != prediction_label:
            risk_order = {"Normal": 0, "Pre-diabetic": 1, "Diabetic": 2}
            if risk_order.get(prediction_label, 0) > risk_order.get(prev_label, 0):
                insight += (
                    f"Compared to their previous visit where they were classified as {prev_label}, "
                    f"this patient's condition has worsened. "
                    f"The deterioration may be linked to changes in "
                )
                # Identify what worsened
                factors = []
                if hba1c > float(previous_prediction["hba1c"]):
                    factors.append(f"rising HbA1c (from {previous_prediction['hba1c']}% to {hba1c}%)")
                if bmi > float(previous_prediction["bmi"]):
                    factors.append(f"increased BMI (from {previous_prediction['bmi']} to {bmi})")
                if steps < int(previous_prediction["total_steps"]):
                    factors.append(f"reduced physical activity ({previous_prediction['total_steps']:,} to {steps:,} steps)")
                if sleep_eff < float(previous_prediction["sleep_efficiency"]):
                    factors.append(f"declining sleep efficiency ({previous_prediction['sleep_efficiency']:.0%} to {sleep_eff:.0%})")
                if factors:
                    insight += ", ".join(factors) + ". "
                else:
                    insight += "overall metabolic changes. "
                insight += "Prompt clinical review and intervention are advised. "
            else:
                insight += (
                    f"Encouragingly, compared to their previous visit where they were classified as {prev_label}, "
                    f"this patient's condition has improved to {prediction_label}. "
                )
                factors = []
                if hba1c < float(previous_prediction["hba1c"]):
                    factors.append(f"reduced HbA1c (from {previous_prediction['hba1c']}% to {hba1c}%)")
                if bmi < float(previous_prediction["bmi"]):
                    factors.append(f"lower BMI (from {previous_prediction['bmi']} to {bmi})")
                if steps > int(previous_prediction["total_steps"]):
                    factors.append(f"increased physical activity ({previous_prediction['total_steps']:,} to {steps:,} steps)")
                if sleep_eff > float(previous_prediction["sleep_efficiency"]):
                    factors.append(f"improved sleep efficiency ({previous_prediction['sleep_efficiency']:.0%} to {sleep_eff:.0%})")
                if factors:
                    insight += "Key improvements include: " + ", ".join(factors) + ". "
                insight += "Current management approach appears effective — continue monitoring. "
        else:
            insight += (
                f"The patient's risk classification remains {prediction_label} compared to their previous visit. "
            )

    # ── Current clinical context ──────────────────────────────
    if hba1c > 6.5:
        insight += (
            f"The patient's HbA1c reading of {hba1c}% is above the diabetic diagnostic threshold of 6.5%, "
            f"making it the most significant clinical concern in this assessment. "
        )
    elif hba1c >= 5.7:
        insight += (
            f"The patient's HbA1c of {hba1c}% sits within the pre-diabetic range, "
            f"suggesting impaired glucose regulation that warrants close monitoring. "
        )
    else:
        insight += (
            f"The patient's HbA1c of {hba1c}% is within the normal range, which is a positive indicator. "
        )

    if bmi >= 30:
        insight += f"Obesity (BMI {bmi}) is a significant contributing lifestyle factor. "
    elif bmi >= 25:
        insight += f"The patient is overweight (BMI {bmi}), which contributes to metabolic risk. "

    if steps < 5000:
        insight += f"With only {steps:,} daily steps recorded, physical inactivity is a notable risk factor. "

    if sedentary > 600:
        insight += f"High sedentary time of {sedentary} minutes per day further compounds the metabolic risk. "

    if sleep_eff < 0.85:
        insight += f"Sleep efficiency of {sleep_eff:.0%} is below the healthy threshold. "

    if age >= 45:
        insight += f"At age {age}, the patient falls within the higher-risk age group per ADA guidelines. "

    insight += (
        "All findings are generated by an AI-assisted decision support tool and must be reviewed "
        "by the attending clinician before any clinical action is taken."
    )

    return insight