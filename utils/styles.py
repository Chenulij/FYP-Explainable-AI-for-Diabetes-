import streamlit as st


def load_css():
    st.markdown(
        """
        <style>

        /* ============================================================
           GLOBAL VARIABLES
           ============================================================ */

        :root {
            --bg: #F4F7FB;
            --navy-900: #0D304E;
            --navy-800: #123A5C;

            --teal-500: #0F8B8D;
            --teal-400: #18A6A8;

            --ink-900: #172033;
            --ink-700: #344054;
            --ink-600: #52627A;

            --line: #D7DFE9;

            --page-gap: 2.5rem;
        }


        /* ============================================================
           REMOVE STREAMLIT DEFAULT HEADER
           ============================================================ */

        [data-testid="stHeader"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
        }

        [data-testid="stDecoration"] {
            display: none !important;
        }


        /* ============================================================
           APP BACKGROUND
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

        [data-testid="stAppViewContainer"] > .main .block-container {

            width: 100% !important;
            max-width: 100% !important;

            margin: 0 !important;

            /*
                Remove space above navbar
            */
            padding-top: 0 !important;

            /*
                Keep actual page content away from edges
            */
            padding-left: var(--page-gap) !important;
            padding-right: var(--page-gap) !important;

            padding-bottom: 3rem !important;

            box-sizing: border-box !important;
        }


        /* ============================================================
           TOP NAVIGATION
           ============================================================ */

        .st-key-topnav {

            /*
                Make navbar full browser width
            */
            width: calc(100% + (2 * var(--page-gap))) !important;

            max-width: none !important;

            /*
                Pull navbar back to browser's left edge
            */
            margin-left: calc(-1 * var(--page-gap)) !important;

            /*
                No unwanted top spacing
            */
            margin-top: 0 !important;

            /*
                Space below navbar
            */
            margin-bottom: 2rem !important;

            /*
                STRAIGHT CORNERS
            */
            border-radius: 0 !important;

            /*
                Navbar internal spacing
            */
            padding: 0.75rem var(--page-gap) !important;

            box-sizing: border-box !important;

            background: var(--navy-900) !important;

            position: relative;

            z-index: 100;
        }


        /* ============================================================
           NAVBAR ALIGNMENT
           ============================================================ */

        .st-key-topnav [data-testid="stHorizontalBlock"] {
            align-items: center !important;
        }

        .st-key-topnav [data-testid="column"],
        .st-key-topnav [data-testid="stColumn"] {
            padding: 0 !important;
        }


        /* ============================================================
           NAVBAR BRAND
           ============================================================ */

        .topnav-brand {
            color: #FFFFFF !important;

            font-weight: 700;

            font-size: 1.02rem;

            letter-spacing: 0.02em;

            line-height: 1;
        }


        /* ============================================================
           DOCTOR / ADMIN INFORMATION
           ============================================================ */

        .topnav-doctor {
            color: rgba(255,255,255,0.90) !important;

            font-size: 0.84rem;

            text-align: right;

            line-height: 1.3;
        }

        .topnav-doctor-sub {
            color: rgba(255,255,255,0.50) !important;
        }


        /* ============================================================
           PROFILE
           ============================================================ */

        .topnav-profile {

            display: flex;

            align-items: center;

            justify-content: flex-end;

            gap: 0.8rem;
        }


        /* ============================================================
           AVATAR
           ============================================================ */

        .topnav-avatar {

            width: 44px;

            height: 44px;

            border-radius: 50%;

            display: flex;

            align-items: center;

            justify-content: center;

            background: rgba(255,255,255,0.10);

            border: 1px solid rgba(255,255,255,0.22);

            color: #FFFFFF;

            font-size: 0.78rem;

            font-weight: 600;

            box-sizing: border-box;
        }


        /* ============================================================
           NAVBAR BUTTONS
           ============================================================ */

        .st-key-topnav [data-testid="stButton"] {
            margin: 0 !important;
        }

        .st-key-topnav [data-testid="stButton"] button {

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
           ACTIVE NAV BUTTON
           ============================================================ */

        .st-key-topnav
        [data-testid="stButton"]
        button[kind="primary"] {

            background: var(--teal-500) !important;

            border: 1px solid var(--teal-500) !important;

            color: #FFFFFF !important;
        }

        .st-key-topnav
        [data-testid="stButton"]
        button[kind="primary"]:hover {

            background: var(--teal-400) !important;

            border-color: var(--teal-400) !important;
        }


        /* ============================================================
           NORMAL NAV / LOGOUT BUTTON
           ============================================================ */

        .st-key-topnav
        [data-testid="stButton"]
        button[kind="secondary"] {

            background: transparent !important;

            border: 1px solid rgba(255,255,255,0.28) !important;

            color: rgba(255,255,255,0.92) !important;
        }

        .st-key-topnav
        [data-testid="stButton"]
        button[kind="secondary"]:hover {

            background: rgba(255,255,255,0.08) !important;

            border-color: rgba(255,255,255,0.50) !important;
        }


        /* ============================================================
           COMMON TYPOGRAPHY
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
           COMMON BUTTONS
           ============================================================ */

        [data-testid="stButton"] button {

            border-radius: 9px !important;

            font-weight: 600;
        }

        [data-testid="stButton"]
        button[kind="primary"],

        [data-testid="stFormSubmitButton"]
        button[kind="primary"] {

            background: var(--navy-900) !important;

            border: none !important;

            border-radius: 9px !important;

            font-weight: 600;
        }

        [data-testid="stButton"]
        button[kind="primary"]:hover,

        [data-testid="stFormSubmitButton"]
        button[kind="primary"]:hover {

            background: var(--teal-500) !important;
        }


        /* ============================================================
           SECONDARY BUTTONS
           ============================================================ */

        [data-testid="stButton"]
        button[kind="secondary"],

        [data-testid="stFormSubmitButton"]
        button[kind="secondary"] {

            border: 1.5px solid var(--line) !important;

            border-radius: 9px !important;

            color: var(--navy-900) !important;

            font-weight: 600;

            background: #FFFFFF !important;
        }

        [data-testid="stButton"]
        button[kind="secondary"]:hover,

        [data-testid="stFormSubmitButton"]
        button[kind="secondary"]:hover {

            border-color: var(--teal-500) !important;

            color: var(--teal-500) !important;
        }


        /* ============================================================
           INPUTS
           ============================================================ */

        [data-testid="stTextInput"] input {

            border: 1.5px solid var(--line) !important;

            border-radius: 9px !important;
        }

        [data-testid="stTextInput"] input:focus {

            border-color: var(--teal-500) !important;

            box-shadow:
                0 0 0 3px rgba(15,139,141,0.15) !important;
        }


        /* ============================================================
           SELECT BOX
           ============================================================ */

        [data-testid="stSelectbox"]
        div[data-baseweb="select"] > div {

            border-radius: 9px !important;

            border: 1.5px solid var(--line) !important;
        }


        /* ============================================================
           METRIC CARDS
           ============================================================ */

        [data-testid="stMetric"] {

            background: #FFFFFF !important;

            border-radius: 10px !important;

            border: 1px solid var(--line) !important;

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
                0 1px 3px rgba(16,24,40,0.12);
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
           RESPONSIVE
           ============================================================ */

        @media (max-width: 900px) {

            :root {
                --page-gap: 1.5rem;
            }

            .st-key-topnav {

                padding-left: var(--page-gap) !important;

                padding-right: var(--page-gap) !important;
            }
        }


        @media (max-width: 600px) {

            :root {
                --page-gap: 1rem;
            }

            .st-key-topnav {

                padding-left: var(--page-gap) !important;

                padding-right: var(--page-gap) !important;
            }
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    """
    Kept for compatibility with existing pages.

    The application uses the custom top navigation instead
    of the default Streamlit sidebar.
    """

    st.markdown(
        """
        <style>

        /*
            Completely hide Streamlit's default sidebar.
        */

        [data-testid="stSidebar"] {
            display: none !important;
        }

        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )