from datetime import datetime, timedelta
from jose import JWTError, jwt
from . import errors

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(user_id: str) -> str:
    to_encode = {"sub": user_id}
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decrypt_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.fromtimestamp(int(payload.get("exp"))) < datetime.now():
            raise errors.TokenExpireError
        user_id: str = payload.get("sub")
        if user_id is None:
            raise errors.TokenSubError
    except JWTError:
        raise errors.TokenError
    return user_id
