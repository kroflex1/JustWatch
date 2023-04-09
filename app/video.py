import boto3
import os
from dotenv import load_dotenv
from app import schemas, crud

load_dotenv()


class VideoManager:
    def __init__(self):
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    def upload_video(self, video_file, video_inf: schemas.VideoBase, author_id: int):
        # db_video = crud.create_video(video_inf, author_id)
        session = boto3.session.Session()
        s3 = session.client(
            service_name='s3',
            aws_access_key_id='YCAJEeYG1D6LReMYAb_-rfxsk',
            aws_secret_access_key='YCPEVLefcjwYuFKKosXR9yGE7wntkyboWAJfBbMh',
            endpoint_url='https://storage.yandexcloud.net'
        )
        s3.upload_fileobj(video_file, 'justwatchvideos', 'test_video')

    def __create_video_key(self, video_id: int):
        return f'{video_id}'
