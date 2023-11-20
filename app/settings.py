import os
import random

from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    POSTGRES_SERVER: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_PORT: str = ""
    POSTGRES_PROTOCOL: str = ""

    @property
    def test_db(self) -> str:
        return f"{self.POSTGRES_DB}_test"

    def get_dsn(self) -> str:
        return "{}://{}:{}@{}:{}/{}".format(
            self.POSTGRES_PROTOCOL,
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_SERVER,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )

    def get_test_dsn(self) -> str:
        return "{}://{}:{}@{}:{}/{}".format(
            self.POSTGRES_PROTOCOL,
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_SERVER,
            self.POSTGRES_PORT,
            self.test_db,
        )


class SQLiteSettings(BaseSettings):
    SQLITE_PROTOCOL: str = ""
    SQLITE_FILEPATH: str = ""

    def get_dsn(self) -> str:
        return f"{self.SQLITE_PROTOCOL}:///{self.SQLITE_FILEPATH}"


class AuthSettings(BaseSettings):
    HASH_ENCODING: str = "UTF-8"
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""
    JWT_EXPIRES_DELTA: int = 0


POSTGRES_SETTINGS = PostgresSettings()
SQLITE_SETTINGS = SQLiteSettings()

AUTH_SETTINGS = AuthSettings()

STAGE = os.environ.get("STAGE", "local")
API_V1_STR: str = os.environ.get("API_V1_STR", "/api/v1")
