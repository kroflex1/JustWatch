import pytest

from app import schemas, models, crud, errors, authentication
from app.database import PeeweeConnectionState
import peewee

test_db = peewee.SqliteDatabase("test.db", check_same_thread=False)
test_db._state = PeeweeConnectionState()
test_db.connect()
test_db.bind([models.User, models.Video])
test_db.drop_tables([models.User, models.Video])
test_db.create_tables([models.User, models.Video])
test_db.close()

USER_EMAIL = 'fake_user@mail.ru'
USERNAME = 'fake_user'
USER_PASSWORD = 'fake_password'


def test_create_user():
    user = schemas.UserCreate(email=USER_EMAIL, username=USERNAME, password=USER_PASSWORD)
    user_db = crud.create_user(user)
    assert user_db.email == USER_EMAIL
    assert user_db.username == USERNAME
    crud.delete_user_by_email(USER_EMAIL)


@pytest.mark.parametrize("email, username, password", [('', 'some_name', 'some_password'),
                                                       ('', '', 'some_password'),
                                                       ('', '', ''),
                                                       ('some_email', '', '')])
def test_create_empty_user(email, username, password):
    user = schemas.UserCreate(email=email, username=username, password=password)
    with pytest.raises(errors.AuthError):
        crud.create_user(user)


def test_take_user_by_email():
    user = schemas.UserCreate(email=USER_EMAIL, username=USERNAME, password=USER_PASSWORD)
    crud.create_user(user)
    user_db = crud.get_user_by_email(USER_EMAIL)
    assert user_db.email == USER_EMAIL
    assert user_db.username == USERNAME
    crud.delete_user_by_email(USER_EMAIL)


def test_take_user_by_email_and_password():
    user = schemas.UserCreate(email=USER_EMAIL, username=USERNAME, password=USER_PASSWORD)
    crud.create_user(user)
    user_db = crud.get_user_by_email_and_password(USER_EMAIL, USER_PASSWORD)
    assert user_db.email == USER_EMAIL
    assert user_db.username == USERNAME
    crud.delete_user_by_email(USER_EMAIL)


def test_update_refresh_token():
    user = schemas.UserCreate(email=USER_EMAIL, username=USERNAME, password=USER_PASSWORD)
    user_db = crud.create_user(user)
    fake_refresh_token = 'fake_refresh'
    crud.update_user_refresh_token(user_db.id, refresh_token=fake_refresh_token)
    user_db = crud.get_user_by_email(USER_EMAIL)
    assert user_db.refresh_token == fake_refresh_token
    crud.delete_user_by_email(USER_EMAIL)


def test_create_identical_users():
    first_user = schemas.UserCreate(email=USER_EMAIL, username=USERNAME, password=USER_PASSWORD)
    second_user = schemas.UserCreate(email=USER_EMAIL, username=USERNAME, password=USER_PASSWORD)
    crud.create_user(first_user)
    with pytest.raises(errors.RegisterError):
        crud.create_user(second_user)
