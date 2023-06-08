from contextvars import ContextVar
import peewee
from .config import settings

DATABASE_NAME = settings.database_name
DATABASE_USER = settings.database_user
DATABASE_PASSWORD = settings.database_password
DATABASE_HOST = settings.database_host
DATABASE_PORT = settings.database_port

db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


db = peewee.PostgresqlDatabase(DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD, host=DATABASE_HOST,
                               port=DATABASE_PORT)
db._state = PeeweeConnectionState()
