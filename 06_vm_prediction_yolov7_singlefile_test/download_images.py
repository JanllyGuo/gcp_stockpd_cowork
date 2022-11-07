from google.cloud import storage
import os

dstfolder = 'test'

if not os.path.isdir(dstfolder):
    os.mkdir(dstfolder)
    

sourcefile = 'stock-image/2303_2000-06-08.png'
bucketname = 'your bucket_name'
dstfile = os.path.join(dstfolder, '2303_2000-06-08.png')


def download_storage(sourcefile, dstfile, bucketname):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucketname)
        blob = bucket.blob(sourcefile)
        blob.download_to_filename(os.getcwd() + "/" + dstfile)
    except:
        print(f'file download from {bucketname} fail ..')


download_storage(sourcefile, dstfile, bucketname)
