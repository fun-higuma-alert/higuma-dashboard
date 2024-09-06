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
bucket_name = 'higuma-detected-images'

# 初期フォルダ設定
folder_name = 'camera1/bear'  # デフォルトはクマのフォルダ

# タイトルの設定
st.title("過去の検出画像")

# ページの初期状態をセッションステートに保存
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ページ遷移のための関数
def go_to_page(page_name):
    st.session_state.page = page_name

# タブの設定
nanae, fun = st.tabs(["七飯町", "はこだて未来大学"])

# 七飯町タブの内容
with nanae:
    st.header("七飯で検出された獣類")
    if st.button("七飯のクマ"):
        go_to_page('nanae_bear')
    if st.button("七飯のシカ"):
        go_to_page('nanae_deer')

with fun:
    st.header("未来大で検出された獣類")
    if st.button("未来大のクマ"):
        go_to_page('fun_bear')
    if st.button("未来大のシカ"):
        go_to_page('fun_dear')


# 参照するフォルダを動的に設定
if st.session_state.page == 'nanae_bear':
    folder_name = 'camera1/bear'  # 七飯のクマフォルダ
    st.write("七飯のクマ一覧")
elif st.session_state.page == 'nanae_deer':
    folder_name = 'camera1/deer'  # 七飯のシカフォルダ
    st.write("七飯のシカ一覧")
elif st.session_state.page == 'fun_bear':
    folder_name = 'camera1/crow'  # 七飯のシカフォルダ
    st.write("未来大のクマ一覧")
elif st.session_state.page == 'fun_dear':
    folder_name = 'camera1/fox'  # 七飯のシカフォルダ
    st.write("未来大のシカ一覧")

# S3から画像を取得する関数
def get_images_from_s3():
    """S3から画像のリストを取得"""
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
    image_list = []
    
    for obj in response.get('Contents', []):
        key = obj['Key']
        if key.endswith('.jpg') or key.endswith('.png') or key.endswith('.jpeg'):
            image_list.append(key)
    
    return image_list

# セッションステートの取得
ss = st.session_state

#### セッション管理 ####
def init_session_state():
    """セッションステートの初期化"""
    if "data" not in ss:
        ss["data"] = get_data()
  
    if "page_index" not in ss:
        ss["page_index"] = 0

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
        if 0 <= ss[session_key] + num < max_val:  # max_valの範囲内か確認
            ss[session_key] += num
    else:
        if ss[session_key] >= num:
            ss[session_key] -= num

#### 画面描画 ####
def display_images():
    """10行,6列で画像の表示"""
    if ss["page_index"] >= len(ss["data"]):
        st.warning("ページインデックスが範囲外です")
        return  # これ以上のページがない場合は表示を行わない
    
    for data_per_page in ss["data"][ss["page_index"]]:
        cols = st.columns(6)  # 6列で表示する
        for col_index, col_ph in enumerate(cols):
            if col_index < len(data_per_page):  # data_per_pageの長さを超えないようにチェック
                img_key = data_per_page[col_index]
                img_obj = s3.get_object(Bucket=bucket_name, Key=img_key)
                img_bytes = img_obj['Body'].read()
                img = Image.open(BytesIO(img_bytes))
                col_ph.image(img)

def pagination():
    """ページネーションボタンの表示"""
    col1, col2, col3 = st.columns([1, 8, 1])

    max_pages = len(ss["data"])

    if col1.button("前へ"):
        update_index("page_index", -1, max_pages)
    if col3.button("次へ"):
        update_index("page_index", 1, max_pages)

    col2.markdown(
        f"""
        <div style='text-align: center;'>
            ページ {ss["page_index"] + 1} / {max_pages}
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
main()

# サイドバーの表示
admin_sidebar()