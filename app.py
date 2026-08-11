import streamlit as st
from utils.database import verify_doctor, verify_admin

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="CDSS — Sign in",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# ALREADY LOGGED IN — REDIRECT
# ============================================================
if "doctor" in st.session_state and st.session_state.doctor:
    st.switch_page("pages/1_Dashboard.py")

if "admin" in st.session_state and st.session_state.admin:
    st.switch_page("pages/6_Admin_Panel.py")

# ============================================================
# DESIGN SYSTEM — CSS
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

    :root {
        --navy-950: #071B2E;
        --navy-900: #0B2C4A;
        --navy-800: #0E3B63;
        --teal-500: #0F8B8D;
        --teal-400: #14A6A6;
        --ink-900:  #101828;
        --ink-600:  #475467;
        --ink-400:  #98A2B3;
        --line:     #E4E9F0;
        --bg:       #F4F7FB;
        --danger:   #D92D20;
        --radius:   14px;
    }

    html, body, [class*="css"]  {
        font-family: 'IBM Plex Sans', -apple-system, sans-serif;
    }

    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stSidebarNav"], [data-testid="stSidebar"] { display: none; }

    /* st.markdown(css, unsafe_allow_html=True) still occupies a real
       flex slot (and the 1rem gap around it) in Streamlit's vertical
       block layout, even though it renders nothing visible — remove
       it from the layout entirely instead of leaving a gap-sized hole */
    div:has(> style) { display: none; }

    [data-testid="stAppViewContainer"] { background: var(--bg); }
    [data-testid="stAppViewContainer"] > .main {
        padding: 0 !important;
    }
    [data-testid="stAppViewContainer"] > .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ---------- two-panel layout via real st.columns ---------- */
    [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        align-items: stretch;
    }
    [data-testid="column"], [data-testid="stColumn"] {
        padding: 0 !important;
    }

    /* left / brand panel — first column */
    [data-testid="column"]:nth-of-type(1),
    [data-testid="stColumn"]:nth-of-type(1) {
        background:
            radial-gradient(120% 140% at 15% -10%, rgba(20,166,166,0.35) 0%, rgba(20,166,166,0) 45%),
            linear-gradient(160deg, var(--navy-950) 0%, var(--navy-900) 55%, var(--navy-800) 100%);
        color: #fff;
        min-height: 100vh;
        padding: 4rem 3.2rem !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* right / form panel — second column */
    [data-testid="column"]:nth-of-type(2),
    [data-testid="stColumn"]:nth-of-type(2) {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 3rem 4rem !important;
        animation: rise 0.5s ease-out both;
    }
    @keyframes rise {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .brand-mark {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        font-size: 1.02rem;
    }
    .brand-mark .dot {
        width: 9px; height: 9px; border-radius: 50%;
        background: var(--teal-400);
        box-shadow: 0 0 0 4px rgba(20,166,166,0.18);
    }

    .brand-copy h1 {
        font-size: 2.15rem;
        line-height: 1.22;
        font-weight: 700;
        margin: 1.6rem 0 0.9rem 0;
        letter-spacing: -0.01em;
    }
    .brand-copy p {
        color: rgba(255,255,255,0.68);
        font-size: 0.98rem;
        line-height: 1.6;
        max-width: 30ch;
        margin: 0;
    }

    /* signature element: ECG trace */
    .trace-wrap { margin: 2.4rem 0 2rem 0; }
    .trace-wrap svg { width: 100%; height: 64px; display: block; }
    .trace-line {
        fill: none;
        stroke: var(--teal-400);
        stroke-width: 2;
        stroke-linecap: round;
        stroke-linejoin: round;
        stroke-dasharray: 340;
        stroke-dashoffset: 340;
        animation: draw 2.2s ease-out forwards 0.3s;
        filter: drop-shadow(0 0 6px rgba(20,166,166,0.55));
    }
    @keyframes draw { to { stroke-dashoffset: 0; } }

    .brand-stats {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.4rem;
        border-top: 1px solid rgba(255,255,255,0.14);
        padding-top: 1.6rem;
    }
    .brand-stats .stat-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(255,255,255,0.5);
        margin-bottom: 0.3rem;
    }
    .brand-stats .stat-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.92rem;
        color: #fff;
    }

    .brand-footer {
        font-size: 0.74rem;
        color: rgba(255,255,255,0.4);
        letter-spacing: 0.01em;
    }

    /* constrain + center the form content inside the right column
       (targets Streamlit's own generated wrapper, not a manual div) */
    [data-testid="column"]:nth-of-type(2) [data-testid="stVerticalBlock"],
    [data-testid="stColumn"]:nth-of-type(2) [data-testid="stVerticalBlock"] {
        max-width: 420px;
        width: 100%;
        margin: 0 auto;
    }

    .form-heading h2 {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--ink-900);
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.01em;
    }
    .form-heading p {
        color: var(--ink-600);
        font-size: 0.9rem;
        margin: 0 0 1.8rem 0;
    }

    /* tabs -> segmented control */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0;
        background: #EAEFF5;
        padding: 4px;
        border-radius: 10px;
        margin-bottom: 1.6rem;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        flex: 1;
        justify-content: center;
        border-radius: 8px;
        padding: 0.5rem 0;
        font-weight: 600;
        font-size: 0.86rem;
        color: var(--ink-600);
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: #fff;
        color: var(--navy-900);
        box-shadow: 0 1px 3px rgba(16,24,40,0.12);
    }
    [data-testid="stTabs"] [data-baseweb="tab-highlight"],
    [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }

    /* inputs */
    [data-testid="stTextInput"] label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--ink-900);
        margin-bottom: 0.2rem;
    }
    [data-testid="stTextInput"] input {
        border: 1.5px solid var(--line);
        border-radius: 9px;
        padding: 0.62rem 0.8rem;
        font-size: 0.92rem;
        background: #fff;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: var(--teal-500);
        box-shadow: 0 0 0 3px rgba(15,139,141,0.15);
    }

    /* submit button */
    [data-testid="stFormSubmitButton"] button {
        background: var(--navy-900);
        color: #fff;
        border: none;
        border-radius: 9px;
        padding: 0.68rem 0;
        font-weight: 600;
        font-size: 0.92rem;
        margin-top: 0.4rem;
        transition: background 0.15s ease, transform 0.1s ease;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background: var(--teal-500);
    }
    [data-testid="stFormSubmitButton"] button:active { transform: scale(0.99); }

    /* alerts */
    [data-testid="stAlert"] { border-radius: 9px; font-size: 0.86rem; }

    .form-footnote {
        text-align: center;
        margin-top: 1.6rem;
        font-size: 0.74rem;
        color: var(--ink-400);
        line-height: 1.6;
    }

    /* native "Press Enter to submit form" hint overflows past the
       input border on password fields (value + eye icon leave no
       room for it) — hide rather than let it spill outside the box */
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
# TWO-PANEL LAYOUT — real st.columns, not a manual div hack.
# Each column is a first-class Streamlit container: widgets
# placed inside `with col:` render as actual children of that
# column in the DOM, so the CSS above can reliably style them.
# ============================================================
col_left, col_right = st.columns([1, 1.3], gap="small")

with col_left:
    st.markdown("""
        <div class="brand-mark"><span class="dot"></span>CDSS</div>
        <div class="brand-copy">
          <h1>Clinical Decision<br/>Support System</h1>
          <p>IoT-enabled diabetes risk prediction for clinical teams — continuous vitals, real-time risk scoring, at the point of care.</p>
          <div class="trace-wrap">
            <svg viewBox="0 0 300 64" preserveAspectRatio="none">
              <path class="trace-line" d="M0,32 L60,32 L75,32 L85,10 L95,54 L105,20 L115,32 L140,32 L155,32 L165,14 L175,50 L185,32 L300,32" />
            </svg>
          </div>
          <div class="brand-stats">
            <div>
              <div class="stat-label">Monitoring</div>
              <div class="stat-value">Continuous IoT feed</div>
            </div>
            <div>
              <div class="stat-label">Access</div>
              <div class="stat-value">Clinician-restricted</div>
            </div>
          </div>
        </div>
        <div class="brand-footer">FYP Prototype · CB013123 · APIIT / Staffordshire University</div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
        <div class="form-heading">
            <h2>Sign in</h2>
            <p>Enter your credentials to access the dashboard.</p>
        </div>
    """, unsafe_allow_html=True)

    tab_doctor, tab_admin = st.tabs(["Doctor", "Administrator"])

    # ── DOCTOR LOGIN ─────────────────────────────────────────
    with tab_doctor:
        with st.form("doctor_login_form"):
            doctor_id = st.text_input("Doctor ID", placeholder="e.g. DOC001")
            password  = st.text_input("Password", type="password", placeholder="Enter your password")
            submit    = st.form_submit_button("Sign in", use_container_width=True)

        if submit:
            if not doctor_id or not password:
                st.error("Please enter both Doctor ID and password.")
            else:
                with st.spinner("Verifying credentials..."):
                    doctor = verify_doctor(doctor_id.strip(), password.strip())
                if doctor:
                    st.session_state.doctor = doctor
                    st.success(f"Welcome, {doctor['full_name']}.")
                    st.switch_page("pages/1_Dashboard.py")
                else:
                    st.error("Invalid Doctor ID or password. Please try again.")

    # ── ADMIN LOGIN ──────────────────────────────────────────
    with tab_admin:
        with st.form("admin_login_form"):
            admin_user = st.text_input("Admin username", placeholder="e.g. admin")
            admin_pass = st.text_input("Password", type="password", placeholder="Enter admin password", key="admin_pw")
            admin_submit = st.form_submit_button("Sign in", use_container_width=True)

        if admin_submit:
            if not admin_user or not admin_pass:
                st.error("Please enter both username and password.")
            else:
                with st.spinner("Verifying admin credentials..."):
                    admin = verify_admin(admin_user.strip(), admin_pass.strip())
                if admin:
                    st.session_state.admin = admin
                    st.success(f"Welcome, {admin['full_name']}.")
                    st.switch_page("pages/6_Admin_Panel.py")
                else:
                    st.error("Invalid admin credentials. Please try again.")

    st.markdown("""
        <div class="form-footnote">Access restricted to verified clinic staff only.</div>
    """, unsafe_allow_html=True)