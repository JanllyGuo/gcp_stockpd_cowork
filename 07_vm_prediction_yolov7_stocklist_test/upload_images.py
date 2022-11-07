from google.cloud import storage
import os
import sys

#folderpath = '/home/$account/prediction-test-yolov7'
#sys.path.append(folderpath)

#stocklist = os.path.join(folderpath, 'stock_list.txt')

stocklist = 'stock_list.txt'
stocks = []

with open(stocklist, 'r', encoding='utf-8') as f:
   for line in f.readlines():
     stocks.append(line.strip())

def upload_storage(sourcefile, dstfile, bucketname):
   try:
     storage_client = storage.Client()
     bucket = storage_client.bucket(bucketname)
     blob = bucket.blob(dstfile)
     blob.upload_from_filename(sourcefile)
   except:
     print(f'file upload to {bucketname} fail ..')

for stock in stocks:

#   sourcefile = os.path.join(folderpath, f'runs/detect/{stock}_yolov7.png')
   sourcefile = f'runs/detect/{stock}_yolov7.png'
   bucketname = 'stockpd-image'
   dstfile = f'prediction/{stock}_yolov7.png'


   upload_storage(sourcefile, dstfile, bucketname)
