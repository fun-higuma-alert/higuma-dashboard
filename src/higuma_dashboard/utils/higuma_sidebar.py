import streamlit as st

def admin_sidebar():
    with st.sidebar:
        st.page_link("streamlit.py", label="ホーム", icon="🏠")
        st.page_link("pages/information.py", label="プロジェクト紹介", icon="👨‍🎓")