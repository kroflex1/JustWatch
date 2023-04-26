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
    description = TextField(default='')
    creation_time = DateTimeField(default=datetime.datetime.now)


class Reaction(BaseModel):
    video_id = ForeignKeyField(Video, backref='reactions')
    user_id = ForeignKeyField(User, backref='reactions')
    is_like = BooleanField(default=False)
    is_dislike = BooleanField(default=False)

    class Meta:
        primary_key = CompositeKey('video_id', 'user_id')
