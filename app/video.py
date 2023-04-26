import boto3
import os
from dotenv import load_dotenv
from app import schemas, crud, errors
from botocore.exceptions import ClientError

load_dotenv()


class VideoManager:
    __AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    __AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    __BUCKET_NAME = 'just-watch-videos'

    @staticmethod
    def upload_video(video_file, video_name: str, video_description: str, author_id: int):
        if video_name == '':
            raise errors.VideoNameEmptyError
        video_base = schemas.VideoCreate(video_name=video_name, description=video_description)
        db_video = crud.create_video(video_base, author_id)
        session = boto3.session.Session()
        s3 = session.client(
            service_name='s3',
            aws_access_key_id=VideoManager.__AWS_ACCESS_KEY_ID,
            aws_secret_access_key=VideoManager.__AWS_SECRET_ACCESS_KEY,
            endpoint_url='https://storage.yandexcloud.net'
        )
        s3.upload_fileobj(video_file, VideoManager.__BUCKET_NAME, str(db_video.id))
        return db_video

    @staticmethod
    def get_video_url_by_id(video_id: int):
        expire = 3600
        session = boto3.session.Session()
        s3 = session.client(
            service_name='s3',
            aws_access_key_id=VideoManager.__AWS_ACCESS_KEY_ID,
            aws_secret_access_key=VideoManager.__AWS_SECRET_ACCESS_KEY,
            endpoint_url='https://storage.yandexcloud.net'
        )
        try:
            response = s3.generate_presigned_url('get_object',
                                                 Params={'Bucket': VideoManager.__BUCKET_NAME,
                                                         'Key': str(video_id)},
                                                 ExpiresIn=expire)
        except ClientError:
            raise errors.VideoNotExist
        return response
