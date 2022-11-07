import yfinance as yf
import pandas as pd
import sys
from google.cloud import storage


def hello_world(request):
	stock_list = ['2303', '2317', '2327', '2330', '2345', '2377', '2395', '2409', '2454', '3037', '3481', '3532', '6415', '8046']
    startDate = '2014-01-01'
    #today = date.today()
	
	def upload_storage(sourcefile, dstfile, bucketname):
		try:
			storage_client = storage.Client()
			bucket = storage_client.bucket(bucketname)
			blob = bucket.blob(dstfile)
			blob.upload_from_filename(sourcefile)
		except:
			print(f'file upload to {bucketname} fail ..')
	 

	for stockid in stockid_list:
		#stockid = stockid.strip()
        data = yf.download(f'{stockid}.Tw', startDate)
        data.drop('Adj Close', axis=1, inplace=True)
        csvfile = data.to_csv()
        print(f'Load {stockid} data done')
		
		# $bucket_name : 須修改為你自己創建的Cloud Storage Bucket
		upload_storage(csvfile, f'stock-data/{stockid}.csv', '$bucket_name)
		print(f'Upload {stockid} data to storage done')