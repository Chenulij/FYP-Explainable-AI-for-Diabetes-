import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import io

# ============================================================
# COLOUR PALETTE
# ============================================================
PRIMARY    = colors.HexColor("#1a73e8")
DANGER     = colors.HexColor("#e74c3c")
WARNING    = colors.HexColor("#f39c12")
SUCCESS    = colors.HexColor("#27ae60")
LIGHT_GREY = colors.HexColor("#f5f6fa")
DARK_GREY  = colors.HexColor("#2c3e50")
MID_GREY   = colors.HexColor("#7f8c8d")

# ============================================================
# RISK COLOUR HELPER
# ============================================================
def risk_color(label):
    if label == "Diabetic":
        return DANGER
    elif label == "Pre-diabetic":
        return WARNING
    return SUCCESS

# ============================================================
# GENERATE PDF — returns bytes (for Streamlit download button)
# ============================================================
def generate_report(
    patient_info: dict,
    doctor_info: dict,
    prediction_label: str,
    confidence: float,
    all_probabilities: dict,
    clinical_insight: str,
    recommendations: list,
    top_features: list,
    shap_fig=None
) -> bytes:
    """
    Builds a PDF clinical report and returns it as bytes.
    Call this from the Report page and pass to st.download_button.
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Custom styles ──────────────────────────────────────────
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=PRIMARY,
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold"
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=MID_GREY,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        fontName="Helvetica-Bold"
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=16,
        textColor=DARK_GREY,
        alignment=TA_JUSTIFY
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        textColor=MID_GREY,
        alignment=TA_CENTER,
        spaceBefore=20
    )

    # ── Header ─────────────────────────────────────────────────
    story.append(Paragraph("Clinical Decision Support System", title_style))
    story.append(Paragraph("Diabetes Risk Prediction Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY))
    story.append(Spacer(1, 0.4*cm))

    # ── Report metadata ────────────────────────────────────────
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")
    meta_data = [
        ["Report Generated:", now],
        ["Attending Doctor:", doctor_info.get("full_name", "—")],
        ["Doctor ID:",        doctor_info.get("doctor_id", "—")],
        ["Specialization:",   doctor_info.get("specialization", "—")],
    ]
    meta_table = Table(meta_data, colWidths=[4.5*cm, 12*cm])
    meta_table.setStyle(TableStyle([
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("TEXTCOLOR",   (0,0), (0,-1), MID_GREY),
        ("TEXTCOLOR",   (1,0), (1,-1), DARK_GREY),
        ("FONTNAME",    (0,0), (0,-1), "Helvetica"),
        ("FONTNAME",    (1,0), (1,-1), "Helvetica-Bold"),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GREY))

    # ── Patient Information ────────────────────────────────────
    story.append(Paragraph("Patient Information", section_style))
    pat_data = [
        ["Patient Code:",   patient_info.get("patient_code", "—"),
         "Full Name:",      patient_info.get("full_name", "—")],
        ["Date of Birth:",  str(patient_info.get("date_of_birth", "—")),
         "Gender:",         patient_info.get("gender", "—")],
        ["Contact:",        patient_info.get("contact_number", "—"),
         "Age:",            str(patient_info.get("AGE", "—"))],
    ]
    pat_table = Table(pat_data, colWidths=[3.5*cm, 7*cm, 3*cm, 4*cm])
    pat_table.setStyle(TableStyle([
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("TEXTCOLOR",    (0,0), (-1,-1), DARK_GREY),
        ("FONTNAME",     (0,0), (0,-1), "Helvetica"),
        ("FONTNAME",     (1,0), (1,-1), "Helvetica-Bold"),
        ("FONTNAME",     (2,0), (2,-1), "Helvetica"),
        ("FONTNAME",     (3,0), (3,-1), "Helvetica-Bold"),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ("BACKGROUND",   (0,0), (-1,-1), LIGHT_GREY),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [LIGHT_GREY, colors.white]),
    ]))
    story.append(pat_table)

    # ── Clinical Input Data ────────────────────────────────────
    story.append(Paragraph("Clinical & IoT Input Data", section_style))
    input_data = [
        ["Parameter", "Value", "Parameter", "Value"],
        ["HbA1c (%)",          str(patient_info.get("HbA1c", "—")),
         "Total Steps",        str(patient_info.get("TotalSteps", "—"))],
        ["BMI",                str(patient_info.get("BMI", "—")),
         "Sedentary Min",      str(patient_info.get("SedentaryMinutes", "—"))],
        ["Triglycerides",      str(patient_info.get("TG", "—")),
         "Calories",           str(patient_info.get("Calories", "—"))],
        ["Sleep (min)",        str(patient_info.get("TotalMinutesAsleep", "—")),
         "Sleep Efficiency",   str(patient_info.get("SleepEfficiency", "—"))],
    ]
    input_table = Table(input_data, colWidths=[4.5*cm, 4*cm, 4.5*cm, 4.5*cm])
    input_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LIGHT_GREY, colors.white]),
        ("GRID",         (0,0), (-1,-1), 0.25, colors.HexColor("#dce1e7")),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
    ]))
    story.append(input_table)

    # ── Prediction Result ──────────────────────────────────────
    story.append(Paragraph("Prediction Result", section_style))
    rc = risk_color(prediction_label)
    pred_data = [
        ["Risk Level", "Confidence", "Normal %", "Pre-diabetic %", "Diabetic %"],
        [
            prediction_label,
            f"{confidence:.1f}%",
            f"{all_probabilities.get('Normal', 0):.1f}%",
            f"{all_probabilities.get('Pre-diabetic', 0):.1f}%",
            f"{all_probabilities.get('Diabetic', 0):.1f}%",
        ]
    ]
    pred_table = Table(pred_data, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 4*cm, 3*cm])
    pred_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("BACKGROUND",   (0,1), (0,1), rc),
        ("TEXTCOLOR",    (0,1), (0,1), colors.white),
        ("FONTNAME",     (0,1), (0,1), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("GRID",         (0,0), (-1,-1), 0.25, colors.HexColor("#dce1e7")),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
    ]))
    story.append(pred_table)

    # ── Top Contributing Features ──────────────────────────────
    if top_features:
        story.append(Paragraph("Top Contributing Features (SHAP)", section_style))
        for i, feat in enumerate(top_features, 1):
            story.append(Paragraph(f"{i}. {feat}", body_style))
        story.append(Spacer(1, 0.3*cm))

    # ── SHAP Chart (if provided) ───────────────────────────────
    if shap_fig is not None:
        try:
            import io as _io
            from reportlab.platypus import Image as RLImage
            img_buffer = _io.BytesIO()
            shap_fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            story.append(Paragraph("SHAP Explanation Chart", section_style))
            story.append(RLImage(img_buffer, width=16*cm, height=8*cm))
            story.append(Spacer(1, 0.3*cm))
        except Exception:
            pass

    # ── Clinical Insight ───────────────────────────────────────
    story.append(Paragraph("Clinical Insight", section_style))
    story.append(Paragraph(clinical_insight, body_style))

    # ── Recommendations ────────────────────────────────────────
    story.append(Paragraph("Clinical Recommendations", section_style))
    story.append(Paragraph(
        "The following recommendations are rule-based suggestions for clinician review only. "
        "They do not constitute a clinical diagnosis or prescription.",
        ParagraphStyle("RecNote", parent=body_style, textColor=MID_GREY, fontSize=9)
    ))
    story.append(Spacer(1, 0.2*cm))

    for rec in recommendations:
        category = rec.get("category", "General")
        text     = rec.get("text", "")
        rec_data = [[f"[{category}]", text]]
        rec_table = Table(rec_data, colWidths=[3.5*cm, 13*cm])
        rec_table.setStyle(TableStyle([
            ("FONTNAME",     (0,0), (0,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0), (-1,-1), 9),
            ("TEXTCOLOR",    (0,0), (0,0), PRIMARY),
            ("TEXTCOLOR",    (1,0), (1,0), DARK_GREY),
            ("VALIGN",       (0,0), (-1,-1), "TOP"),
            ("BOTTOMPADDING",(0,0), (-1,-1), 5),
            ("TOPPADDING",   (0,0), (-1,-1), 5),
            ("ROWBACKGROUNDS",(0,0),(-1,-1), [LIGHT_GREY, colors.white]),
        ]))
        story.append(rec_table)
        story.append(Spacer(1, 0.1*cm))

    # ── Disclaimer ─────────────────────────────────────────────
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY))
    story.append(Paragraph(
        "DISCLAIMER: This report is generated by an AI-assisted Clinical Decision Support System for informational purposes only. "
        "All findings must be reviewed and validated by a qualified healthcare professional before any clinical decision is made. "
        "This system does not provide autonomous medical diagnoses or prescriptions.",
        disclaimer_style
    ))

    # ── Build PDF ──────────────────────────────────────────────
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()