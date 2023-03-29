from fastapi import Depends,  Body, Header
import fastapi_jsonrpc as jsonrpc
import logging
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from . import crud, models, schemas, errors, authentication
from .database import SessionLocal, engine

logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_auth_user(auth_token: str = Header(None, alias='user-auth-token'),
                  db: Session = Depends(get_db)) -> schemas.UserBase:
    if not auth_token:
        raise errors.AuthError
    user_id = authentication.decrypt_token(auth_token)
    user_db = crud.get_user_by_id(db=db, user_id=user_id)
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

models.Base.metadata.create_all(bind=engine)

@api.method()
def test(number: int = Body()) -> str:
    return str(number + 1)


@api.method()
def register_user(user_data: schemas.UserCreate = Body(), db: Session = Depends(get_db)) -> str:
    user_db = crud.get_user_by_email(db=db, email=user_data.email)
    if user_db:
        raise errors.RegisterError
    crud.create_user(db=db, user=user_data)
    return "user registered"


@api.method()
def login_for_access_token(user_data: schemas.UserIn = Body(), db: Session = Depends(get_db)) -> str:
    user_db = crud.get_user_by_email(db=db, email=user_data.email)
    if user_db is None:
        raise errors.AccountNotFound
    access_token = authentication.create_access_token(user_db.id)
    return access_token


app = jsonrpc.API()
app.bind_entrypoint(api)
