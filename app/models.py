from peewee import *
from .database import db
import datetime


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
    description = CharField(default='')
    creation_time = DateTimeField(default=datetime.datetime.now)
    number_of_likes = IntegerField(default=0)
    number_of_dislikes = IntegerField(default=0)
