from google.cloud import storage

# 下載檔案到 storage
def download_storage(sourcefile, dstfile, bucketname):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucketname)
        blob = bucket.blob(sourcefile)
        blob.download_to_filename(dstfile)
    except:
        print(f'file download from {bucketname} fail ..')

# 上傳檔案到 storage
def upload_storage(sourcefile, dstfile, bucketname):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucketname)
        blob = bucket.blob(dstfile)
        blob.upload_from_filename(sourcefile)
    except:
        print(f'file upload to {bucketname} fail ..')

