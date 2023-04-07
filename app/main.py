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


def get_auth_user(auth_token: str = Header(None, alias='user-auth-token'),
                  dependencies=[Depends(get_db)]) -> schemas.UserBase:
    if not auth_token:
        raise errors.AuthError
    user_id = authentication.decrypt_token(auth_token)
    user_db = crud.get_user_by_id(user_id=user_id)
    return schemas.UserBase(email=user_db.email, username=user_db.username)


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


@api.method()
def test(number: int = Body()) -> str:
    return str(number + 1)


@api.method(dependencies=[Depends(get_db)])
def register_user(user_data: schemas.UserCreate = Body()) -> str:
    user_db = crud.get_user_by_email(email=user_data.email)
    if user_db:
        raise errors.RegisterError
    crud.create_user(user=user_data)
    return "user registered"


@api.method(dependencies=[Depends(get_db)])
def login_for_access_token(user_data: schemas.UserIn = Body()) -> str:
    user_db = crud.get_user_by_email_and_password(email=user_data.email, password=user_data.password)
    if user_db is None:
        raise errors.AccountNotFound
    access_token = authentication.create_access_token(user_db.id)
    return access_token


app = jsonrpc.API()
app.bind_entrypoint(api)
