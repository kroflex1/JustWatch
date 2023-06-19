from pydantic import BaseSettings
import pathlib


class Settings(BaseSettings):
    database_name: str
    database_user: str
    database_password: str
    database_host: str
    database_port: str
    secret_key: str
    aws_access_key_id: str
    aws_secret_access_key: str
    SECRET_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    class Config:
        env_file = f"{pathlib.Path(__file__).resolve().parent}/.env"

settings = Settings()


