import os
import random

from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    POSTGRES_SERVER: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    # POSTGRES_TEST_DB: str = f"{POSTGRES_DB}_test_{random.randint(0, 9999)}"
    POSTGRES_PORT: str = ""
    POSTGRES_PROTOCOL: str = ""

    def get_dsn(self) -> str:
        return "{}://{}:{}@{}:{}/{}".format(
            self.POSTGRES_PROTOCOL,
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_SERVER,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )


class SQLiteSettings(BaseSettings):
    SQLITE_PROTOCOL: str = ""
    SQLITE_FILEPATH: str = ""

    def get_dsn(self) -> str:
        return f"{self.SQLITE_PROTOCOL}:///{self.SQLITE_FILEPATH}"


POSTGRES_SETTINGS = PostgresSettings()
SQLITE_SETTINGS = SQLiteSettings()

API_V1_STR: str = os.environ.get("API_V1_STR", "/api/v1")
