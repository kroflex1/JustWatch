import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from . import errors, schemas




class TokenManager:
    __SECRET_KEY = os.getenv('SECRET_KEY')
    __ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 60

    @staticmethod
    def create_token(user_id: int, expire: timedelta):
        to_encode = {"user_id": user_id, "exp": datetime.utcnow() + expire}
        encoded_jwt = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=TokenManager.__ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_access_and_refresh_token(user_id: int) -> schemas.Tokens:
        access_token = TokenManager.create_token(user_id, timedelta(minutes=TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_token = TokenManager.create_token(user_id, timedelta(days=TokenManager.REFRESH_TOKEN_EXPIRE_DAYS))
        return schemas.Tokens(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def try_get_user_id_from_token(token: str) -> int:
        try:
            payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[TokenManager.__ALGORITHM])
            if datetime.fromtimestamp(int(payload.get("exp"))) < datetime.now():
                raise errors.TokenExpireError
            user_id: str = payload.get("user_id")
            if user_id is None:
                raise errors.TokenSubError
        except JWTError:
            raise errors.TokenError
        return int(user_id)

