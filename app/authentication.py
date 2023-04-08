from datetime import datetime, timedelta
from jose import JWTError, jwt
from . import errors, schemas

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


class TokenManager:
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 60

    @staticmethod
    def __create_token(user_id: int, expire: timedelta):
        to_encode = {"user_id": user_id, "exp": datetime.utcnow() + expire}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_access_and_refresh_token(user_id: int) -> schemas.Tokens:
        access_token = TokenManager.__create_token(user_id, timedelta(minutes=TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_token = TokenManager.__create_token(user_id, timedelta(days=TokenManager.REFRESH_TOKEN_EXPIRE_DAYS))
        return schemas.Tokens(access_token=access_token, refresh_token=refresh_token)

    @staticmethod
    def get_user_id_from_token(token: str) -> int:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if datetime.fromtimestamp(int(payload.get("exp"))) < datetime.now():
                raise errors.TokenExpireError
            user_id: str = payload.get("user_id")
            if user_id is None:
                raise errors.TokenSubError
        except JWTError:
            raise errors.TokenError
        return int(user_id)
