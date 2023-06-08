from pydantic import BaseSettings
import pathlib


class Settings(BaseSettings):
    database_name: str
    database_user: str
    database_password: str
    database_host: str
    database_port: str

    class Config:
        env_file = f"{pathlib.Path(__file__).resolve().parent}/.env"

settings = Settings()


