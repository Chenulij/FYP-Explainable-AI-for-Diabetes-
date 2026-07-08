import streamlit as st
if "doctor" not in st.session_state or not st.session_state.doctor:
    st.switch_page("app.py")
st.set_page_config(page_title="Patient Report", page_icon="📄", layout="wide")
st.title("📄 Patient Report")
st.info("Coming soon.")