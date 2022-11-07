import mpl_finance as mpf
import matplotlib.pyplot as plt
import pandas as pd
from google.cloud import storage

# plot kbar pic
def plot_Kbar(data):
    df = data
    # 設定畫布大小(橫,直)
    fig = plt.figure(figsize=(12,6))
    # 等份切割畫布(直向,橫向,指定圖要放的位置) 假設切割成(2,3,1) 意指切成如2x3的陣列 位置編號[[1,2,3],[4,5,6]] 圖放在1號位置  
    ax = fig.add_subplot(1,1,1) 
    # 設定刻度 此為每30筆資料為一格
    ax.set_xticks(range(0,len(df.index),30)) 
    #把日期後的時間刪掉(原始:2022-05-03 00:00:00) 只剩日期(2022-05-03) 由於資料量很多所有日期都顯示會擠在一起 所以只顯示每30天的日期
    convert_date = pd.DataFrame(df.index[::30])["Date"].apply(lambda x: x.strftime("%Y-%m-%d"))
    # x座標名稱
    ax.set_xticklabels(convert_date, fontsize = 12) 
    # 繪製k線圖或稱蠟燭圖 主體(粗)端點代表開盤與收盤價 引線(細)的端點代表最高或最低
    # width 主體寬度  alpha 透明度  在台灣紅色(俗稱上漲 colorup="r")的由上到下:高收開低 綠色(下跌 color="g"):高開收低 (美國顏色相反)
    mpf.candlestick2_ochl(ax,df["Open"],df["Close"],df["High"],df["Low"],width = 0.6, colorup = "r", colordown = "g", alpha = 0.9)
    # 另有參數 rotation = 90 表刻度文字旋轉90度

    last_date = df.index[-1].strftime("%Y-%m-%d")
    print(last_date, end = " ")

    return fig


# upload every day stock data to gcs
def upload_storage_file(source, dstfile, bucketname):
    try:
        client = storage.Client()
        bucket = client.bucket(bucketname)
        blob = bucket.blob(dstfile)
        blob.upload_from_string(source)
    except:
        print(f'file upload to {bucketname} fail ..')

# upload kbar png to gcs
def upload_storage_img(source, dstfile, bucketname):
    try:
        client = storage.Client()
        bucket = client.bucket(bucketname)
        blob = bucket.blob(dstfile)
        blob.upload_from_filename(source)
    except:
        print(f'image upload to {bucketname} fail ..')