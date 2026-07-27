import streamlit as st
from utils.database import (
    get_all_doctors, add_doctor,
    toggle_doctor_status, reset_doctor_password
)
from utils.styles import load_css

# ============================================================
# AUTH GUARD — admin only
# ============================================================
if "admin" not in st.session_state or not st.session_state.admin:
    st.switch_page("app.py")

admin = st.session_state.admin

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Admin Panel", page_icon="🔧", layout="wide")
load_css()

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
    <style>
    .doctor-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2563eb;
    }
    .doctor-card-inactive {
        border-left: 4px solid #94a3b8;
        opacity: 0.7;
    }
    .stat-box {
        background: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
col_title, col_logout = st.columns([6, 1])
with col_title:
    st.title("🔧 Admin Panel")
    st.caption(f"Logged in as **{admin['full_name']}** · Clinic Administrator")
with col_logout:
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.divider()

# ============================================================
# LOAD DOCTORS
# ============================================================
doctors = get_all_doctors()

# ============================================================
# SUMMARY METRICS
# ============================================================
total    = len(doctors)
active   = sum(1 for d in doctors if d['is_active'])
inactive = total - active

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Doctors", total)
with col2:
    st.metric("✅ Active", active)
with col3:
    st.metric("🔴 Inactive", inactive)

st.divider()

# ============================================================
# TABS — View Doctors | Add Doctor
# ============================================================
tab1, tab2 = st.tabs(["👨‍⚕️ Manage Doctors", "➕ Add New Doctor"])

# ── TAB 1: MANAGE DOCTORS ───────────────────────────────────
with tab1:
    st.markdown("### Registered Doctors")

    if not doctors:
        st.info("No doctors registered yet.")
    else:
        for doc in doctors:
            is_active = doc['is_active']
            card_class = "doctor-card" if is_active else "doctor-card doctor-card-inactive"
            status_badge = "🟢 Active" if is_active else "🔴 Inactive"

            col_info, col_actions = st.columns([5, 2])

            with col_info:
                st.markdown(f"""
                    <div class='{card_class}'>
                        <strong>{doc['full_name']}</strong>
                        &nbsp;&nbsp;
                        <span style='color:#64748b; font-size:0.85rem'>
                            ID: {doc['doctor_id']} · {doc['specialization']} · 
                            {doc['email']} · Patients: {doc['total_patients']}
                        </span>
                        &nbsp;&nbsp;{status_badge}
                    </div>
                """, unsafe_allow_html=True)

            with col_actions:
                st.markdown("<br/>", unsafe_allow_html=True)
                col_a, col_b = st.columns(2)

                with col_a:
                    # Toggle active/inactive
                    btn_label = "Deactivate" if is_active else "Activate"
                    if st.button(btn_label, key=f"toggle_{doc['id']}", use_container_width=True):
                        toggle_doctor_status(doc['id'], not is_active)
                        st.success(f"{'Deactivated' if is_active else 'Activated'} {doc['full_name']}")
                        st.rerun()

                with col_b:
                    # Reset password
                    if st.button("Reset PW", key=f"reset_{doc['id']}", use_container_width=True):
                        st.session_state[f"reset_open_{doc['id']}"] = True

            # Password reset form (shows inline when button clicked)
            if st.session_state.get(f"reset_open_{doc['id']}", False):
                with st.form(f"reset_form_{doc['id']}"):
                    new_pw = st.text_input(
                        f"New password for {doc['full_name']}",
                        type="password",
                        key=f"new_pw_{doc['id']}"
                    )
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        save = st.form_submit_button("Save", type="primary", use_container_width=True)
                    with col_cancel:
                        cancel = st.form_submit_button("Cancel", use_container_width=True)

                    if save:
                        if not new_pw or len(new_pw) < 6:
                            st.error("Password must be at least 6 characters.")
                        else:
                            reset_doctor_password(doc['id'], new_pw)
                            st.success(f"Password reset for {doc['full_name']}")
                            st.session_state[f"reset_open_{doc['id']}"] = False
                            st.rerun()
                    if cancel:
                        st.session_state[f"reset_open_{doc['id']}"] = False
                        st.rerun()

# ── TAB 2: ADD NEW DOCTOR ───────────────────────────────────
with tab2:
    st.markdown("### Add New Doctor")
    st.caption("New doctor will be able to log in immediately after being added.")

    with st.form("add_doctor_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_id     = st.text_input("Doctor ID *", placeholder="e.g. DOC003")
            new_name   = st.text_input("Full Name *", placeholder="e.g. Dr. Sarah Khan")
            new_email  = st.text_input("Email *", placeholder="e.g. sarah@clinic.com")
        with col2:
            new_spec   = st.selectbox("Specialization *", [
                "General Practice",
                "Endocrinology",
                "Internal Medicine",
                "Diabetology",
                "Cardiology",
                "Other"
            ])
            new_pass   = st.text_input("Password *", type="password", placeholder="Min 6 characters")
            new_pass2  = st.text_input("Confirm Password *", type="password", placeholder="Repeat password")

        add_submit = st.form_submit_button("➕ Add Doctor", type="primary", use_container_width=True)

    if add_submit:
        errors = []
        if not new_id:    errors.append("Doctor ID is required.")
        if not new_name:  errors.append("Full Name is required.")
        if not new_email: errors.append("Email is required.")
        if not new_pass:  errors.append("Password is required.")
        if new_pass != new_pass2: errors.append("Passwords do not match.")
        if len(new_pass) < 6: errors.append("Password must be at least 6 characters.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            success, msg = add_doctor(
                new_id.strip().upper(),
                new_name.strip(),
                new_email.strip(),
                new_pass.strip(),
                new_spec
            )
            if success:
                st.success(f"✅ {new_name} added successfully! They can now log in with ID: {new_id.strip().upper()}")
                st.rerun()
            else:
                if "Duplicate" in msg or "1062" in msg:
                    st.error("That Doctor ID or email already exists. Please use a different one.")
                else:
                    st.error(f"Error adding doctor: {msg}")