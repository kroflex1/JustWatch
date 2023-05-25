import fastapi_jsonrpc as jsonrpc


class AuthError(jsonrpc.BaseError):
    CODE = 1000
    MESSAGE = 'Auth error'


class RegisterError(jsonrpc.BaseError):
    CODE = 1000
    MESSAGE = 'Register error'


class AccountNotFound(jsonrpc.BaseError):
    CODE = 1000
    MESSAGE = 'Account not found'


class TokenError(jsonrpc.BaseError):
    CODE = 1000
    MESSAGE = 'Invalid token'


class TokenExpireError(jsonrpc.BaseError):
    CODE = 1000
    MESSAGE = 'The token expired'


class AccessTokenMissingError(jsonrpc.BaseError):
    CODE = 1000
    MESSAGE = 'The access token is missing in header'


class RefreshTokenMissingError(jsonrpc.BaseError):
    CODE = 1000
    MESSAGE = 'The refresh token is missing in header'


class TokenSubError(jsonrpc.BaseError):
    CODE = 1000
    MESSAGE = 'Token sub empty'


class NoFileError(jsonrpc.BaseError):
    CODE = 5000
    MESSAGE = 'No file'


class VideoNameEmptyError(jsonrpc.BaseError):
    CODE = 5000
    MESSAGE = 'Video name is empty'


class VideoNotExist(jsonrpc.BaseError):
    CODE = 5000
    MESSAGE = 'No video with this id found'


class AlreadySubscribed(jsonrpc.BaseError):
    CODE = 7000
    MESSAGE = 'User already subscribed to author'


class AlreadySubscribed(jsonrpc.BaseError):
    CODE = 7000
    MESSAGE = 'User already subscribed to author'


class AlreadyUnsubscribed(jsonrpc.BaseError):
    CODE = 7000
    MESSAGE = 'User already unsubscribed to author'


class AlreadyWatched(jsonrpc.BaseError):
    CODE = 7000
    MESSAGE = 'User already watched this video'


class SubscribeToYourself(jsonrpc.BaseError):
    CODE = 7000
    MESSAGE = "User can't subscribe to yourself"
