import mysql.connector
from mysql.connector import Error
import streamlit as st
import certifi

# ============================================================
# DATABASE CONNECTION SETTINGS
# ============================================================
DB_CONFIG = {
    "host": st.secrets["database"]["host"],
    "port": int(st.secrets["database"]["port"]),
    "user": st.secrets["database"]["user"],
    "password": st.secrets["database"]["password"],
    "database": st.secrets["database"]["database"],
    "ssl_ca": certifi.where(),
    "ssl_verify_cert": True,
    "ssl_verify_identity": True,
    "connection_timeout": 20
}

# ============================================================
# GET CONNECTION
# ============================================================
def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def get_next_id(cursor, table_name):
    """Return the next ID for tables imported without AUTO_INCREMENT."""
    allowed_tables = {
        "doctors",
        "patients",
        "predictions",
        "recommendations"
    }

    if table_name not in allowed_tables:
        raise ValueError("Invalid table name")

    cursor.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {table_name}")
    return cursor.fetchone()[0]

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
        cursor.execute("""
            SELECT * FROM patients
            WHERE patient_code = %s
        """, (patient_code,))
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
        new_id = get_next_id(cursor, "patients")
        cursor.execute("""
            INSERT INTO patients
            (id, patient_code, full_name, date_of_birth, gender, contact_number, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            new_id, patient_code, full_name, date_of_birth,
            gender, contact_number, doctor_id
        ))
        conn.commit()
        return new_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_all_patients(doctor_id):
    """Get all patients created by this doctor for the dashboard."""
    conn = get_connection()

    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                p.*,
                COALESCE(ps.total_predictions, 0) AS total_predictions,
                ps.last_assessed,
                (
                    SELECT pr2.prediction_label
                    FROM predictions pr2
                    WHERE pr2.patient_id = p.id
                    ORDER BY pr2.predicted_at DESC, pr2.id DESC
                    LIMIT 1
                ) AS latest_risk
            FROM patients p
            LEFT JOIN (
                SELECT
                    patient_id,
                    COUNT(*) AS total_predictions,
                    MAX(predicted_at) AS last_assessed
                FROM predictions
                GROUP BY patient_id
            ) ps ON ps.patient_id = p.id
            WHERE p.created_by = %s
              AND p.is_active = TRUE
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
        new_id = get_next_id(cursor, "predictions")
        cursor.execute("""
            INSERT INTO predictions 
            (id, patient_id, doctor_id, age, gender, hba1c, tg, bmi, 
             total_steps, sedentary_minutes, calories, 
             total_minutes_asleep, sleep_efficiency,
             prediction_label, confidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            new_id, patient_id, doctor_id,
            input_data['AGE'], input_data['Gender'],
            input_data['HbA1c'], input_data['TG'], input_data['BMI'],
            input_data['TotalSteps'], input_data['SedentaryMinutes'],
            input_data['Calories'], input_data['TotalMinutesAsleep'],
            input_data['SleepEfficiency'],
            prediction_label, confidence
        ))
        conn.commit()
        return new_id
    except Exception:
        conn.rollback()
        raise
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
            new_id = get_next_id(cursor, "recommendations")
            rec_text = f"[{rec['category']}] {rec['text']}"
            cursor.execute("""
                INSERT INTO recommendations (id, prediction_id, recommendation_text)
                VALUES (%s, %s, %s)
            """, (new_id, prediction_id, rec_text))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
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

def get_last_prediction(patient_id):
    """Get the most recent prediction values for a patient — used to pre-fill assessment form."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM predictions 
            WHERE patient_id = %s 
            ORDER BY predicted_at DESC 
            LIMIT 1
        """, (patient_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def get_next_patient_code(doctor_db_id, doctor_code):
    """Auto-generate next patient code for this doctor e.g. DOC001-P001"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM patients 
            WHERE created_by = %s
        """, (doctor_db_id,))
        count = cursor.fetchone()[0]
        next_num = count + 1
        return f"{str(doctor_code).upper()}-P{str(next_num).zfill(3)}"
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

def get_previous_prediction(patient_id):
    """Get the second most recent prediction for a patient —
    used AFTER saving the new prediction to compare with 
    the previous visit."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM predictions
            WHERE patient_id = %s
            ORDER BY predicted_at DESC
            LIMIT 1 OFFSET 1
        """, (patient_id,))
        return cursor.fetchone()
    finally:
        conn.close()

# ============================================================
# ADMIN AUTH & MANAGEMENT
# ============================================================
def verify_admin(username, password):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM admins 
            WHERE username = %s AND password = %s
        """, (username, password))
        return cursor.fetchone()
    finally:
        conn.close()

def get_all_doctors():
    conn = get_connection()

    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                d.*,
                (
                    SELECT COUNT(*)
                    FROM patients p
                    WHERE p.created_by = d.id
                ) AS total_patients
            FROM doctors d
            ORDER BY d.created_at DESC
        """)

        return cursor.fetchall()

    finally:
        conn.close()

def get_all_admin_patients():
    """Return active and archived patients for administrator management."""
    conn = get_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                p.*,
                d.full_name AS doctor_name,
                d.doctor_id AS doctor_code,
                COALESCE(ps.total_predictions, 0) AS total_predictions,
                ps.last_assessed,
                (
                    SELECT pr2.prediction_label
                    FROM predictions pr2
                    WHERE pr2.patient_id = p.id
                    ORDER BY pr2.predicted_at DESC, pr2.id DESC
                    LIMIT 1
                ) AS latest_risk
            FROM patients p
            LEFT JOIN doctors d ON d.id = p.created_by
            LEFT JOIN (
                SELECT
                    patient_id,
                    COUNT(*) AS total_predictions,
                    MAX(predicted_at) AS last_assessed
                FROM predictions
                GROUP BY patient_id
            ) ps ON ps.patient_id = p.id
            ORDER BY p.created_at DESC, p.id DESC
        """)
        return cursor.fetchall()
    finally:
        conn.close()

def toggle_patient_status(patient_id, is_active):
    """Archive or restore a patient without deleting clinical history."""
    conn = get_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE patients
            SET is_active = %s
            WHERE id = %s
        """, (is_active, patient_id))
        conn.commit()
        return cursor.rowcount == 1
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
        
def add_doctor(doctor_id, full_name, email, password, specialization):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    try:
        cursor = conn.cursor()
        new_id = get_next_id(cursor, "doctors")
        cursor.execute("""
            INSERT INTO doctors
            (id, doctor_id, full_name, email, password, specialization)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            new_id, doctor_id, full_name,
            email, password, specialization
        ))
        conn.commit()
        return True, "Doctor added successfully"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def toggle_doctor_status(doctor_id, is_active):
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE doctors SET is_active = %s WHERE id = %s
        """, (is_active, doctor_id))
        conn.commit()
        return True
    finally:
        conn.close()

def reset_doctor_password(doctor_id, new_password):
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE doctors SET password = %s WHERE id = %s
        """, (new_password, doctor_id))
        conn.commit()
        return True
    finally:
        conn.close()