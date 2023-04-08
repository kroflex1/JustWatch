import fastapi_jsonrpc as jsonrpc


class AuthError(jsonrpc.BaseError):
    CODE = 7000
    MESSAGE = 'Auth error'


class RegisterError(jsonrpc.BaseError):
    CODE = 7000
    MESSAGE = 'Register error'


class AccountNotFound(jsonrpc.BaseError):
    CODE = 6000
    MESSAGE = 'Account not found'


class TokenError(jsonrpc.BaseModel):
    CODE = 8000
    MESSAGE = 'Invalid token'


class TokenExpireError(jsonrpc.BaseModel):
    CODE = 8000
    MESSAGE = 'The token expired'

class TokenMissinError(jsonrpc.BaseError):
    CODE = 8000
    MESSAGE = 'The token is missing in header'


class TokenSubError(jsonrpc.BaseModel):
    CODE = 8000
    MESSAGE = 'Token sub empty'


class VideoNameEmptyError(jsonrpc.BaseModel):
    CODE = 5000
    MESSAGE = 'Video name is empty'
