import os #import the os module
from google.cloud import storage #import the storage module

#Storage module is going to look at this environment to variable path and locate the service account file.
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'ServiceKey_GoogleCloud.json'

storage_client = storage.Client()
"""
Create a bucket 
"""
#bucket_name = "dev_data_bucket"
#bucket = storage_client.bucket(bucket_name)
#bucket.location = 'US'
#bucket = storage_client.create_bucket(bucket)

"""
Print bucket detail
"""
#vars(bucket)

"""
Accessing a specific bucket
"""

#my_bucket = storage_client.get_bucket('dev_data_bucket')
#vars(my_bucket)

"""
Upload Files
"""
def upload_to_bucket(blob_name, file_path, bucket_name):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_file_name(file_path)
        return True
    except Exception as e:
        print(e)
        return

file_path = r'C:\Users\Alejandro Sanchez\Documents\GitHub\Developer-Beta-Tester-Webapp\files_to_upload'
upload_to_bucket('FileUpload1', os.path.join(file_path, 'HelloWorld.txt'), 'dev_data_bucket')

# Creating a new directory
upload_to_bucket('/newFolder1/FileUpload1', os.path.join(file_path, 'HelloWorld.txt'), 'dev_data_bucket')