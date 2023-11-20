from datetime import datetime, timedelta
from jose import jwt

from app import settings


class JWTAuthorizer:
    SECRET_KEY = settings.AUTH_SETTINGS.JWT_SECRET_KEY
    ALGORITHM = settings.AUTH_SETTINGS.JWT_ALGORITHM
    EXPIRES_DELTA = settings.AUTH_SETTINGS.JWT_EXPIRES_DELTA

    @classmethod
    def create(cls, email: str, expires_delta: int = EXPIRES_DELTA) -> str:
        payload = {
            "sub": email,
            "exp": datetime.utcnow() + timedelta(minutes=expires_delta),
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def decode(cls, access_token: str) -> dict:
        return jwt.decode(access_token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
