import pytest
from fastapi.testclient import TestClient
from app.main import app, get_db
from app import schemas, models, authentication, crud, errors, video
from app.database import PeeweeConnectionState
from contextvars import ContextVar
import peewee

test_db = peewee.SqliteDatabase("test.db", check_same_thread=False)
test_db._state = PeeweeConnectionState()
test_db.connect()
test_db.bind([models.User, models.Video])
test_db.drop_tables([models.User, models.Video])
test_db.create_tables([models.User, models.Video])
test_db.close()

VIDEO_NAME = 'Top 10 cats'
VIDEO_DESCRIPTION = 'The most funny cats'


def override_get_db():
    try:
        test_db.connect()
        yield
    finally:
        if not test_db.is_closed():
            test_db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

USER_EMAIL = "fake_user@mail.ru"
USERNAME = "fake_user"
USER_PASSWORD = "fake_password"
JSON_PRC_BASE_REGISTRATION = {
    "jsonrpc": "2.0",
    "id": 0,
    "method": "register_user",
    "params": {
        "user_data": {
            "email": USER_EMAIL,
            "username": USERNAME,
            "password": USER_PASSWORD
        }
    }
}


def create_author():
    user = schemas.UserCreate(email='test_user@mail.ru', username='test_user_name', password='test_user_password')
    return crud.create_user(user)


def test_upload_video_file_s3():
    author = create_author()
    with open('/tests/static_files/test_video.mp4') as video_file:
        db_video = video.VideoManager.upload_video(video_file, VIDEO_NAME, VIDEO_DESCRIPTION, author.id)
    assert db_video.video_name == VIDEO_NAME