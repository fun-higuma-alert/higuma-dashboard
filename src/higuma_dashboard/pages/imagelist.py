import streamlit as st
import os
import boto3
from io import BytesIO
from PIL import Image
from utils.higuma_sidebar import admin_sidebar

# AWSクレデンシャルの設定
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

# S3クライアントの初期化
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# セッション状態が無い場合に初期化
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_to_page(page_name):
    """ページを変更"""
    st.session_state.page = page_name
    # ボタンを押すたびにページ状態をリセット
    st.session_state.page_index = 0
    if 'data' in st.session_state:
        del st.session_state['data']  # 以前のデータをクリア

# タブの作成
nanae, fun = st.tabs(["七飯町", "はこだて未来大学"])

with nanae:
    st.header("七飯で検出された獣類")
    # 8列のカラムを作成し、最初の2つにボタンを配置
    cols = st.columns(6)
    with cols[0]:
        if st.button("七飯のクマ"):
            go_to_page('nanae_bear')
    with cols[1]:
        if st.button("七飯のシカ"):
            go_to_page('nanae_dear')
    with cols[2]:
        if st.button("七飯のカラス"):
            go_to_page('nanae_crow')
    with cols[3]:
        if st.button("七飯のキツネ"):
            go_to_page('nanae_fox')

with fun:
    st.header("未来大で検出された獣類")
    # 8列のカラムを作成し、最初の2つにボタンを配置
    cols = st.columns(6)
    with cols[0]:
        if st.button("未来大のクマ"):
            go_to_page('fun_bear')
    with cols[1]:
        if st.button("未来大のシカ"):
            go_to_page('fun_dear')
    with cols[2]:
        if st.button("未来大のカラス"):
            go_to_page('fun_crow')
    with cols[3]:
        if st.button("未来大のキツネ"):
            go_to_page('fun_fox')


# フォルダ名を動的に設定
def get_folder_name():
    """現在のページに基づき、フォルダ名を返す"""
    if st.session_state.page == 'nanae_bear':
        return 'camera1/bear'
    elif st.session_state.page == 'nanae_dear':
        return 'camera1/deer'
    elif st.session_state.page == 'nanae_crow':
        return 'camera1/crow'
    elif st.session_state.page == 'nanae_fox':
        return 'camera1/fox'
    elif st.session_state.page == 'fun_bear':
        return 'camera2/bear'
    elif st.session_state.page == 'fun_dear':
        return 'camera2/deer'
    elif st.session_state.page == 'fun_crow':
        return 'camera2/crow'
    elif st.session_state.page == 'fun_fox':
        return 'camera2/fox'
    else:
        return None

def get_images_from_s3():
    """S3から画像のリストを取得"""
    folder_name = get_folder_name()

    if folder_name is None or st.session_state.page == 'home':
        st.warning("フォルダが設定されていません")
        return []

    response = s3.list_objects_v2(Bucket='higuma-detected-images', Prefix=folder_name)

    if 'Contents' not in response:
        st.warning(f"{folder_name}内に画像が見つかりませんでした")
        return []

    image_list = []
    for obj in response['Contents']:
        key = obj['Key']
        if key.endswith('.jpg') or key.endswith('.png') or key.endswith('.jpeg') or key.endswith('.webp'):
            image_list.append(key)
    
    if not image_list:
        st.warning(f"{folder_name}内に画像ファイルがありません")
    
    return image_list

def display_images():
    """10行,6列で画像の表示"""
    if "data" not in st.session_state:
        st.session_state["data"] = get_data()  # 初めて画像を取得する

    if st.session_state["page_index"] >= len(st.session_state["data"]):
        st.warning("ページインデックスが範囲外です")
        return
    
    # ページごとのデータを取得
    for data_per_page in st.session_state["data"][st.session_state["page_index"]]:
        cols = st.columns(6)
        for col_index, col_ph in enumerate(cols):
            if col_index < len(data_per_page):
                img_key = data_per_page[col_index]
                try:
                    img_obj = s3.get_object(Bucket='higuma-detected-images', Key=img_key)
                    img_bytes = img_obj['Body'].read()
                    img = Image.open(BytesIO(img_bytes))
                    col_ph.image(img, use_column_width=True)
                except Exception as e:
                    col_ph.warning(f"画像の読み込みに失敗しました: {e}")

# ページネーションに必要なデータ
def init_session_state():
    """セッションステートの初期化"""
    if "page_index" not in st.session_state:
        st.session_state.page_index = 0

#### アプリケーションロジック ####
def get_data():
    """S3から画像を3次元配列で格納"""
    pages = []
    rows = []
    cols = []
    
    image_list = get_images_from_s3()  # S3から画像リストを取得
    
    for img_key in image_list:
        cols.append(img_key)
        if len(cols) >= 6:
            rows.append(cols)
            cols = []
        if len(rows) >= 5:
            pages.append(rows)
            rows = []
    
    if cols:  # 最後の残りのカラムを追加
        rows.append(cols)
    if rows:  # 最後の残りの行を追加
        pages.append(rows)
    
    return pages

def update_index(session_key, num, max_val=None):
    """ページネーションのインデックスを更新"""
    if max_val:
        if st.session_state[session_key] < max_val - num:
            st.session_state[session_key] += num
    else:
        if st.session_state[session_key] >= num:
            st.session_state[session_key] -= num

def pagination():
    """ページネーションボタンの表示"""
    col1, col2, col3 = st.columns([1, 8, 1])

    col1.button("前へ" * 1, on_click=update_index, args=("page_index", 1))
    col3.button("次へ" * 1, on_click=update_index, args=("page_index", 1, len(st.session_state["data"])))

    col2.markdown(
        f"""
        <div style='text-align: center;'>
            {st.session_state["page_index"] + 1} / {len(st.session_state["data"])}
        </div>
        """,
        unsafe_allow_html=True,
    )

#### メイン処理 ####
def main():
    """メイン処理"""
    init_session_state()
    display_images()
    pagination()

# ページネーションを有効化して実行
if st.session_state.page != 'home':
    main()

# サイドバーの表示
admin_sidebar()
