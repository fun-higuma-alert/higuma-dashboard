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
from datetime import datetime

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

def update_location_info(animal, folder_path, alt_text):
    # camera1 と camera2 を動的に参照する
    latest_image_key_camera1 = get_latest_image_from_s3(bucket_name, f'camera1/{folder_path}')
    image_url_camera1 = get_image_url_from_s3(bucket_name, latest_image_key_camera1) if latest_image_key_camera1 else ""

    latest_image_key_camera2 = get_latest_image_from_s3(bucket_name, f'camera2/{folder_path}')
    image_url_camera2 = get_image_url_from_s3(bucket_name, latest_image_key_camera2) if latest_image_key_camera2 else ""

    # 画像の更新日時を取得し、9時間を追加
    latest_image_info_camera1 = list_images_in_s3_folder(bucket_name, f'camera1/{folder_path}')
    latest_image_time_camera1 = max(latest_image_info_camera1, key=lambda x: x[1])[1] if latest_image_info_camera1 else None

    latest_image_info_camera2 = list_images_in_s3_folder(bucket_name, f'camera2/{folder_path}')
    latest_image_time_camera2 = max(latest_image_info_camera2, key=lambda x: x[1])[1] if latest_image_info_camera2 else None

    # 日本時間に合わせて9時間追加
    if latest_image_time_camera1:
        last_modified_jst_camera1 = latest_image_time_camera1 + timedelta(hours=9)
        last_modified_str_camera1 = last_modified_jst_camera1.strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_modified_str_camera1 = "更新日時不明"

    if latest_image_time_camera2:
        last_modified_jst_camera2 = latest_image_time_camera2 + timedelta(hours=9)
        last_modified_str_camera2 = last_modified_jst_camera2.strftime("%Y-%m-%d %H:%M:%S")
    else:
        last_modified_str_camera2 = "更新日時不明"

    # st.session_state にカメラ1とカメラ2の画像情報を格納し、"last_modified" キーを追加
    st.session_state['location_info'] = [
        {
            "name": f"大沼ネイチャーセンターの{animal}",
            "location": [41.982099, 140.669183],
            "day": 1902,
            "html": f"""
                <b>大沼ネイチャーセンターの{animal}</b><br>
                <i>テスト:</i> {animal}の情報<br>
                <img src="{image_url_camera1}" alt="{alt_text}" width="200"><br>
                <i>出現日時:</i> {last_modified_str_camera1}
            """,
            "last_modified": last_modified_str_camera1  # camera1の更新日時をキーに渡す
        },
        {
            "name": f"はこだて未来大学の{animal}",
            "location": [41.841505, 140.766193],
            "day": 2000,
            "html": f"""
                <b>はこだて未来大学の{animal}</b><br>
                <i>テスト:</i> {animal}の情報<br>
                <img src="{image_url_camera2}" alt="{alt_text}" width="200"><br>
                <i>出現日時:</i> {last_modified_str_camera2}
            """,
            "last_modified": last_modified_str_camera2  # camera2の更新日時をキーに渡す
        }
    ]
    st.rerun()


# S3からフォルダ内の最新の画像を取得
def get_latest_image_from_s3(bucket, folder):
    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder)
        images = [(content['Key'], content['LastModified']) for content in response.get('Contents', []) if content['Key'].lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'webp'))]
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
        images = [(content['Key'], content['LastModified']) for content in response.get('Contents', []) if content['Key'].lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'webp'))]
        if not images:
            st.error(f"フォルダ '{folder}' には画像が見つかりませんでした。")
        return images
    except Exception as e:
        st.error(f"画像リストの取得中にエラーが発生しました: {e}")
        return []


# Mapboxのアクセストークンを設定
mapbox_token = os.getenv("MAPBOX_TOKEN")

# 日本語のMapboxタイルURL
japanese_tiles = 'https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png'

# 初期値設定
if 'location_info' not in st.session_state:
    update_location_info('クマ', 'bear/', 'kuma')

# ボタン間の空白を減らす
cols = st.columns(8)  # より多くの列を作成

with cols[0]:
    if st.button("🐻 クマ", key="bear"):
        update_location_info('クマ', 'bear/', 'kuma')

with cols[1]:
    if st.button("🫎 シカ", key="deer"):
        update_location_info('シカ', 'deer/', 'shika')

with cols[2]:
    if st.button("🐦‍⬛ カラス", key="crow"):
        update_location_info('カラス', 'crow/', 'crow')

with cols[3]:
    if st.button("🦊 キツネ", key="fox"):
        update_location_info('キツネ', 'fox/', 'kitune')


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
day_ranges = [(11, 30), (6, 10), (0, 5)]

# 出現日に基づいて色を決定する関数 (更新日時との比較)
def get_color_by_day(last_modified_str):
    if last_modified_str == "更新日時不明":
        return "#ffffff"  # デフォルトの色（範囲外の場合）

    # 現在時刻と更新日時の差分を計算
    last_modified_time = datetime.strptime(last_modified_str, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    day_diff = (now - last_modified_time).days

    for color, (start_day, end_day) in zip(colors, day_ranges):
        if start_day <= day_diff <= end_day:
            return color
    return "#ffffff"  # デフォルトの色（範囲外の場合）

# 各マーカーを追加
for loc in st.session_state['location_info']:
    color = get_color_by_day(loc["last_modified"])
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
    cb.set_ticklabels([f"{start}~{end}" for start, end in day_ranges])
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