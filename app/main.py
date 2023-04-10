from fastapi import Depends, Body, Header, UploadFile
import fastapi_jsonrpc as jsonrpc
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from . import crud, schemas, errors, authentication, database, models, video
from .database import db_state_default

logger = logging.getLogger(__name__)
database.db.connect()
database.db.create_tables([models.User, models.Video])
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
    user_db = crud.get_user_by_id(user_id=user_id)
    if user_db.refresh_token != refresh_token:
        raise errors.AuthError

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


app = jsonrpc.API()
app.bind_entrypoint(api)


@app.post("/upload-video-file", dependencies=[Depends(get_db)])
async def upload_video_file(user: Annotated[schemas.User, Depends(get_current_user)], video_name: str,
                            video_descr: str | None = None,
                            data: UploadFile | None = None) -> int:
    if not data:
        raise errors.NoFileError
    db_video = video.VideoManager().upload_video(data.file, video_name, video_descr, user.id)
    return int(db_video.id)
