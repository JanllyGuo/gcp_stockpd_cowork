# 載入相關套件
import yfinance as yf
import mpl_finance as mpf
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager
import pandas as pd
from google.cloud import storage
from google.cloud import firestore
# 載入LineBot所需要的套件
from flask import Flask, request, abort
from flask_cors import CORS
# 引用line套件
from linebot import (
    LineBotApi, WebhookHandler
)
# 驗證消息用的套件
from linebot.exceptions import (
    InvalidSignatureError
)
# 引用消息套件
# from linebot.models import 
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage
)
# 載入Follow 關注事件 , Unfollow event 封鎖事件
from linebot.models.events import (
    FollowEvent, UnfollowEvent
)

# 圖片下載與上傳專用
import urllib.request
import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

# 建立日誌紀錄設定檔
# https://googleapis.dev/python/logging/latest/stdlib-usage.html
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler

# 啟用log的客戶端
client = google.cloud.logging.Client()
# 建立line event log，用來記錄line event
bot_event_handler = CloudLoggingHandler(client, name="stockbot_test_event")
bot_event_logger = logging.getLogger('stockbot_test_event')
bot_event_logger.setLevel(logging.INFO)
bot_event_logger.addHandler(bot_event_handler)

# 準備APP
app = Flask(__name__)
CORS(app)

# 註冊機器人
# 跟line溝通的
line_bot_api=LineBotApi(channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
# 收發消息專用
handler=WebhookHandler(channel_secret=os.environ["LINE_CHANNEL_SECRET"])


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    # print(body)
    # 消息整個交給bot_event_logger，請它傳回GCP
    bot_event_logger.info(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


'''
消息素材準備
'''
# @的素材
# 先直接寫死 之後改先去查股票表列
stock_list = ['2303', '2317', '2327', '2330', '2345', '2377',
              '2395', '2409', '2454', '3037', '3481', '3532', '6415', '8046']
stock_arry = ""
for i in stock_list:
    stock_arry = stock_arry + i + "\n"

ticket_message = TextSendMessage(
    "查詢股票走勢圖\n請加N或T(大寫)\n例如:當下走勢圖=>N+股號\n         當下日K圖=>T+股號\n\n股票查詢中的股票可加P或F\n查詢預測圖與型態特徵圖\n" + stock_arry + "例如:預測走勢圖=>P+股號\n         形態特徵圖=>F+股號")

contact_us_message = TextSendMessage("請將問題寄到我們的信箱xxx@xxx.com ，有專人會回覆您")

'''
設計一個字典
當用戶輸入相應文字消息時，系統會從此挑揀消息
'''
# 根據自定義菜單四張故事線的圖，設定相對應image
ticket_message_dict = {
    "@股票查詢": ticket_message,
    "@聯絡我們": contact_us_message
}

'''
共用函式: 抓資料 , 畫圖 , 上傳圖檔
'''
# 抓資料
def stock_data(stock_or, period, interval):
    """
    進行個股K線繪製，回傳至於雲端圖床的連結。將顯示包含5MA、20MA及量價關係，起始預設自2020-01-01起迄昨日收盤價。
    :stock :個股代碼(字串)，預設0050。
    :date_from :起始日(字串)，格式為YYYY-MM-DD，預設自2020-01-01起。
    """
    stock = str(stock_or)+".tw"
    df = yf.download(stock, period=period, interval=interval)
    # 抓後面100筆
    if period == 'max':
        df = df.iloc[-100:]
    # print(df)

    return df

# 畫圖
def mpf_bar(df, stock_or, period):
    # 自設版面
    fig = plt.figure(figsize=(24, 16))  # 設定畫布大小(橫,直)
    # 等份切割畫布(直向,橫向,指定圖要放的位置) 假設切割成(2,3,1) 意指切成如2x3的陣列 位置編號[[1,2,3],[4,5,6]] 圖放在1號位置
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xticks(range(0, len(df.index), 30))  # 設定刻度 此為每30筆資料為一格
    # 把日期後的時間刪掉(原始:2022-05-03 00:00:00) 只剩日期(2022-05-03) 由於資料量很多所有日期都顯示會擠在一起 所以只顯示每30天的日期
    if period == 'max':
        convert_date = pd.DataFrame(df.index[::30])["Date"].apply(
            lambda x: x.strftime("%Y-%m-%d"))
        ax.set_xticklabels(convert_date, fontsize=12)  # x座標名稱
    else:
        ax.set_xticklabels(df.index[::30], fontsize=12)
    # 繪製k線圖或稱蠟燭圖 主體(粗)端點代表開盤與收盤價 引線(細)的端點代表最高或最低
    # width 主體寬度  alpha 透明度  在台灣紅色(俗稱上漲 colorup="r")的由上到下:高收開低 綠色(下跌 color="g"):高開收低 (美國顏色相反)
    mpf.candlestick2_ochl(ax, df["Open"], df["Close"], df["High"],
                          df["Low"], width=0.6, colorup="r", colordown="g", alpha=0.9)

    last_date = df.index[-1].strftime("%Y-%m-%d")
    # print(last_date, end = " ")

    plt.title(f"{stock_or} {last_date}前100根k棒")  # 標題名稱
    plt.xlabel("日期")  # x軸標題
    plt.ylabel("價格")  # y軸標題
    # try:
    #     plt.savefig(f"/content/drive/MyDrive/stockhistory_kbar/{stock_or}.png") # 要放在show前面 否則會變空圖
    # except:
    #     pass

    return fig

# 上傳圖檔
def upload_storage_img(source, dstfile, bucketname):
    try:
        client = storage.Client()
        bucket = client.bucket(bucketname)
        blob = bucket.blob(dstfile)
        blob.upload_from_filename(source)
    except:
        print(f'image upload to {bucketname} fail ..')

'''
共用函式: 股票查詢
N =>當下走勢圖
T =>當日K線
P =>預測股價
F =>K線特徵
'''
# 查詢股號當下走勢圖(ex: N2330)
def now_trend_message(text):
    df = stock_data(text[1:5], '1d', '1m')
    if df.empty == False:
        fig = mpf_bar(df, text, '1d')
        fig.savefig(f'{text}.png')
        # print(fig)
        upload_storage_img(f'{text}.png', f'trend/{text}.png', 'stockpd-image')
        os.remove(f'{text}.png')

        # massage = ImageSendMessage(
        #     original_content_url="https://storage.cloud.google.com/stockpd-image/trend/" + text + ".png",
        #     preview_image_url="https://storage.cloud.google.com/stockpd-image/trend/" + text + ".png"
        # )

        # https://storage.googleapis.com/stockpd-image/trend/N2303.png
        massage = ImageSendMessage(
            original_content_url="https://storage.googleapis.com/stockpd-image/trend/" + text + ".png",
            preview_image_url="https://storage.googleapis.com/stockpd-image/trend/" + text + ".png"
        )
    else:
        massage = TextSendMessage("請確認股票是否存在!")

    return massage

# 查詢股號當日K線(ex: T2330)
def trend_message(text):
    df = stock_data(text[1:5], 'max', '1d')
    if df.empty == False:
        fig = mpf_bar(df, text, 'max')
        fig.savefig(f'{text}.png')
        # print(fig)
        upload_storage_img(f'{text}.png', f'trend/{text}.png', 'stockpd-image')
        os.remove(f'{text}.png')

        # massage = ImageSendMessage(
        #     original_content_url="https://storage.cloud.google.com/stockpd-image/trend/" + text + ".png",
        #     preview_image_url="https://storage.cloud.google.com/stockpd-image/trend/" + text + ".png"
        # )

        # https://storage.googleapis.com/stockpd-image/trend/T2303.png
        massage = ImageSendMessage(
            original_content_url="https://storage.googleapis.com/stockpd-image/trend/" + text + ".png",
            preview_image_url="https://storage.googleapis.com/stockpd-image/trend/" + text + ".png"
        )
    else:
        massage = TextSendMessage("請確認股票是否存在!")

    return massage

# 預測股價趨勢(ex: P2330) # 由 GRU模型 改為 Prophet by FB
def predict_message(text, stock_list):
    if text[1:5] in stock_list:
        # massage = ImageSendMessage(
        #     original_content_url="https://storage.googleapis.com/stockpd-image/original/" +
        #     text[1:5] + ".png",
        #     preview_image_url="https://storage.googleapis.com/stockpd-image/original/" +
        #     text[1:5] + ".png"
        # )

        # https://storage.googleapis.com/stockpd-image/prediction/2303_prophet.png
        massage = ImageSendMessage(
            original_content_url="https://storage.googleapis.com/stockpd-image/prediction/" +
                            text[1:5] + "_prophet.png",
            preview_image_url="https://storage.googleapis.com/stockpd-image/prediction/" +
                            text[1:5] + "_prophet.png"
        )
    else:
        massage = TextSendMessage("不在股票表列中,請按股票查詢,確認股票表列!")

    return massage

# 取得K線特徵(ex: F2330)
def feature_message(text, stock_list):
    if text[1:5] in stock_list:
        # massage = ImageSendMessage(
        #     original_content_url="https://storage.cloud.google.com/stockpd-image/prediction/" +
        #     text[1:5] + "_yolov7.png",
        #     preview_image_url="https://storage.cloud.google.com/stockpd-image/prediction/" +
        #     text[1:5] + "_yolov7.png"
        # )

        # https://storage.googleapis.com/stockpd-image/prediction/2303_yolov7.png
        massage = ImageSendMessage(
            original_content_url="https://storage.googleapis.com/stockpd-image/prediction/" +
                            text[1:5] + "_yolov7.png",
            preview_image_url="https://storage.googleapis.com/stockpd-image/prediction/" +
                            text[1:5] + "_yolov7.png"
        )
    else:
        massage = TextSendMessage("不在股票表列中,請按股票查詢,確認股票表列!")

    return massage


# handler收到文字消息時
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if (event.message.text.find('@') != -1):
        line_bot_api.reply_message(
            event.reply_token,
            ticket_message_dict.get(event.message.text)
        )

    # N=>當下走勢圖
    elif (event.message.text.find('N') != -1):
        line_bot_api.reply_message(
            event.reply_token,
            now_trend_message(event.message.text)
        )

    # T=>當日K線
    elif (event.message.text.find('T') != -1):
        line_bot_api.reply_message(
            event.reply_token,
            trend_message(event.message.text)
        )

    # P=>預測股價趨勢
    elif (event.message.text.find('P') != -1):
        line_bot_api.reply_message(
            event.reply_token,
            predict_message(event.message.text, stock_list)
        )

    # F=>K線特徵
    elif (event.message.text.find('F') != -1):
        line_bot_api.reply_message(
            event.reply_token,
            feature_message(event.message.text, stock_list)
        )

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="查無資料，請按股票查詢，選取股票")
        )

# 關注消息處理(當用戶關注時，取得用戶大頭照上傳Storage並新增用戶資料到資料庫)
@handler.add(FollowEvent)
def handle_follow_event(event):
    # 取個資
    line_user_profile = line_bot_api.get_profile(event.source.user_id)
    # 跟line 取回照片(用戶的大頭照)，並放置在本地端
    file_name = line_user_profile.user_id+'.jpg'
    # 下載用戶的大頭照
    urllib.request.urlretrieve(line_user_profile.picture_url, file_name)

    # 把用戶的大頭照上傳到Cloud Storage
    storage_client = storage.Client()
    # 指定桶子名
    bucket_name="stockpd-user"
    # 依用戶ID 當資料夾,大頭照檔名為 user_pic.png
    destination_blob_name = f"{line_user_profile.user_id}/user_pic.png"
    source_file_name = file_name
    # 進行上傳
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    # 設定用戶資料json(把用戶的資料轉成dict)
    # 用戶ID , 用戶大頭照的網址 , 用戶的暱稱 , 用戶的狀態
    user_dict={
        "user_id": line_user_profile.user_id,
        "picture_url": f"https://storage.googleapis.com/{bucket_name}/destination_blob_name",
        "display_name": line_user_profile.display_name,
        "status_message": line_user_profile.status_message
    }
    # 新增到資料庫firestore
    db = firestore.Client()
    # 指定特定表格 line-user , 資料主鍵為 用戶ID
    # doc_ref = db.collection(u'line-user').document(user_dict.get("user_id"))
    doc_ref = db.collection(u'stockpd-user-info').document(user_dict.get("user_id"))
    # 新增整筆資料
    doc_ref.set(user_dict)

    # 請 line_bot_api 回傳消息的給用戶(回傳文字訊息:個資已取)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="歡迎加入~荷包股起來!!")
    )


#主程式
import os
if __name__ == "__main__":
    #port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
