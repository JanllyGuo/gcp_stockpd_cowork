import os
from flask import Flask
# 
import sys
from datetime import date
import yfinance as yf
import pandas as pd
from utils import upload_storage


app = Flask(__name__)

@app.route("/")
def hello_world():
    # name = os.environ.get("NAME", "World")
    # return "Hello {}!".format(name)
    
    with open('stock_list.txt', 'r', encoding='utf-8') as f:
	    stockid_list = f.readlines()

    startDate = '2014-01-01'
    today = date.today()

    for stockid in stockid_list:
        stockid = stockid.strip()
        data = yf.download(f'{stockid}.Tw', startDate)
        data.drop('Adj Close', axis=1, inplace=True)
        data.to_csv(f'stock_data/{stockid}.csv')
        print(f'Load {stockid} data done')

        upload_storage(f'stock_data/{stockid}.csv', f'stock-data/{stockid}_{today}.csv', 'your bucket name')
        print(f'Upload {stockid} data to storage done')
    
    return "Upload data to storage done!"



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))