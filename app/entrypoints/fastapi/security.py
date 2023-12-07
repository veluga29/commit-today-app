from dataclasses import dataclass
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

from app import settings


class JWTAuthorizer:
    SECRET_KEY = settings.AUTH_SETTINGS.JWT_SECRET_KEY
    ALGORITHM = settings.AUTH_SETTINGS.JWT_ALGORITHM
    EXPIRES_DELTA = settings.AUTH_SETTINGS.JWT_EXPIRES_DELTA

    class CredentialsException(Exception):
        ...

    @dataclass
    class UserInfo:
        email: str
        username: str
        last_name: str
        first_name: str

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

    @classmethod
    def get_user_info(cls, auth_header: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False))):
        try:
            if auth_header is None:
                raise cls.CredentialsException
            token = auth_header.credentials
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            email, username, last_name, first_name = (
                payload.get("sub"),
                payload.get("username"),
                payload.get("last_name"),
                payload.get("first_name"),
            )
            if not (email and username and last_name and first_name):
                raise cls.CredentialsException
            user_info = cls.UserInfo(email=email, username=username, last_name=last_name, first_name=first_name)
        except (JWTError, cls.CredentialsException):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_info
