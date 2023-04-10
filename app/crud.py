from . import models, schemas, errors
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_id(user_id: int):
    return models.User.filter(models.User.id == user_id).first()


def get_user_by_email(email: str):
    return models.User.filter(models.User.email == email).first()


def get_user_by_email_and_password(email: str, password: str):
    db_user = get_user_by_email(email)
    if db_user is not None and pwd_context.verify(password, db_user.hashed_password):
        return db_user


def create_user(user: schemas.UserCreate):
    if user.username == '' or user.email == '' or user.password == '':
        raise errors.AuthError
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    try:
        db_user.save()
    except:
        raise errors.RegisterError
    else:
        return db_user


def delete_user_by_id(user_id: int):
    q = models.User.delete().where(models.User.id == user_id)
    q.execute()


def delete_user_by_email(email: str):
    q = models.User.delete().where(models.User.email == email)
    q.execute()


def update_user_refresh_token(user_id: int, refresh_token: str):
    q = (models.User.update({models.User.refresh_token: refresh_token}).where(models.User.id == user_id))
    q.execute()


def create_video(video_base: schemas.VideoBase, user_id: int):
    db_video = models.Video(video_name=video_base.video_name, author_id=user_id, description=video_base.description)
    db_video.save()
    return db_video


def get_video_by_id(video_id: int):
    return models.Video.filter(models.Video == video_id).first()


def delete_video(video_id: int):
    q = models.Video.delete().where(models.Video.id == video_id)
    q.execute()
