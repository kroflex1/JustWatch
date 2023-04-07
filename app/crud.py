from . import models, schemas
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
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db_user.save()
    return db_user


def update_user_refresh_token(user_id: int, refresh_token: str):
    q = (models.User.update({models.User.refresh_token: refresh_token}).where(models.User.id == user_id))
    q.execute()
