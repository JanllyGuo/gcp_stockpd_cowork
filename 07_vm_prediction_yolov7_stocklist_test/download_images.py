from google.cloud import storage
import os
import sys

#folderpath = '/home/$account/prediction-test-yolov7'
#sys.path.append(folderpath)

#dstfolder = os.path.join(folderpath, 'originalimages')
dstfolder = 'originalimages'

if not os.path.isdir(dstfolder):
    os.mkdir(dstfolder)

stocks = []
#stocklist = os.path.join(folderpath, 'stock_list.txt')
stocklist = 'stock_list.txt'

with open(stocklist, 'r', encoding='utf-8') as f:
   for line in f.readlines():
     stocks.append(line.strip())

def download_storage(sourcefile, dstfile, bucketname):
   try:
     storage_client = storage.Client()
     bucket = storage_client.bucket(bucketname)
     blob = bucket.blob(sourcefile)
     blob.download_to_filename(dstfile)
   except:
     print(f'file download from {bucketname} fail ..')


for stock in stocks:
   sourcefile = f'original/{stock}.png'
   bucketname = 'stockpd-image'
   dstfile = os.path.join(dstfolder, f'{stock}.png')

   download_storage(sourcefile, dstfile, bucketname)
