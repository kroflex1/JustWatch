import pytest
from fastapi.testclient import TestClient
from app.main import app, get_db
from app import schemas, models, authentication, crud, errors, video
from app.database import PeeweeConnectionState
from datetime import datetime, timedelta
import peewee

test_db = peewee.SqliteDatabase("test.db", check_same_thread=False)
test_db._state = PeeweeConnectionState()
test_db.connect()
test_db.bind([models.User, models.Video])
test_db.drop_tables([models.User, models.Video])
test_db.create_tables([models.User, models.Video])
test_db.close()


def override_get_db():
    try:
        test_db.connect()
        yield
    finally:
        if not test_db.is_closed():
            test_db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

author = crud.create_user(
    schemas.UserCreate(email='test_user@mail.ru', username='test_user_name', password='test_user_password'))
VIDEO_NAME = 'Top 10 cats'
VIDEO_DESCRIPTION = 'The most funny cats'


def test_upload_video_file_s3():
    with open('static_files/test_video.mp4', 'rb') as video_file:
        db_video = video.VideoManager.upload_video(video_file, VIDEO_NAME, VIDEO_DESCRIPTION, author.id)
    assert db_video.video_name == VIDEO_NAME


def test_upload_video_api():
    author_token = authentication.TokenManager.create_token(author.id, timedelta(minutes=15))
    with open('static_files/test_video.mp4', 'rb') as video_file:
        response = client.post(
            f"/upload-video-file/?video_name={VIDEO_NAME}&video_descr={VIDEO_DESCRIPTION}",
            headers={"access-token": author_token},
            json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
            files={"video_file": video_file}
        )
