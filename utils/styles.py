import streamlit as st


# ============================================================
# LOAD GLOBAL CSS
# ============================================================

def load_css():
    """
    Shared styling for all authenticated CDSS pages.

    Controls:
    - Streamlit header/sidebar removal
    - page background
    - page side spacing
    - full-width top navbar
    - navbar buttons/profile
    - common buttons, inputs, tabs and metrics
    """

    # st.html is used for a CSS-only block so the stylesheet itself
    # does not create a visible Streamlit element above the navbar.
    st.html(
        """
        <style>

        /* ============================================================
           GLOBAL VARIABLES
           ============================================================ */

        :root {
            --bg: #F4F7FB;

            --navy-950: #071B2E;
            --navy-900: #0B2C4A;
            --navy-800: #0E3B63;

            --teal-500: #0F8B8D;
            --teal-400: #14A6A6;

            --ink-900: #101828;
            --ink-700: #344054;
            --ink-600: #475467;
            --ink-400: #98A2B3;

            --line: #E4E9F0;

            /*
             * Normal page content distance from the
             * left and right browser edges.
             */
            --page-gap: 2.5rem;
        }


        /* ============================================================
           FONT
           ============================================================ */

        @import url(
            'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap'
        );

        html,
        body {
            margin: 0 !important;
            padding: 0 !important;

            font-family:
                'IBM Plex Sans',
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }


        /* ============================================================
           REMOVE STREAMLIT DEFAULT UI
           ============================================================ */

        header,
        [data-testid="stHeader"] {
            display: none !important;

            height: 0 !important;
            min-height: 0 !important;

            margin: 0 !important;
            padding: 0 !important;
        }

        [data-testid="stDecoration"] {
            display: none !important;
        }

        #MainMenu {
            display: none !important;
        }

        footer {
            display: none !important;
        }

        [data-testid="stToolbar"] {
            display: none !important;
        }


        /* ============================================================
           REMOVE STREAMLIT SIDEBAR
           ============================================================ */

        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }


        /* ============================================================
           APP ROOT
           ============================================================ */

        [data-testid="stAppViewContainer"] {
            background: var(--bg) !important;

            margin: 0 !important;
            padding: 0 !important;
        }

        [data-testid="stAppViewContainer"] > .main {
            margin: 0 !important;
            padding: 0 !important;
        }


        /* ============================================================
           MAIN CONTENT CONTAINER
           ============================================================ */

        /*
         * Current Streamlit versions.
         *
         * Normal page content keeps a 2.5rem side gap.
         * Top padding is zero so the navbar can begin at the top.
         */

        [data-testid="stMainBlockContainer"] {
            width: 100% !important;
            max-width: 100% !important;

            margin: 0 !important;

            padding-top: 0 !important;
            padding-bottom: 3rem !important;

            padding-left: var(--page-gap) !important;
            padding-right: var(--page-gap) !important;

            box-sizing: border-box !important;
        }


        /*
         * Compatibility with Streamlit versions where
         * the main container still uses .block-container.
         */

        [data-testid="stAppViewContainer"]
        > .main
        .block-container {
            width: 100% !important;
            max-width: 100% !important;

            margin: 0 !important;

            padding-top: 0 !important;
            padding-bottom: 3rem !important;

            padding-left: var(--page-gap) !important;
            padding-right: var(--page-gap) !important;

            box-sizing: border-box !important;
        }


        /* ============================================================
           REMOVE TOP-OF-PAGE STREAMLIT SPACING
           ============================================================ */

        [data-testid="stMainBlockContainer"]
        > [data-testid="stVerticalBlock"] {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        .block-container
        > [data-testid="stVerticalBlock"] {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        /*
         * The first element on authenticated pages is the navbar.
         * Make sure Streamlit doesn't place a top margin before it.
         */

        [data-testid="stMainBlockContainer"]
        > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }


        /* ============================================================
           TOP NAVIGATION BAR
           ============================================================ */

        .st-key-topnav {
            /*
             * Full viewport width.
             *
             * The parent container has --page-gap padding.
             * This full-bleed technique ignores that padding only
             * for the navbar.
             */
            width: 100vw !important;
            max-width: 100vw !important;

            position: relative !important;
            left: 50% !important;

            margin-left: -50vw !important;
            margin-right: -50vw !important;

            /*
             * No blank area above navbar.
             */
            margin-top: 0 !important;

            /*
             * Normal gap between navbar and actual page content.
             */
            margin-bottom: 2rem !important;

            /*
             * Straight navbar corners.
             */
            border-radius: 0 !important;

            /*
             * Internal content still lines up visually with
             * the rest of the page.
             */
            padding:
                0.75rem
                var(--page-gap) !important;

            background: var(--navy-900) !important;

            box-sizing: border-box !important;

            z-index: 100 !important;
        }


        /* ============================================================
           NAVBAR INTERNAL LAYOUT
           ============================================================ */

        .st-key-topnav
        [data-testid="stHorizontalBlock"] {
            align-items: center !important;
        }

        .st-key-topnav
        [data-testid="column"],

        .st-key-topnav
        [data-testid="stColumn"] {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }


        /* ============================================================
           NAVBAR BRAND
           ============================================================ */

        .topnav-brand {
            color: #FFFFFF !important;

            font-weight: 700;

            font-size: 1.02rem;

            letter-spacing: 0.02em;

            line-height: 1.2;
        }


        /* ============================================================
           DOCTOR / ADMIN INFORMATION
           ============================================================ */

        .topnav-doctor {
            color:
                rgba(255, 255, 255, 0.90) !important;

            font-size: 0.84rem;

            text-align: right;

            line-height: 1.3;
        }

        .topnav-doctor-sub {
            color:
                rgba(255, 255, 255, 0.50) !important;
        }


        /* ============================================================
           ADMIN PROFILE
           ============================================================ */

        .topnav-profile {
            display: flex;

            align-items: center;

            justify-content: flex-end;

            gap: 0.8rem;
        }


        /* ============================================================
           ADMIN AVATAR
           ============================================================ */

        .topnav-avatar {
            width: 44px;
            height: 44px;

            border-radius: 50%;

            display: flex;

            align-items: center;
            justify-content: center;

            flex-shrink: 0;

            background:
                rgba(255, 255, 255, 0.10);

            border:
                1px solid rgba(255, 255, 255, 0.22);

            color: #FFFFFF;

            font-size: 0.78rem;

            font-weight: 600;

            box-sizing: border-box;
        }


        /* ============================================================
           NAVBAR BUTTONS
           ============================================================ */

        .st-key-topnav
        [data-testid="stButton"] {
            margin: 0 !important;
        }

        .st-key-topnav
        [data-testid="stButton"] button {
            min-height: 40px;

            border-radius: 8px !important;

            font-weight: 600;

            font-size: 0.85rem;

            transition:
                background 0.15s ease,
                border-color 0.15s ease,
                color 0.15s ease;
        }


        /* ============================================================
           ACTIVE NAVIGATION BUTTON
           ============================================================ */

        .st-key-topnav
        [data-testid="stButton"]
        button[kind="primary"] {
            background:
                var(--teal-500) !important;

            border:
                1px solid var(--teal-500) !important;

            color: #FFFFFF !important;
        }

        .st-key-topnav
        [data-testid="stButton"]
        button[kind="primary"]:hover {
            background:
                var(--teal-400) !important;

            border-color:
                var(--teal-400) !important;
        }


        /* ============================================================
           NAV / LOGOUT SECONDARY BUTTON
           ============================================================ */

        .st-key-topnav
        [data-testid="stButton"]
        button[kind="secondary"] {
            background:
                transparent !important;

            border:
                1px solid rgba(255, 255, 255, 0.28)
                !important;

            color:
                rgba(255, 255, 255, 0.92) !important;
        }

        .st-key-topnav
        [data-testid="stButton"]
        button[kind="secondary"]:hover {
            background:
                rgba(255, 255, 255, 0.08) !important;

            border-color:
                rgba(255, 255, 255, 0.50) !important;

            color: #FFFFFF !important;
        }


        /* ============================================================
           COMMON PAGE TYPOGRAPHY
           ============================================================ */

        .page-title {
            font-size: 1.5rem;

            font-weight: 700;

            color: var(--ink-900);

            margin: 0;

            letter-spacing: -0.01em;
        }

        .page-sub {
            color: var(--ink-600);

            font-size: 0.88rem;

            margin-top: 0.15rem;
        }

        .section-title {
            font-size: 1.02rem;

            font-weight: 700;

            color: var(--ink-900);

            margin: 0 0 0.4rem 0;
        }


        /* ============================================================
           COMMON PRIMARY BUTTONS
           ============================================================ */

        [data-testid="stButton"]
        button[kind="primary"],

        [data-testid="stFormSubmitButton"]
        button[kind="primary"] {
            background:
                var(--navy-900) !important;

            border: none !important;

            border-radius: 9px !important;

            font-weight: 600;
        }

        [data-testid="stButton"]
        button[kind="primary"]:hover,

        [data-testid="stFormSubmitButton"]
        button[kind="primary"]:hover {
            background:
                var(--teal-500) !important;
        }


        /* ============================================================
           COMMON SECONDARY BUTTONS
           ============================================================ */

        [data-testid="stButton"]
        button[kind="secondary"],

        [data-testid="stFormSubmitButton"]
        button[kind="secondary"] {
            border:
                1.5px solid var(--line) !important;

            border-radius: 9px !important;

            color:
                var(--navy-900) !important;

            font-weight: 600;

            background: #FFFFFF !important;
        }

        [data-testid="stButton"]
        button[kind="secondary"]:hover,

        [data-testid="stFormSubmitButton"]
        button[kind="secondary"]:hover {
            border-color:
                var(--teal-500) !important;

            color:
                var(--teal-500) !important;
        }


        /* ============================================================
           INPUTS
           ============================================================ */

        [data-testid="stTextInput"] input {
            border:
                1.5px solid var(--line) !important;

            border-radius: 9px !important;
        }

        [data-testid="stTextInput"] input:focus {
            border-color:
                var(--teal-500) !important;

            box-shadow:
                0 0 0 3px
                rgba(15, 139, 141, 0.15)
                !important;
        }


        /* ============================================================
           SELECT BOX
           ============================================================ */

        [data-testid="stSelectbox"]
        div[data-baseweb="select"] > div {
            border-radius: 9px !important;

            border:
                1.5px solid var(--line) !important;
        }


        /* ============================================================
           METRIC CARDS
           ============================================================ */

        [data-testid="stMetric"] {
            background: #FFFFFF !important;

            border-radius: 10px !important;

            border:
                1px solid var(--line) !important;

            padding: 0.9rem 1rem !important;
        }


        /* ============================================================
           TABS
           ============================================================ */

        [data-testid="stTabs"]
        [data-baseweb="tab-list"] {
            gap: 0;

            background: #EAEFF5;

            padding: 4px;

            border-radius: 10px;
        }

        [data-testid="stTabs"]
        [data-baseweb="tab"] {
            border-radius: 8px;

            font-weight: 600;

            font-size: 0.86rem;

            color: var(--ink-600);
        }

        [data-testid="stTabs"]
        [aria-selected="true"] {
            background: #FFFFFF;

            color: var(--navy-900);

            box-shadow:
                0 1px 3px rgba(16, 24, 40, 0.12);
        }

        [data-testid="stTabs"]
        [data-baseweb="tab-highlight"],

        [data-testid="stTabs"]
        [data-baseweb="tab-border"] {
            display: none;
        }


        /* ============================================================
           ALERTS
           ============================================================ */

        [data-testid="stAlert"] {
            border-radius: 9px;

            font-size: 0.88rem;
        }


        /* ============================================================
           HIDE STREAMLIT INPUT INSTRUCTIONS
           ============================================================ */

        [data-testid="InputInstructions"],
        [data-testid="stInputInstructions"],
        [data-testid="stWidgetInstructions"],
        [data-testid="stTextInputInstructions"],
        [data-testid="stTextInput"] [class*="Instructions"],
        [data-testid="stTextInput"] small {
            display: none !important;
        }


        /* ============================================================
           RESPONSIVE - TABLETS
           ============================================================ */

        @media (max-width: 900px) {

            :root {
                --page-gap: 1.5rem;
            }

        }


        /* ============================================================
           RESPONSIVE - MOBILE
           ============================================================ */

        @media (max-width: 600px) {

            :root {
                --page-gap: 1rem;
            }

        }

        </style>
        """
    )


# ============================================================
# TOP NAVIGATION
# ============================================================

def render_sidebar(active_page="Dashboard"):
    """
    Renders the custom doctor top navigation bar.

    The name render_sidebar() is intentionally kept because
    existing pages already import/use that function.
    """

    doctor = st.session_state.get("doctor")

    nav_items = [
        (
            "Dashboard",
            "pages/1_Dashboard.py"
        ),
        (
            "Patient Assessment",
            "pages/2_Patient_Assessment.py"
        ),
    ]


    # ========================================================
    # NAVBAR CONTAINER
    # ========================================================

    with st.container(key="topnav"):

        (
            c_logo,
            c_nav1,
            c_nav2,
            c_spacer,
            c_doctor,
            c_logout
        ) = st.columns(
            [1.6, 1.3, 1.9, 3, 2.6, 1]
        )


        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        with c_logo:

            st.markdown(
                '<div class="topnav-brand">CDSS</div>',
                unsafe_allow_html=True
            )


        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

        for col, (label, page) in zip(
            [c_nav1, c_nav2],
            nav_items
        ):

            with col:

                is_active = active_page == label

                if st.button(
                    label,
                    key=f"nav_{label}",
                    use_container_width=True,
                    type=(
                        "primary"
                        if is_active
                        else "secondary"
                    )
                ):

                    if not is_active:
                        st.switch_page(page)


        # ----------------------------------------------------
        # DOCTOR INFORMATION
        # ----------------------------------------------------

        with c_doctor:

            if doctor:

                full_name = doctor.get(
                    "full_name",
                    ""
                )

                specialization = doctor.get(
                    "specialization",
                    ""
                )

                st.markdown(
                    f"""
                    <div class="topnav-doctor">

                        <b>
                            {full_name}
                        </b>

                        <span class="topnav-doctor-sub">
                            · {specialization}
                        </span>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # ----------------------------------------------------
        # LOGOUT
        # ----------------------------------------------------

        with c_logout:

            if st.button(
                "Logout",
                key="topnav_logout",
                use_container_width=True,
                type="secondary"
            ):

                st.session_state.clear()

                st.switch_page("app.py")