import streamlit as st
import os
import sys
from utils.higuma_sidebar import admin_sidebar

st.title("過去の検出画像")

if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_to_page(page_name):
    st.session_state.page = page_name

nanae, fun = st.tabs(["七飯町", "はこだて未来大学"])

with nanae:
    st.header("七飯で検出された獣類")
    if st.button("七飯のクマ"):
        go_to_page('nanae_bear')
    if st.button("七飯のシカ"):
        go_to_page('nanae_dear')

with fun:
    st.header("未来大で検出された獣類")
    if st.button("未来大のクマ"):
        go_to_page('fun_bear')
    if st.button("未来大のシカ"):
        go_to_page('fun_dear')

if st.session_state.page == 'nanae_bear':
    st.write("七飯のクマ一覧")
elif st.session_state.page == 'nanae_dear':
    st.write("七飯のシカ一覧")
elif st.session_state.page == 'fun_bear':
    st.write("未来大のクマ一覧")
elif st.session_state.page == 'fun_dear':
    st.write("未来大のシカ一覧")
else:
    st.write("場所と閲覧したい検出された過去の獣類を選択してください")

admin_sidebar()