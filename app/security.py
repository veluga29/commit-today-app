from datetime import datetime, timedelta
from jose import jwt

from app import settings


class JWTAuthorizer:
    SECRET_KEY = settings.AUTH_SETTINGS.JWT_SECRET_KEY
    ALGORITHM = settings.AUTH_SETTINGS.JWT_ALGORITHM
    EXPIRE_MINUTES = 60 * 24 * 7

    @classmethod
    def create(cls, email: str) -> str:
        payload = {
            "sub": email,
            "exp": datetime.utcnow() + timedelta(days=1),
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def decode(cls, access_token: str) -> dict:
        return jwt.decode(access_token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
