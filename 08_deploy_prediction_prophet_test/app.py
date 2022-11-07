import os
from google.cloud import storage
from prophet import Prophet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
from flask import Flask
import warnings
warnings.filterwarnings('ignore')

from utils import download_storage, upload_storage
from models import create_prophet_model, remove_weekends

# 建立日誌紀錄設定檔
# https://googleapis.dev/python/logging/latest/stdlib-usage.html
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler

client = google.cloud.logging.Client()

# 建立line event log，用來記錄line event
bot_event_handler = CloudLoggingHandler(client,name="prophet_event")
bot_event_logger=logging.getLogger('prophet_event')
bot_event_logger.setLevel(logging.INFO)
bot_event_logger.addHandler(bot_event_handler)

app = Flask(__name__)

# storage bucket name
# common_variable = True
# if common_variable: 
#     bucket_name = os.environ['USER_INFO_GS_BUCKET_NAME']
# else:
#     bucket_name = 'brianlin-test-only'

download_bucket = 'stockpd-data'
upload_bucket = 'stockpd-image'

def plot_stock_and_future(data, forecast, history, days, stockid):
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 18))
    #plt.figure(figsize=(14, 10))
    ax1.plot(data['ds'][-history:], data['y'][-history:], 'ko-', linewidth = 1.4, alpha = 0.8, ms = 1.8, label = 'Real')
    ax1.plot(forecast['ds'][-(history+days):], forecast['yhat'][-(history+days):], 'forestgreen',linewidth = 2.4, label = 'Prediction')
    ax1.fill_between(forecast['ds'][-(history+days):], forecast['yhat_upper'][-(history+days):], forecast['yhat_lower'][-(history+days):], alpha = 0.3, 
                        facecolor = 'g', edgecolor = 'k', linewidth = 1.4, label = 'Confidence Interval')
    ax1.legend(loc = 2, prop={'size': 10})
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price $') 
    ax1.grid(linewidth=0.6, alpha = 0.6)
    ax1.set_title(f'{stockid} Real vs Prediction')
    # plt.close()
    # plt.show()

    prediction = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']][-days:]
    prediction = remove_weekends(prediction)
    # Calculate whether increase or not
    prediction['diff'] = prediction['yhat'].diff()

    prediction = prediction.dropna()

    # Find the prediction direction and create separate dataframes
    prediction['direction'] = (prediction['diff'] > 0) * 1

    # Rename the columns for presentation
    prediction = prediction.rename(columns={'ds': 'Date', 'yhat': 'estimate', 'diff': 'change', 
                                            'yhat_upper': 'upper', 'yhat_lower': 'lower'})

    prediction_increase = prediction[prediction['direction'] == 1]
    prediction_decrease = prediction[prediction['direction'] == 0]

    # Plot the estimates
    ax2.plot(prediction_increase['Date'], prediction_increase['estimate'], 'r^', ms = 12, label = 'Pred. Increase')
    ax2.plot(prediction_decrease['Date'], prediction_decrease['estimate'], 'gv', ms = 12, label = 'Pred. Decrease')

    # Plot errorbars
    ax2.errorbar(prediction['Date'].dt.to_pydatetime(), prediction['estimate'], 
                yerr = prediction['upper'] - prediction['lower'], 
                capthick=1.4, color = 'k',linewidth = 2,
                ecolor='darkblue', capsize = 4, elinewidth = 1, label = 'Pred with Range')

    # Plot formatting
    ax2.legend(loc = 2, prop={'size': 10})
    ax2.tick_params('x', labelrotation=45)
    ax2.set_ylabel('Predicted Stock Price')
    ax2.set_xlabel('Date')
    ax2.set_title(f'Predictions for {stockid}')
    ax2.grid(linewidth=0.6, alpha = 0.6)
    
    return fig

# main
@app.route('/call')
def call():
    history = 300                                 # 要顯示的歷史股價
    days = 60                                     # 預測未來天數
    #stockid = '2303'
    # 讀取股票列表
    stocklist = []
    with open('stock_list.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            stocklist.append(line.strip())

    for stockid in stocklist:
        download_storage(f'{stockid}.csv', f'stockData/{stockid}.csv', download_bucket)
        df = pd.read_csv(f'stockData/{stockid}.csv')
        data = df[['Date', 'Close']]
        data.columns = ['ds', 'y']
        data['ds'] = pd.to_datetime(data['ds'])
        data['ds'] = data['ds'].dt.tz_localize(None)

        model = create_prophet_model(data)
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)

        fig = plot_stock_and_future(data, forecast, history, days, stockid)
        fig.savefig(f'stockPred/{stockid}.png')

        upload_storage(f'stockPred/{stockid}.png', f'prediction/{stockid}_prophet.png', upload_bucket)

    return 'OK'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))