from fastapi import Depends, Body, Header, UploadFile
import fastapi_jsonrpc as jsonrpc
import logging
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware

from . import crud, schemas, errors, authentication, database, models, video
from .database import db_state_default

logger = logging.getLogger(__name__)
database.db.connect()
database.db.create_tables([models.User, models.Video, models.Reaction])
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
def login(user_data: schemas.UserIn = Body()) -> schemas.Tokens:
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
def get_all_videos_inf(user: Annotated[schemas.User, Depends(get_current_user)]) -> list[schemas.VideoInf]:
    videos = []
    for video_inf in crud.get_all_videos():
        videos.append(
            schemas.VideoInf(id=video_inf.id, video_name=video_inf.video_name, description=video_inf.description))
    return videos


@api.method(dependencies=[Depends(get_db)])
def get_video_show_inf_by_id(user: Annotated[schemas.User, Depends(get_current_user)],
                             video_id: int) -> schemas.VideoShow:
    video_db = crud.get_video_by_id(video_id)
    video_name, description = video_db.video_name, video_db.description
    video_url = video.VideoManager.get_video_url_by_id(video_id)
    reactions = crud.get_video_number_of_likes_and_dislikes(video_id)
    return schemas.VideoShow(video_url=video_url, reactionsInf=reactions, video_name=video_name, description=description)


app = jsonrpc.API()
app.bind_entrypoint(api)

origins = ["http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload-video-file", dependencies=[Depends(get_db)])
async def upload_video_file(user: Annotated[schemas.User, Depends(get_current_user)], video_name: str,
                            video_descr: str | None = None,
                            video_data: UploadFile | None = None) -> int:
    if not video_data:
        raise errors.NoFileError
    db_video = video.VideoManager().upload_video(video_data.file, video_name, video_descr, user.id)
    return int(db_video.id)
