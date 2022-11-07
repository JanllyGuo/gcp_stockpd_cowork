from google.cloud import storage
import os

sourcefile = 'runs/detect/exp/2303_2000-06-08_yolov7.png'
bucketname = 'your bucket_name'
dstfile = 'stock-image/2303_2000-06-08_yolov7.png'

def upload_storage(sourcefile, dstfile, bucketname):
   try:
     storage_client = storage.Client()
     bucket = storage_client.bucket(bucketname)
     blob = bucket.blob(dstfile)
     blob.upload_from_filename(sourcefile)
   except:
     print(f'file upload to {bucketname} fail ..')

upload_storage(sourcefile, dstfile, bucketname)