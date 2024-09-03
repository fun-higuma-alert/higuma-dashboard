import streamlit as st
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import numpy as np
from higuma_sidebar import admin_sidebar

# ページ設定
st.set_page_config(layout="wide")

import branca
from dotenv import load_dotenv
import os

load_dotenv()

# Streamlitのタイトル
st.title("Folium Map in Streamlit")

# 地図の中心座標とズームレベルを設定
map_center = [41.768793, 140.728810]  # 函館の座標
zoom_level = 10

# Mapboxのアクセストークンを設定
mapbox_token = os.getenv("MAPBOX_TOKEN")

# 日本語のMapboxタイルURL
japanese_tiles = f'https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={mapbox_token}&language=ja'

# 初期値設定
if 'initial_info' not in st.session_state:
    st.session_state['initial_info'] = [
        {
            "name": "函館駅",
            "location": [41.768793, 140.728810],
            "established": 1902,
            "html": """
                <b>函館駅</b><br>
                <i>所在地:</i> 北海道函館市<br>
                <i>開業:</i> 1902年<br>
                <i>運営:</i> JR北海道<br>
                <i>路線:</i> 函館本線<br>
                <img src="https://test-image-higuma.s3.ap-northeast-1.amazonaws.com/kuma.png" alt="函館駅" width="200">
            """
        },
        {
            "name": "はこだて未来大学",
            "location": [41.841505, 140.766193],
            "established": 2000,
            "html": """
                <b>はこだて未来大学</b><br>
                <i>所在地:</i> 北海道函館市<br>
                <i>設立:</i> 2000年<br>
                <i>学部:</i> システム情報科学部<br>
                <img src="https://test-image-higuma.s3.ap-northeast-1.amazonaws.com/FUN.jpg" alt="はこだて未来大学" width="200">
            """
        }
    ]

# 現在の表示情報を初期値に設定
if 'location_info' not in st.session_state:
    st.session_state['location_info'] = st.session_state['initial_info']

# ボタン間の空白を減らす
cols = st.columns(8)  # より多くの列を作成

with cols[0]:
    if st.button("🐻 クマ", key="bear"):
        st.session_state['location_info'] = st.session_state['initial_info']
        st.experimental_rerun()

with cols[1]:
    if st.button("🫎 シカ", key="deer"):
        st.session_state['location_info'] = [
            {
                "name": "函館駅",
                "location": [41.768793, 140.728810],
                "established": 1902,
                "html": """
                    <b>函館駅の鹿</b><br>
                    <i>テスト:</i> 鹿の情報<br>
                    <img src="https://test-image-higuma.s3.ap-northeast-1.amazonaws.com/shika.jpg" alt="函館駅" width="200">
                """
            },
            {
                "name": "はこだて未来大学",
                "location": [41.841505, 140.766193],
                "established": 2000,
                "html": """
                    <b>はこだて未来大学の鹿</b><br>
                    <i>テスト:</i> 鹿の情報<br>
                    <img src="https://test-image-higuma.s3.ap-northeast-1.amazonaws.com/shika.jpg" alt="はこだて未来大学" width="200">
                """
            }
        ]
        st.experimental_rerun()

with cols[2]:
    if st.button("🐦‍⬛ カラス", key="crow"):
        st.session_state['location_info'] = [
            {
                "name": "函館駅",
                "location": [41.768793, 140.728810],
                "established": 1902,
                "html": """
                    <b>函館駅のカラス</b><br>
                    <i>テスト:</i> カラスの情報<br>
                    <img src="https://test-image-higuma.s3.ap-northeast-1.amazonaws.com/crow.jpg" alt="函館駅" width="200">
                """
            },
            {
                "name": "はこだて未来大学",
                "location": [41.841505, 140.766193],
                "established": 2000,
                "html": """
                    <b>はこだて未来大学のカラス</b><br>
                    <i>テスト:</i> カラスの情報<br>
                    <img src="https://test-image-higuma.s3.ap-northeast-1.amazonaws.com/crow.jpg" alt="はこだて未来大学" width="200">
                """
            }
        ]
        st.experimental_rerun()

with cols[3]:
    if st.button("🦊 キツネ", key="fox"):
        st.session_state['location_info'] = [
            {
                "name": "函館駅",
                "location": [41.768793, 140.728810],
                "established": 1902,
                "html": """
                    <b>函館駅のキツネ</b><br>
                    <i>テスト:</i> キツネの情報<br>
                    <img src="https://test-image-higuma.s3.ap-northeast-1.amazonaws.com/kitune.jpg" alt="函館駅" width="200">
                """
            },
            {
                "name": "はこだて未来大学",
                "location": [41.841505, 140.766193],
                "established": 2000,
                "html": """
                    <b>はこだて未来大学のキツネ</b><br>
                    <i>テスト:</i> キツネの情報<br>
                    <img src="https://test-image-higuma.s3.ap-northeast-1.amazonaws.com/kitune.jpg" alt="はこだて未来大学" width="200">
                """
            }
        ]
        st.experimental_rerun()

# Foliumで地図を作成（日本語Mapboxタイルを使用）
m = folium.Map(
    location=map_center,
    zoom_start=zoom_level,
    tiles=None
)

folium.TileLayer(
    tiles=japanese_tiles,
    attr='Mapbox',
    name='Mapbox',
    overlay=True,
    control=True
).add_to(m)

# カラーバーで使用する色と対応する設立年の範囲を定義
colors = ["#ffa07a", "#ff6347", "#ff0000"]
year_ranges = [(2000, 2024), (1950, 1999), (1900, 1949)]

# 年に基づいて色を決定する関数
def get_color_by_year(established_year):
    for color, (start_year, end_year) in zip(colors, year_ranges):
        if start_year <= established_year <= end_year:
            return color
    return "#ffffff"  # デフォルトの色（範囲外の場合）

# 各マーカーを追加
for loc in st.session_state['location_info']:
    color = get_color_by_year(loc["established"])
    folium.CircleMarker(
        location=loc["location"],
        radius=10,  # 円の半径
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        tooltip=loc["html"]
    ).add_to(m)

# カラーバーを作成する関数
def create_color_bar():
    # カラーバーを作成
    fig, ax = plt.subplots(figsize=(0.5, 4))  # サイズを調整
    cmap = plt.cm.colors.ListedColormap(colors)  # カラーマップをリストから作成
    norm = plt.Normalize(vmin=0, vmax=len(colors))
    cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax)
    cb.set_ticks(np.arange(len(colors)) + 0.5)
    cb.set_ticklabels([f"{start}-{end}" for start, end in year_ranges])
    cb.ax.invert_yaxis()
    cb.ax.tick_params(labelsize=10)  # フォントサイズを適切に設定

    return fig

# レイアウトを調整
col1, col2 = st.columns([8, 1])  # カラムの比率を調整

with col1:
    folium_static(m, width=1600, height=1000)
with col2:
    fig = create_color_bar()
    st.pyplot(fig)

admin_sidebar()
