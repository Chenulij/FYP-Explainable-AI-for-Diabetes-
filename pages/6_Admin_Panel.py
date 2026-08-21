import streamlit as st
from utils.database import (
    get_all_doctors, add_doctor,
    toggle_doctor_status, reset_doctor_password,
    get_all_admin_patients, toggle_patient_status
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
st.set_page_config(page_title="Admin Panel", page_icon="🩺", layout="wide")
load_css()

# ============================================================
# DESIGN SYSTEM — same tokens as the doctor-facing pages
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

    :root {
        --navy-900: #0B2C4A;
        --teal-500: #0F8B8D;
        --ink-900:  #101828;
        --ink-600:  #475467;
        --ink-400:  #98A2B3;
        --line:     #E4E9F0;
        --bg:       #F4F7FB;
        --danger:   #D92D20;
        --success:  #15803D;
        --success-bg:#EFFAF3;
        --radius:   12px;
    }

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', -apple-system, sans-serif; }

    .page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink-900); margin: 0; letter-spacing: -0.01em; }
    .page-sub   { color: var(--ink-600); font-size: 0.88rem; margin-top: 0.15rem; }
    .section-title { font-size: 1.02rem; font-weight: 700; color: var(--ink-900); margin: 0 0 0.4rem 0; }

    /* ---------- doctor cards ---------- */
    .doctor-card {
        background: #fff;
        border-radius: 10px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.55rem;
        border: 1px solid var(--line);
        border-left: 4px solid var(--card-accent, var(--navy-900));
    }
    .doctor-card.inactive { opacity: 0.65; }
    .doctor-name { font-weight: 700; color: var(--ink-900); }
    .doctor-meta { color: var(--ink-600); font-size: 0.84rem; margin-top: 0.15rem; }

    .status-pill {
        display: inline-block;
        padding: 0.16rem 0.6rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        margin-left: 0.5rem;
    }
    .status-active   { background: var(--success-bg); color: var(--success); }
    .status-inactive { background: #F1F5F9; color: var(--ink-600); }

    /* ---------- tabs -> segmented control ---------- */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0; background: #EAEFF5; padding: 4px; border-radius: 10px;
        width: fit-content; margin-bottom: 1.2rem;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 8px; padding: 0.5rem 1.2rem; font-weight: 600;
        font-size: 0.86rem; color: var(--ink-600);
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: #fff; color: var(--navy-900); box-shadow: 0 1px 3px rgba(16,24,40,0.12);
    }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"],
    [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }

    /* ---------- inputs / buttons ---------- */
    [data-testid="stTextInput"] input {
        border: 1.5px solid var(--line); border-radius: 9px;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: var(--teal-500); box-shadow: 0 0 0 3px rgba(15,139,141,0.15);
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border-radius: 9px; border: 1.5px solid var(--line);
    }
    [data-testid="stButton"] button[kind="primary"],
    [data-testid="stFormSubmitButton"] button[kind="primary"] {
        background: var(--navy-900); border: none; border-radius: 9px; font-weight: 600;
    }
    [data-testid="stButton"] button[kind="primary"]:hover,
    [data-testid="stFormSubmitButton"] button[kind="primary"]:hover { background: var(--teal-500); }
    [data-testid="stButton"] button[kind="secondary"],
    [data-testid="stFormSubmitButton"] button[kind="secondary"] {
        border: 1.5px solid var(--line); border-radius: 9px; color: var(--navy-900);
        font-weight: 600; background: #fff;
    }
    [data-testid="stButton"] button[kind="secondary"]:hover,
    [data-testid="stFormSubmitButton"] button[kind="secondary"]:hover {
        border-color: var(--teal-500); color: var(--teal-500);
    }
    [data-testid="stAlert"] { border-radius: 9px; font-size: 0.88rem; }
    [data-testid="stMetric"] {
        background: #fff; border-radius: 10px; border: 1px solid var(--line); padding: 0.9rem 1rem;
    }

    /* native "Press Enter to submit form" hint overflows the input
       box in tight columns — hide it rather than let it spill out */
    [data-testid="InputInstructions"],
    [data-testid="stInputInstructions"],
    [data-testid="stWidgetInstructions"],
    [data-testid="stTextInputInstructions"],
    [data-testid="stTextInput"] [class*="Instructions"],
    [data-testid="stTextInput"] small {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# TOP NAV BAR — admin-specific, since render_sidebar() is built
# for the doctor session (checks st.session_state.doctor and
# links to doctor-only pages). Reuses the same .st-key-topnav
# classes styles.py already defines, no nav links needed since
# Admin Panel is the only admin page.
# ============================================================
with st.container(key="topnav"):
    c_logo, c_spacer, c_admin, c_logout = st.columns([1.6, 5, 2.4, 1])

    with c_logo:
        st.markdown('<div class="topnav-brand">CDSS</div>', unsafe_allow_html=True)

    with c_admin:
        initials = "".join(p[0] for p in admin["full_name"].split()[:2]).upper()
        st.markdown(f"""
            <div class="topnav-profile">
                <div class="topnav-doctor">
                    <b>{admin['full_name']}</b><br/>
                    <span class="topnav-doctor-sub">Clinic Administrator</span>
                </div>
                <div class="topnav-avatar">{initials}</div>
            </div>
        """, unsafe_allow_html=True)

    with c_logout:
        if st.button("Logout", key="admin_logout", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.switch_page("app.py")

with st.container(key="page-content"):

    # ============================================================
    # PAGE TITLE
    # (Admin identity + logout now live in the top bar above —
    # don't add another logout control here.)
    # ============================================================
    st.markdown('<div class="page-title">Admin Panel</div>', unsafe_allow_html=True)
    st.write("")

    # ============================================================
    # LOAD ADMIN DATA
    # ============================================================
    doctors = get_all_doctors()
    patients = get_all_admin_patients()

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
        st.metric("Active", active)
    with col3:
        st.metric("Inactive", inactive)

    st.write("")

    # ============================================================
    # TABS — Doctors | Patients | Add Doctor
    # ============================================================
    tab1, tab2, tab3 = st.tabs([
        "Manage Doctors",
        "Manage Patients",
        "Add New Doctor"
    ])

    # ── TAB 1: MANAGE DOCTORS ───────────────────────────────────
    with tab1:
        st.markdown('<div class="section-title">Registered Doctors</div>', unsafe_allow_html=True)

        if not doctors:
            st.info("No doctors registered yet.")
        else:
            for doc in doctors:
                is_active = doc['is_active']
                card_class = "doctor-card" if is_active else "doctor-card inactive"
                status_html = (
                    '<span class="status-pill status-active">Active</span>' if is_active
                    else '<span class="status-pill status-inactive">Inactive</span>'
                )
                card_accent = "var(--success)" if is_active else "var(--ink-400)"

                col_info, col_actions = st.columns([5, 2])

                with col_info:
                    st.markdown(f"""
                        <div class="{card_class}" style="--card-accent:{card_accent}">
                            <span class="doctor-name">{doc['full_name']}</span>{status_html}
                            <div class="doctor-meta">
                                ID: {doc['doctor_id']} · {doc['specialization']} ·
                                {doc['email']} · Patients: {doc['total_patients']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                with col_actions:
                    st.write("")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        btn_label = "Deactivate" if is_active else "Activate"
                        if st.button(btn_label, key=f"toggle_{doc['id']}", use_container_width=True, type="secondary"):
                            toggle_doctor_status(doc['id'], not is_active)
                            st.success(f"{'Deactivated' if is_active else 'Activated'} {doc['full_name']}")
                            st.rerun()
                    with col_b:
                        if st.button("Reset PW", key=f"reset_{doc['id']}", use_container_width=True, type="secondary"):
                            st.session_state[f"reset_open_{doc['id']}"] = True

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

    # ── TAB 2: MANAGE PATIENTS ──────────────────────────────────
    with tab2:
        st.markdown('<div class="section-title">Registered Patients</div>', unsafe_allow_html=True)
        st.caption("Archived patients are hidden from doctor dashboards, but their assessment history is retained.")

        patient_total = len(patients)
        patient_active = sum(1 for p in patients if p.get("is_active"))
        patient_archived = patient_total - patient_active

        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("Total Patients", patient_total)
        with p2:
            st.metric("Active Patients", patient_active)
        with p3:
            st.metric("Archived Patients", patient_archived)

        st.write("")
        filter_col1, filter_col2 = st.columns([3, 1])
        with filter_col1:
            patient_search = st.text_input(
                "Search patients",
                placeholder="Search by patient code, name or doctor",
                key="admin_patient_search"
            ).strip().lower()
        with filter_col2:
            patient_status = st.selectbox(
                "Status",
                ["All", "Active", "Archived"],
                key="admin_patient_status"
            )

        filtered_patients = []
        for patient in patients:
            is_patient_active = bool(patient.get("is_active"))
            searchable_text = " ".join([
                str(patient.get("patient_code") or ""),
                str(patient.get("full_name") or ""),
                str(patient.get("doctor_name") or ""),
                str(patient.get("doctor_code") or "")
            ]).lower()

            matches_search = not patient_search or patient_search in searchable_text
            matches_status = (
                patient_status == "All"
                or (patient_status == "Active" and is_patient_active)
                or (patient_status == "Archived" and not is_patient_active)
            )

            if matches_search and matches_status:
                filtered_patients.append(patient)

        if not filtered_patients:
            st.info("No patients match the selected search and status filters.")
        else:
            for patient in filtered_patients:
                is_patient_active = bool(patient.get("is_active"))
                card_class = "doctor-card" if is_patient_active else "doctor-card inactive"
                status_html = (
                    '<span class="status-pill status-active">Active</span>'
                    if is_patient_active
                    else '<span class="status-pill status-inactive">Archived</span>'
                )
                card_accent = "var(--success)" if is_patient_active else "var(--ink-400)"
                latest_risk = patient.get("latest_risk") or "Not assessed"
                doctor_name = patient.get("doctor_name") or "Unassigned"
                doctor_code = patient.get("doctor_code") or "N/A"

                col_info, col_action = st.columns([6, 1.4])
                with col_info:
                    st.markdown(f"""
                        <div class="{card_class}" style="--card-accent:{card_accent}">
                            <span class="doctor-name">{patient['full_name']}</span>{status_html}
                            <div class="doctor-meta">
                                Patient: {patient['patient_code']} · Doctor: {doctor_name} ({doctor_code}) ·
                                Assessments: {patient['total_predictions']} · Latest risk: {latest_risk}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                with col_action:
                    st.write("")
                    action_label = "Archive" if is_patient_active else "Restore"
                    if st.button(
                        action_label,
                        key=f"patient_toggle_{patient['id']}",
                        use_container_width=True,
                        type="secondary"
                    ):
                        updated = toggle_patient_status(
                            patient['id'],
                            not is_patient_active
                        )
                        if updated:
                            st.success(
                                f"{patient['full_name']} was "
                                f"{'archived' if is_patient_active else 'restored'}."
                            )
                            st.rerun()
                        else:
                            st.error("The patient status could not be updated.")

    # ── TAB 3: ADD NEW DOCTOR ───────────────────────────────────
    with tab3:
        with st.container(border=True):
            st.markdown('<div class="section-title">Add New Doctor</div>', unsafe_allow_html=True)
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

                add_submit = st.form_submit_button("Add Doctor", type="primary", use_container_width=True)

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
                        st.success(f"{new_name} added successfully! They can now log in with ID: {new_id.strip().upper()}")
                        st.rerun()
                    else:
                        if "Duplicate" in msg or "1062" in msg:
                            st.error("That Doctor ID or email already exists. Please use a different one.")
                        else:
                            st.error(f"Error adding doctor: {msg}")