import os
import pandas as pd
import yfinance as yf
from flask import Flask
# 載入共用函式
import utils

app = Flask(__name__)

@app.route("/")
def hello_world():
    # name = os.environ.get("NAME", "World")
    # return "Hello {}!".format(name)

    # Date: 2022-10-28
    # Source Code: upload_data_image.y
    stock_list = ['2303', '2317', '2327', '2330', '2345', '2377', '2395', '2409', '2454', '3037', '3481', '3532', '6415', '8046']
    startDate = '2014-01-01'
    for stockid in stock_list:
        data = yf.download(f'{stockid}.Tw', startDate)
        data.drop('Adj Close', axis=1, inplace=True)
        csvfile = data.to_csv()
        print(f'Load {stockid} data done')
        # upload stock csv
        utils.upload_storage_file(csvfile, f'{stockid}.csv', 'stockpd-data')
        # plot kbar
        fig = utils.plot_Kbar(data[-100:])
        fig.savefig(f'{stockid}.png')
        # upload kbar png
        utils.upload_storage_img(f'{stockid}.png', f'original/{stockid}.png', 'stockpd-image')
        print(f'Upload {stockid} data to storage done')

    return "Upload stock data and image to storage done!"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))