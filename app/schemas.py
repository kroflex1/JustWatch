from typing import Any, List

import peewee
from pydantic import BaseModel, Field
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
    email: str = Field(example="supercat@gamil.com")
    username: str = Field(example="superCat228")


class UserCreate(UserBase):
    password: str = Field(example="superPassword")


class UserIn(BaseModel):
    email: str = Field(example="supercat@gamil.com")
    password: str = Field(example="superPassword")


class User(UserBase):
    id: int
    is_active: bool
    videos: List[Video] = []

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class Tokens(BaseModel):
    access_token: str = Field(example="eyJhbGciOiJIU.eyJleHAiOiIxMjM0NTY3.-Wp-D4EWy79DFM")
    refresh_token: str = Field("R5cCI6Ikp.eyJleHAcl9pZCI6MX0.AIdrrnGpoz79DFM")
