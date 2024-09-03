import streamlit as st

image_files = [f'higuma_dashboard/data/page_{i+1}.png' for i in range(3)]  # 3ページ分の画像

st.title("🐻ヒグマプロジェクト")

# 2. PDFの紹介セクション（1列レイアウト）
st.subheader("プロジェクト紹介")
for i, image_file in enumerate(image_files):
    st.image(image_file, use_column_width=True)
