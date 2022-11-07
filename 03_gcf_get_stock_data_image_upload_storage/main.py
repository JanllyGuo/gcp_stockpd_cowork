import yfinance as yf
import pandas as pd
from google.cloud import storage
import mpl_finance as mpf
import matplotlib.pyplot as plt
from os import path, remove
#from datetime import date

# Root path on CF will be /workspace, while on local Windows: C:\
root = path.dirname(path.abspath(__file__))

def hello_world(request):    
    stock_list = ['2303', '2317', '2327', '2330', '2345', '2377', '2395', '2409', '2454', '3037', '3481', '3532', '6415', '8046']
    startDate = '2014-01-01'
    #today = date.today()

    def upload_storage_doc(source, dstfile, bucketname):
        try:
          client = storage.Client()
          bucket = client.bucket(bucketname)
          blob = bucket.blob(dstfile)
          blob.upload_from_string(source)
        except:
          print(f'file upload to {bucketname} fail ..')

    def upload_storage_img(source, dstfile, bucketname):
        try:
          client = storage.Client()
          bucket = client.bucket(bucketname)
          blob = bucket.blob(dstfile)
          blob.upload_from_filename(source)
        except:
          print(f'image upload to {bucketname} fail ..')
    
    def plot_Kbar(data):
        df = data

        fig = plt.figure(figsize=(12,6))  # �]�w�e���j�p(��,��)
        ax = fig.add_subplot(1,1,1) # �������εe��(���V,��V,���w�ϭn�񪺦�m) ���]���Φ�(2,3,1) �N�������p2x3���}�C ��m�s��[[1,2,3],[4,5,6]] �ϩ�b1����m
        ax.set_xticks(range(0,len(df.index),30)) # �]�w��� �����C30����Ƭ��@��
        #�����᪺�ɶ��R��(��l:2022-05-03 00:00:00) �u�Ѥ��(2022-05-03) �ѩ��ƶq�ܦh�Ҧ��������ܷ|���b�@�_ �ҥH�u��ܨC30�Ѫ����
        convert_date = pd.DataFrame(df.index[::30])["Date"].apply(lambda x: x.strftime("%Y-%m-%d"))
        ax.set_xticklabels(convert_date, fontsize = 12) # x�y�ЦW��
        # ø�sk�u�ϩκ������ �D��(��)���I�N��}�L�P���L�� �޽u(��)�����I�N��̰��γ̧C
        # width �D��e��  alpha �z����  �b�x�W����(�U�٤W�� colorup="r")���ѤW��U:�����}�C ���(�U�^ color="g"):���}���C (�����C��ۤ�)
        mpf.candlestick2_ochl(ax,df["Open"],df["Close"],df["High"],df["Low"],width = 0.6, colorup = "r", colordown = "g", alpha = 0.9)
        # �t���Ѽ� rotation = 90 ���פ�r����90��
        return fig

    for stockid in stock_list:
        #stockid = stockid.strip()
        data = yf.download(f'{stockid}.Tw', startDate)
        data.drop('Adj Close', axis=1, inplace=True)
        csvfile = data.to_csv()
        print(f'Load {stockid} data done')

        upload_storage_doc(csvfile, f'stock-data/{stockid}.csv', 'your bucket name')
        print(f'Upload {stockid} data to storage done')

        fig = plot_Kbar(data[-100:])
        
        file_path = '/tmp/' + f'{stockid}.png'
        file_path = path.join(root, file_path)

        fig.savefig(file_path)
        plt.close(fig)
        # If file is a binary, we rather use 'wb' instead of 'w'
        #with open(file_path, 'wb') as file:
        #  file.write(fig)
        
        upload_storage_img(file_path, f'stock-image/{stockid}.png', 'your bucket name')
        print(f'Upload {stockid} image to storage done')
        remove(file_path)
