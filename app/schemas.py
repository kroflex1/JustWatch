from typing import Any, List
from datetime import datetime

import peewee
from pydantic import BaseModel, Field
from pydantic.utils import GetterDict


class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        res = getattr(self._obj, key, default)
        if isinstance(res, peewee.ModelSelect):
            return list(res)
        return res


class VideoReactionsInf(BaseModel):
    number_of_likes: int = Field(example=537)
    number_of_dislikes: int = Field(example=136)


class CommentCreate(BaseModel):
    video_id: int
    author_id: int
    text: str = Field(example='I like this video')


class CommentShow(BaseModel):
    author_name: str = Field(example='Kroflex')
    text: str = Field(example='I like this video')
    published_at: datetime = Field(example='2008-09-15T15:53:00+05:00')


class VideoCreate(BaseModel):
    video_name: str = Field(example="Top 10 cats")
    description: str = Field(example="Videos about the funniest cats")


class VideoInf(VideoCreate):
    id: int = Field(example=1)
    preview_image_url: str | None
    author_name: str = Field(example="SuperCat")
    author_id: int = Field(example = "1")
    published_at: datetime = Field(example='2008-09-15T15:53:00+05:00')
    number_of_views: int = Field(example='3412')


class VideoShow(VideoCreate):
    video_url: str = Field()
    author_id: int = Field(example=1)
    reactionsInf: VideoReactionsInf
    comments: list[CommentShow]
    user_reaction: str = Field(example='like')
    published_at: datetime = Field(example='2008-09-15T15:53:00+05:00')
    number_of_views: int = Field(example='3412')


class Video(VideoInf):
    author_id: int = Field(example=523)
    number_of_likes: int = Field(example=11)
    number_of_dislikes: int = Field(example=6)
    creation_time: datetime
    reactions: List[VideoReactionsInf]

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class UserBase(BaseModel):
    email: str = Field(example="supercat@gamil.com")
    username: str = Field(example="superCat228")


class UserCreate(UserBase):
    password: str = Field(example="superPassword")


class UserInf(BaseModel):
    email: str = Field(example="supercat@gamil.com")
    password: str = Field(example="superPassword")


class UserChannelInformation(BaseModel):
    username: str = Field(example="SuperCat")
    number_of_subscribers: int = Field(example=245)
    user_avatar_url: str


class UserProfileInformation(BaseModel):
    username: str = Field(example="superCar")
    number_of_subscribers: int = Field(example=245)
    number_of_videos: int = Field(example=21)
    user_videos: list[VideoInf]
    user_avatar_url: str


class User(UserBase):
    id: int
    is_active: bool
    videos: List[Video] = []

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class Tokens(BaseModel):
    access_token: str = Field(example="eyJhbGciOiJIU.eyJleHAiOiIxMjM0NTY3.-Wp-D4EWy79DFM")
    refresh_token: str = Field(example="R5cCI6Ikp.eyJleHAcl9pZCI6MX0.AIdrrnGpoz79DFM")
