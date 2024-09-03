import streamlit as st
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))

# information.pyからの相対パスで画像ファイルのパスを取得
image_files = [os.path.join(script_dir, '..', 'static', 'data', f'page_{i+1}.png') for i in range(3)]

# 取得したパスを絶対パスに変換
image_files = [os.path.abspath(image_file) for image_file in image_files]

st.title("🐻ヒグマプロジェクト")

# プロジェクト紹介セクション（1列レイアウト）
st.subheader("プロジェクト紹介")
for i, image_file in enumerate(image_files):
    st.image(image_file, use_column_width=True)

with st.sidebar:
    st.page_link("streamlit.py", label="ホーム", icon="🏠")
    st.page_link("pages/information.py", label="ヘルプ", icon="❓")
