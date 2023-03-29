import fastapi_jsonrpc as jsonrpc


class AuthError(jsonrpc.BaseError):
    CODE = 7000
    MESSAGE = 'Auth error'


class RegisterError(jsonrpc.BaseError):
    CODE = 7000
    MESSAGE = 'Register error'


class TokenError(jsonrpc.BaseModel):
    CODE = 8000
    MESSAGE = 'Invalid token'


class TokenExpireError(jsonrpc.BaseModel):
    CODE = 8000
    MESSAGE = 'The token expired'


class TokenSubError(jsonrpc.BaseModel):
    CODE = 8000
    MESSAGE = 'Token sub empty'


class AccountNotFound(jsonrpc.BaseError):
    CODE = 6000
    MESSAGE = 'Account not found'
