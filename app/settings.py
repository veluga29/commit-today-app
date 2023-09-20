import os
import random

API_V1_STR: str = os.environ.get("API_V1_STR", "/api/v1")

POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "")
POSTGRES_USER: str = os.getenv("POSTGRES_USER", "")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB: str = os.getenv("POSTGRES_DB", "")
POSTGRES_TEST_DB = f"{POSTGRES_DB}_test{random.randint(0, 9999)}"
POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "")
POSTGRES_PROTOCOL: str = os.getenv("POSTGRES_PROTOCOL", "")

SQLALCHEMY_DATABASE_URI = "{}://{}:{}@{}:{}/{}".format(
    POSTGRES_PROTOCOL,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_SERVER,
    POSTGRES_PORT,
    POSTGRES_DB,
)
