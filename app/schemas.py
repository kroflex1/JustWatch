from typing import Any, List

import peewee
from pydantic import BaseModel
from pydantic.utils import GetterDict


class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):
            return list(res)
        return res


class VideoBase(BaseModel):
    video_name: str
    number_of_likes: int
    number_of_dislikes: int


class Video(VideoBase):
    author_id: int

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class UserBase(BaseModel):
    email: str
    username: str


class UserIn(BaseModel):
    email: str
    password: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    videos: List[Video] = []

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class Token(BaseModel):
    access_token: str
    token_type: str
