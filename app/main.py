from fastapi import Depends, Body, Header, UploadFile
import fastapi_jsonrpc as jsonrpc
import logging
from contextlib import asynccontextmanager
from typing import Annotated
from starlette.middleware.cors import CORSMiddleware

from . import crud, schemas, errors, authentication, database, models, video, avatar
from .database import db_state_default

logger = logging.getLogger(__name__)
database.db.connect()
database.db.create_tables(
    [models.User, models.Video, models.Reaction, models.Comment, models.Subscriber, models.Viewer])
database.db.close()


async def reset_db_state():
    database.db._state._state.set(db_state_default.copy())
    database.db._state.reset()


def get_db(db_state=Depends(reset_db_state)):
    try:
        database.db.connect()
        yield
    finally:
        if not database.db.is_closed():
            database.db.close()


async def get_current_user(access_token: str = Header(None, alias='access-token')) -> schemas.User:
    if not access_token:
        raise errors.AccessTokenMissingError
    user_id = authentication.TokenManager.try_get_user_id_from_token(access_token)
    user_db = crud.get_user_by_id(user_id=user_id)
    return user_db


@asynccontextmanager
async def logging_middleware(ctx: jsonrpc.JsonRpcContext):
    logger.info('Request: %r', ctx.raw_request)
    try:
        yield
    finally:
        logger.info('Response: %r', ctx.raw_response)


api = jsonrpc.Entrypoint(
    '/api',
    middlewares=[logging_middleware],
)


@api.method(dependencies=[Depends(get_db)])
def get_new_refresh_and_access_token(refresh_token: str = Header(None, alias='refresh-token')) -> schemas.Tokens:
    if not refresh_token:
        raise errors.RefreshTokenMissingError
    user_id = authentication.TokenManager.try_get_user_id_from_token(refresh_token)
    if user_id is None:
        raise errors.TokenError
    user_db = crud.get_user_by_id(user_id=user_id)
    new_tokens = authentication.TokenManager.create_access_and_refresh_token(user_db.id)
    crud.update_user_refresh_token(user_id, new_tokens.refresh_token)
    return new_tokens


@api.method(dependencies=[Depends(get_db)])
def register_user(user_data: schemas.UserCreate = Body()) -> schemas.Tokens:
    user_db = crud.get_user_by_email(email=user_data.email)
    if user_db:
        raise errors.RegisterError

    user_db = crud.create_user(user=user_data)
    new_tokens = authentication.TokenManager.create_access_and_refresh_token(user_db.id)
    crud.update_user_refresh_token(user_db.id, new_tokens.refresh_token)
    return new_tokens


@api.method(dependencies=[Depends(get_db)])
def login(user_data: schemas.UserInf = Body()) -> schemas.Tokens:
    user_db = crud.get_user_by_email_and_password(email=user_data.email, password=user_data.password)
    if user_db is None:
        raise errors.AccountNotFound

    new_tokens = authentication.TokenManager.create_access_and_refresh_token(user_db.id)
    crud.update_user_refresh_token(user_db.id, new_tokens.refresh_token)
    return new_tokens


@api.method(dependencies=[Depends(get_db)])
def get_current_user_information(user: Annotated[schemas.User, Depends(get_current_user)]) -> schemas.UserBase:
    return schemas.UserBase(email=user.email, username=user.username)


@api.method(dependencies=[Depends(get_db)])
def get_user_profile(user: Annotated[schemas.User, Depends(get_current_user)],
                     user_id: int) -> schemas.UserProfileInformation:
    user_db = models.User.get_by_id(user_id)
    user_videos_db = user_db.videos
    videos_show_inf = []
    for user_video in user_videos_db:
        preview_image_url = video.VideoManager.get_video_image_preview_url(user_video.id)
        author_name = user_db.username
        number_of_views = crud.get_number_of_views(user_video.id)
        videos_show_inf.append(
            schemas.VideoInf(video_name=user_video.video_name, description=user_video.description, id=user_video.id,
                             preview_image_url=preview_image_url, author_name=author_name, author_id=user_id,
                             published_at=user_video.creation_time, number_of_views=number_of_views))
    number_of_subscribers = user_db.subscribers.count()
    number_of_videos = len(videos_show_inf)
    user_avatar_url = avatar.AvatarManager.get_avatar_url(user_id)

    return schemas.UserProfileInformation(username=user.username,
                                          number_of_subscribers=number_of_subscribers,
                                          number_of_videos=number_of_videos,
                                          user_videos=videos_show_inf,
                                          user_avatar_url=user_avatar_url)


@api.method(dependencies=[Depends(get_db)])
def get_all_videos_inf(user: Annotated[schemas.User, Depends(get_current_user)]) -> list[schemas.VideoInf]:
    videos = []
    for video_inf in crud.get_all_videos():
        preview_image_url = video.VideoManager.get_video_image_preview_url(video_inf.id)
        author_name = crud.get_user_by_id(video_inf.author_id).username

        number_of_views = crud.get_number_of_views(video_inf.id)
        videos.append(
            schemas.VideoInf(id=video_inf.id, video_name=video_inf.video_name, description=video_inf.description,
                             preview_image_url=preview_image_url, author_name=author_name,
                             author_id=video_inf.author_id.id,
                             published_at=video_inf.creation_time, number_of_views=number_of_views))
    return videos


@api.method(dependencies=[Depends(get_db)])
def get_video_show_inf_by_id(user: Annotated[schemas.User, Depends(get_current_user)],
                             video_id: int) -> schemas.VideoShow:
    video_db = crud.get_video_by_id(video_id)
    author_id = video_db.author_id.id
    video_name, description = video_db.video_name, video_db.description
    video_url = video.VideoManager.get_video_url_by_id(video_id)
    reactions = crud.get_video_number_of_likes_and_dislikes(video_id)
    user_reaction = crud.get_user_reaction_to_video(user.id, video_id)
    comments = crud.get_comments_show_inf_from_video(video_id)
    number_of_views = crud.get_number_of_views(video_id)
    published_at = video_db.creation_time

    return schemas.VideoShow(video_url=video_url, reactionsInf=reactions, video_name=video_name,
                             description=description, user_reaction=user_reaction, comments=comments,
                             number_of_views=number_of_views, published_at=published_at, author_id=author_id)


@api.method(dependencies=[Depends(get_db)])
def get_user_channel_information(user: Annotated[schemas.User, Depends(get_current_user)],
                                 user_id: int) -> schemas.UserChannelInformation:
    user_db = crud.get_user_by_id(user_id)
    user_avatar_url = avatar.AvatarManager.get_avatar_url(user_id)
    return schemas.UserChannelInformation(username=user_db.username, number_of_subscribers=user_db.subscribers.count(),
                                          user_avatar_url=user_avatar_url)


@api.method()
def get_user_avatar_image(user: Annotated[schemas.User, Depends(get_current_user)], user_id: int) -> str:
    return avatar.AvatarManager.get_avatar_url(user_id)


@api.method(dependencies=[Depends(get_db)])
def watch_video(user: Annotated[schemas.User, Depends(get_current_user)], video_id: int):
    crud.watch_video(user_id=user.id, video_id=video_id)


@api.method(dependencies=[Depends(get_db)])
def rate_video(user: Annotated[schemas.User, Depends(get_current_user)], video_id: int, user_reaction: crud.Reaction):
    crud.rate_video(user_id=user.id, video_id=video_id, user_reaction=user_reaction)


@api.method(dependencies=[Depends(get_db)])
def add_comment_to_video(user: Annotated[schemas.User, Depends(get_current_user)], video_id: int, comment_text: str):
    comment_inf = schemas.CommentCreate(video_id=video_id, author_id=user.id, text=comment_text)
    crud.create_comment(comment_inf)


@api.method(dependencies=[Depends(get_db)])
def get_comments_from_video(user: Annotated[schemas.User, Depends(get_current_user)], video_id: int) -> list[
    schemas.CommentShow]:
    return crud.get_comments_show_inf_from_video(video_id)


@api.method(dependencies=[Depends(get_db)])
def subscribe(user: Annotated[schemas.User, Depends(get_current_user)], author_id: int):
    return crud.subscribe(subscriber_id=user.id, author_id=author_id)


@api.method(dependencies=[Depends(get_db)])
def unsubscribe(user: Annotated[schemas.User, Depends(get_current_user)], author_id: int):
    return crud.unsubscribe(subscriber_id=user.id, author_id=author_id)


@api.method(dependencies=[Depends(get_db)])
def is_subscribed_to_author(user: Annotated[schemas.User, Depends(get_current_user)], author_id: int) -> bool:
    return crud.is_user_subscribed_to_author(user_id=user.id, author_id=author_id)


@api.method(dependencies=[Depends(get_db)])
def get_latest_viewed_videos(user: Annotated[schemas.User, Depends(get_current_user)]) -> list[schemas.VideoInf]:
    videos_db = crud.get_viewed_videos(user.id)
    result = []
    for video_db in videos_db:
        preview_image_url = video.VideoManager.get_video_image_preview_url(video_db.id)
        author_name = crud.get_user_by_id(video_db.author_id.id).username
        number_of_views = crud.get_number_of_views(video_db.id)
        result.append(schemas.VideoInf(video_name=video_db.video_name, description=video_db.description, id=video_db.id,
                                       preview_image_url=preview_image_url, author_name=author_name,  author_id = video_db.author_id.id,
                                       published_at=video_db.creation_time, number_of_views=number_of_views))
    return result


@api.method(dependencies=[Depends(get_db)])
def delete_video(user: Annotated[schemas.User, Depends(get_current_user)], video_id: int):
    video_db = models.Video.get_by_id(video_id)
    if video_db.author_id.id != user.id:
        raise errors.CantDeleteVideo
    crud.delete_video(video_id)
    video.VideoManager.delete_video(video_id)


app = jsonrpc.API()
app.bind_entrypoint(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload-video-file", dependencies=[Depends(get_db)])
async def upload_video_file(user: Annotated[schemas.User, Depends(get_current_user)], video_name: str,
                            video_data: UploadFile,
                            preview_image_data: UploadFile,
                            video_descr: str | None = None,
                            ) -> int:
    if not video_data:
        raise errors.NoFileError
    if video_data.content_type not in ['video/mp4']:
        raise errors.InvalidVideoFormat
    if preview_image_data.content_type not in ['image/jpeg', 'image/png']:
        raise errors.InvalidImageFormat
    db_video = await video.VideoManager().upload_video(video_file=video_data.file,
                                                       video_image_preview=preview_image_data.file,
                                                       video_name=video_name,
                                                       video_description=video_descr, author_id=user.id)
    return int(db_video.id)


@app.post("/api/upload-avatar", dependencies=[Depends(get_db)])
def upload_avatar(user: Annotated[schemas.User, Depends(get_current_user)], avatar_data: UploadFile):
    if not avatar_data:
        raise errors.NoFileError
    if avatar_data.content_type not in ['image/jpeg', 'image/png']:
        raise errors.InvalidImageFormat
    avatar.AvatarManager.upload_avatar(avatar_file=avatar_data.file, user_id=user.id)
