import pytest
from fastapi.testclient import TestClient
from app.main import app, get_db
from app import schemas, models, authentication, crud, errors
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

JSON_PRC_BASE_LOGIN = {
    "jsonrpc": "2.0",
    "id": 0,
    "method": "login",
    "params": {
        "user_data": {
            "email": USER_EMAIL,
            "username": USERNAME,
            "password": USER_PASSWORD
        }
    }
}


def test_user_created_after_request():
    json_rpc = JSON_PRC_BASE_REGISTRATION.copy()
    response = client.post("/api", json=json_rpc)
    user_db = crud.get_user_by_email(USER_EMAIL)
    assert user_db.email == USER_EMAIL
    assert user_db.username == USERNAME
    test_db.drop_tables([models.User, models.Video])
    test_db.create_tables([models.User, models.Video])


def test_create_tokens_after_registration():
    json_rpc = JSON_PRC_BASE_REGISTRATION.copy()
    response = client.post("/api", json=json_rpc)
    data = response.json()["result"]
    access_token = data['access_token']
    refresh_token = data['refresh_token']
    assert access_token != ''
    assert refresh_token != ''
    test_db.drop_tables([models.User, models.Video])
    test_db.create_tables([models.User, models.Video])


def test_register_identical_users():
    json_rpc = JSON_PRC_BASE_REGISTRATION.copy()
    response = client.post("/api", json=json_rpc)
    with pytest.raises(errors.RegisterError):
        client.post("/api", json=json_rpc)


def test_user_login():
    response = client.post("/api", json=JSON_PRC_BASE_LOGIN)
    assert response.json()['result']['access_token']
    assert response.json()['result']['refresh_token']
    test_db.drop_tables([models.User, models.Video])
    test_db.create_tables([models.User, models.Video])
