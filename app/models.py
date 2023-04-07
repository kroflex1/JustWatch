from peewee import *
from .database import db


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    email = CharField(unique=True, index=True)
    username = CharField(unique=True, index=True)
    hashed_password = CharField()
    refresh_token = CharField(null=True)
    is_active = BooleanField(default=True)


class Video(BaseModel):
    video_name = CharField(index=True)
    author_id = ForeignKeyField(User, backref="videos")
    number_of_likes = IntegerField()
    number_of_dislikes = IntegerField()
