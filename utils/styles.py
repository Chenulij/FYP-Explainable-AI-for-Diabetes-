import streamlit as st
import os

def load_css():
    # Hide default Streamlit sidebar navigation
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

    # Load custom CSS file
    css_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "style.css"
    )
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_sidebar(active_page="Dashboard"):
    """
    Renders custom sidebar navigation for doctors.
    Only shows Dashboard and Patient Assessment.
    Everything else is accessed through the natural flow.
    """
    with st.sidebar:
        st.markdown("""
            <div style='padding: 1rem 0 0.5rem 0; text-align: center;'>
                <div style='font-size: 2rem;'>🏥</div>
                <div style='font-size: 0.85rem; font-weight: bold; 
                            color: #1e293b; margin-top: 0.3rem;'>
                    Diabetes CDSS
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Doctor info
        if "doctor" in st.session_state and st.session_state.doctor:
            doctor = st.session_state.doctor
            st.markdown(f"""
                <div style='font-size: 0.8rem; color: #64748b; 
                            padding: 0 0.5rem; margin-bottom: 0.5rem;'>
                    👨‍⚕️ <strong>{doctor['full_name']}</strong><br/>
                    {doctor['specialization']}<br/>
                    ID: {doctor['doctor_id']}
                </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Navigation — only Dashboard and Patient Assessment
        nav_items = [
            ("🏠", "Dashboard", "pages/1_Dashboard.py"),
            ("📋", "Patient Assessment", "pages/2_Patient_Assessment.py"),
        ]

        for icon, label, page in nav_items:
            is_active = active_page == label
            if is_active:
                st.markdown(f"""
                    <div style='background: #2563eb; border-radius: 8px; 
                                padding: 0.6rem 1rem; margin-bottom: 0.3rem;
                                color: white; font-weight: bold; font-size: 0.9rem;'>
                        {icon} {label}
                    </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(f"{icon} {label}", key=f"nav_{label}",
                             use_container_width=True):
                    st.switch_page(page)

        st.divider()

        # Logout at bottom
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.switch_page("app.py")