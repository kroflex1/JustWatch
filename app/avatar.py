import boto3
import os
from dotenv import load_dotenv
from app import schemas, crud, errors
from botocore.exceptions import ClientError

load_dotenv()


class AvatarManager:
    __AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    __AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    __BUCKET_NAME_FOR_AVATARS = 'just-watch-avatars'

    @staticmethod
    def upload_avatar(avatar_file, user_id: int):
        session = boto3.session.Session()
        s3 = session.client(
            service_name='s3',
            aws_access_key_id=AvatarManager.__AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AvatarManager.__AWS_SECRET_ACCESS_KEY,
            endpoint_url='https://storage.yandexcloud.net'
        )
        s3.upload_fileobj(avatar_file, AvatarManager.__BUCKET_NAME_FOR_AVATARS, str(user_id))

    @staticmethod
    def get_avatar_url(user_id: int):
        expire = 3600
        session = boto3.session.Session()
        s3 = session.client(
            service_name='s3',
            aws_access_key_id=AvatarManager.__AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AvatarManager.__AWS_SECRET_ACCESS_KEY,
            endpoint_url='https://storage.yandexcloud.net'
        )
        try:
            response = s3.generate_presigned_url('get_object',
                                                 Params={'Bucket': AvatarManager.__BUCKET_NAME_FOR_AVATARS,
                                                         'Key': str(user_id)},
                                                 ExpiresIn=expire)
            return response
        except ClientError:
            return None
