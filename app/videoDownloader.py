import boto3
import os
from dotenv import load_dotenv

load_dotenv()


class VideoDownloader:
    def __init__(self):
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    def download_video(self):
        session = boto3.session.Session()
        s3 = session.client(
            service_name='s3',
            aws_access_key_id='YCAJEeYG1D6LReMYAb_-rfxsk',
            aws_secret_access_key='YCPEVLefcjwYuFKKosXR9yGE7wntkyboWAJfBbMh',
            endpoint_url='https://storage.yandexcloud.net'
        )
        with open('videoDownloader.py', 'rb') as data:
            s3.upload_fileobj(data, 'justwatchvideos', 'test_video')

    def download_test(self):
        session = boto3.session.Session()
        s3 = session.client(
            service_name='s3',
            aws_access_key_id='YCAJEeYG1D6LReMYAb_-rfxsk',
            aws_secret_access_key='YCPEVLefcjwYuFKKosXR9yGE7wntkyboWAJfBbMh',
            endpoint_url='https://storage.yandexcloud.net'
        )
        s3.put_object(Bucket='justwatchvideos', Key='object_name', Body='TEST', StorageClass='COLD')


x = VideoDownloader()
x.download_video()
