import streamlit as st
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from utils.higuma_sidebar import admin_sidebar
import boto3
from io import BytesIO
from PIL import Image
import base64
from dotenv import load_dotenv
from datetime import timedelta

# ページ設定
st.set_page_config(layout="wide")

import branca
from dotenv import load_dotenv

load_dotenv()

# Streamlitのタイトル
st.title("ヒグマダッシュボード")

# 地図の中心座標とズームレベルを設定
map_center = [41.768793, 140.728810]  # 函館の座標
zoom_level = 10

# AWSクレデンシャルの設定
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
bucket_name = 'higuma-detected-images'

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# 動物に応じてS3フォルダを参照する処理を共通化
def update_location_info(animal, folder_path, alt_text):
    latest_image_key = get_latest_image_from_s3(bucket_name, folder_path)
    image_url = get_image_url_from_s3(bucket_name, latest_image_key) if latest_image_key else ""

    # 画像の更新日時を取得し、9時間を追加
    latest_image_info = list_images_in_s3_folder(bucket_name, folder_path)
    latest_image_time = max(latest_image_info, key=lambda x: x[1])[1] if latest_image_info else None
    if latest_image_time:
        last_modified_jst = latest_image_time + timedelta(hours=9)
        last_modified_str = last_modified_jst.strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_modified_str = "更新日時不明"

    st.session_state['location_info'] = [
        {
            "name": f"函館駅の{animal}",
            "location": [41.768793, 140.728810],
            "established": 1902,
            "html": f"""
                <b>函館駅の{animal}</b><br>
                <i>テスト:</i> {animal}の情報<br>
                <img src="{image_url}" alt="{alt_text}" width="200"><br>
                <i>出現日時:</i> {last_modified_str}
            """
        },
        {
            "name": f"はこだて未来大学の{animal}",
            "location": [41.841505, 140.766193],
            "established": 2000,
            "html": f"""
                <b>はこだて未来大学の{animal}</b><br>
                <i>テスト:</i> {animal}の情報<br>
                <img src="https://test-image-higuma.s3.ap-northeast-1.amazonaws.com/{alt_text}.jpg" alt="{alt_text}" width="200">
            """
        }
    ]
    st.experimental_rerun()


# S3からフォルダ内の最新の画像を取得
def get_latest_image_from_s3(bucket, folder):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder)
        images = [(content['Key'], content['LastModified']) for content in response.get('Contents', []) if content['Key'].lower().endswith(('png', 'jpg', 'jpeg', 'gif'))]
        if not images:
            return None
        latest_image = max(images, key=lambda x: x[1])[0]  # 最新の画像
        return latest_image
    except Exception as e:
        st.error(f"S3から最新の画像の取得中にエラーが発生しました: {e}")
        return None

# S3内の最新の画像のURLを取得
def get_image_url_from_s3(bucket, image_key):
    try:
        url = s3_client.generate_presigned_url('get_object',
            Params={'Bucket': bucket, 'Key': image_key},
            ExpiresIn=3600)  # URLの有効期限を1時間に設定
        return url
    except Exception as e:
        st.error(f"画像URLの取得中にエラーが発生しました: {e}")
        return None

def list_images_in_s3_folder(bucket, folder):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder)
        images = [(content['Key'], content['LastModified']) for content in response.get('Contents', []) if content['Key'].lower().endswith(('png', 'jpg', 'jpeg', 'gif'))]
        if not images:
            st.error(f"フォルダ '{folder}' には画像が見つかりませんでした。")
        return images
    except Exception as e:
        st.error(f"画像リストの取得中にエラーが発生しました: {e}")
        return []


    
    # S3から画像を取得
folder_path = 'camera1/higuma/'
image_info = list_images_in_s3_folder(bucket_name, folder_path)

# Mapboxのアクセストークンを設定
mapbox_token = os.getenv("MAPBOX_TOKEN")

# 日本語のMapboxタイルURL
japanese_tiles = 'https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png'

# 初期値設定
if 'initial_info' not in st.session_state:
    # S3から最新画像を取得
    latest_image_key = get_latest_image_from_s3(bucket_name, 'camera1/higuma/')
    image_url = get_image_url_from_s3(bucket_name, latest_image_key) if latest_image_key else ""
    
    # 画像の更新日時を取得し、9時間を追加
    latest_image_info = list_images_in_s3_folder(bucket_name, 'camera1/higuma/')
    latest_image_time = max(latest_image_info, key=lambda x: x[1])[1] if latest_image_info else None
    if latest_image_time:
        # 9時間を追加
        last_modified_jst = latest_image_time + timedelta(hours=9)
        last_modified_str = last_modified_jst.strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_modified_str = "更新日時不明"

    st.session_state['initial_info'] = [
        {
            "name": "函館駅",
            "location": [41.768793, 140.728810],
            "established": 1902,
            "html": f"""
                <b>函館駅</b><br>
                <i>所在地:</i> 北海道函館市<br>
                <i>開業:</i> 1902年<br>
                <img src="{image_url}" alt="函館駅" width="200"><br>
                <i>出現日時:</i> {last_modified_str}
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
        update_location_info('クマ', 'camera1/higuma/', 'kuma')

with cols[1]:
    if st.button("🫎 シカ", key="deer"):
        update_location_info('シカ', 'camera1/deer/', 'shika')

with cols[2]:
    if st.button("🐦‍⬛ カラス", key="crow"):
        update_location_info('カラス', 'camera1/crow/', 'crow')

with cols[3]:
    if st.button("🦊 キツネ", key="fox"):
        update_location_info('キツネ', 'camera1/fox/', 'kitune')


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
col1, col2 = st.columns([14, 1])  # カラムの比率を調整

with col1:
    folium_static(m, width=1370, height=700)
with col2:
    fig = create_color_bar()
    st.pyplot(fig)

admin_sidebar()