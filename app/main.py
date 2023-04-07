from fastapi import Depends, Body, Header
import fastapi_jsonrpc as jsonrpc
import logging
from contextlib import asynccontextmanager

from . import crud, schemas, errors, authentication, database, models
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


def get_auth_user(access_token: str = Header(None, alias='access-token'),
                  dependencies=[Depends(get_db)]) -> schemas.UserBase:
    if not access_token:
        raise errors.AuthError
    user_id = authentication.TokenManager.decrypt_token(access_token)
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
        raise errors.AuthError
    user_id = authentication.TokenManager.decrypt_token(refresh_token)
    user_db = crud.get_user_by_id(user_id=user_id)
    if user_db.refresh_token != refresh_token:
        raise errors.AuthError
    tokens = authentication.TokenManager.create_access_and_refresh_token(user_db.id)
    crud.update_user_refresh_token(user_id, tokens.refresh_token)
    return tokens


@api.method(dependencies=[Depends(get_db)])
def register_user(user_data: schemas.UserCreate = Body()) -> schemas.Tokens:
    user_db = crud.get_user_by_email(email=user_data.email)
    if user_db:
        raise errors.RegisterError
    user_db = crud.create_user(user=user_data)
    tokens = authentication.TokenManager.create_access_and_refresh_token(user_db.id)
    crud.update_user_refresh_token(user_db.id, tokens.refresh_token)
    return tokens


@api.method(dependencies=[Depends(get_db)])
def login(user_data: schemas.UserIn = Body()) -> schemas.Tokens:
    user_db = crud.get_user_by_email_and_password(email=user_data.email, password=user_data.password)
    if user_db is None:
        raise errors.AccountNotFound
    tokens = authentication.TokenManager.create_access_and_refresh_token(user_db.id)
    crud.update_user_refresh_token(user_db.id, tokens.refresh_token)
    return tokens


app = jsonrpc.API()
app.bind_entrypoint(api)
