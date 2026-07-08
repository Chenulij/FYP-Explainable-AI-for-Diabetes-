import mysql.connector
from mysql.connector import Error

# ============================================================
# DATABASE CONNECTION SETTINGS
# ============================================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # XAMPP MySQL default has no password
    'database': 'cdss_db'
}

# ============================================================
# GET CONNECTION
# ============================================================
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

# ============================================================
# DOCTOR AUTH
# ============================================================
def verify_doctor(doctor_id, password):
    """Check if doctor ID and password match a record in the doctors table."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM doctors 
            WHERE doctor_id = %s AND password = %s AND is_active = TRUE
        """, (doctor_id, password))
        doctor = cursor.fetchone()
        return doctor
    finally:
        conn.close()

# ============================================================
# PATIENT FUNCTIONS
# ============================================================
def get_patient_by_code(patient_code):
    """Find existing patient by their unique code."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM patients WHERE patient_code = %s", (patient_code,))
        return cursor.fetchone()
    finally:
        conn.close()

def create_patient(patient_code, full_name, date_of_birth, gender, contact_number, doctor_id):
    """Create a new patient record — called first time a patient is assessed."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patients (patient_code, full_name, date_of_birth, gender, contact_number, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (patient_code, full_name, date_of_birth, gender, contact_number, doctor_id))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_all_patients(doctor_id):
    """Get all patients created by this doctor — for dashboard."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, 
                   COUNT(pr.id) as total_predictions,
                   MAX(pr.predicted_at) as last_assessed,
                   (SELECT prediction_label FROM predictions 
                    WHERE patient_id = p.id 
                    ORDER BY predicted_at DESC LIMIT 1) as latest_risk
            FROM patients p
            LEFT JOIN predictions pr ON p.id = pr.patient_id
            WHERE p.created_by = %s
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """, (doctor_id,))
        return cursor.fetchall()
    finally:
        conn.close()

# ============================================================
# PREDICTION FUNCTIONS
# ============================================================
def save_prediction(patient_id, doctor_id, input_data, prediction_label, confidence):
    """Save a prediction result to the database."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions 
            (patient_id, doctor_id, age, gender, hba1c, tg, bmi, 
             total_steps, sedentary_minutes, calories, 
             total_minutes_asleep, sleep_efficiency,
             prediction_label, confidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            patient_id, doctor_id,
            input_data['AGE'], input_data['Gender'],
            input_data['HbA1c'], input_data['TG'], input_data['BMI'],
            input_data['TotalSteps'], input_data['SedentaryMinutes'],
            input_data['Calories'], input_data['TotalMinutesAsleep'],
            input_data['SleepEfficiency'],
            prediction_label, confidence
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def save_recommendations(prediction_id, recommendations):
    """Save the rule-based recommendations linked to a prediction."""
    conn = get_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        for rec in recommendations:
            # rec is a dict with 'category' and 'text' keys
            rec_text = f"[{rec['category']}] {rec['text']}"
            cursor.execute("""
                INSERT INTO recommendations (prediction_id, recommendation_text)
                VALUES (%s, %s)
            """, (prediction_id, rec_text))
        conn.commit()
    finally:
        conn.close()

def get_patient_history(patient_id):
    """Get all past predictions for a patient — for monitoring."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT pr.*, d.full_name as doctor_name
            FROM predictions pr
            JOIN doctors d ON pr.doctor_id = d.id
            WHERE pr.patient_id = %s
            ORDER BY pr.predicted_at DESC
        """, (patient_id,))
        return cursor.fetchall()
    finally:
        conn.close()

def get_prediction_recommendations(prediction_id):
    """Get recommendations for a specific prediction."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM recommendations 
            WHERE prediction_id = %s
        """, (prediction_id,))
        return cursor.fetchall()
    finally:
        conn.close()