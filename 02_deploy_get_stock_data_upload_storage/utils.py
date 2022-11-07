from google.cloud import storage

def upload_storage(sourcefile, dstfile, bucketname):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucketname)
        blob = bucket.blob(dstfile)
        blob.upload_from_filename(sourcefile)
    except:
        print(f'file upload to {bucketname} fail ..')

