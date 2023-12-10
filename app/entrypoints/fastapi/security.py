from dataclasses import dataclass
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Any

from app import settings


class JWTCookieAuth(OAuth2PasswordBearer):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        super().__init__(
            tokenUrl=tokenUrl,
            scheme_name=scheme_name,
            scopes=scopes,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> str | None:
        if (access_token := request.cookies.get("access_token")) is None:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None

        return access_token


class JWTAuthorizer:
    SECRET_KEY = settings.AUTH_SETTINGS.JWT_SECRET_KEY
    ALGORITHM = settings.AUTH_SETTINGS.JWT_ALGORITHM
    EXPIRES_DELTA = settings.AUTH_SETTINGS.JWT_EXPIRES_DELTA
    JWT_COOKIE_AUTH = JWTCookieAuth(tokenUrl="api/v1/external/auth/login", auto_error=False)

    class CredentialsException(Exception):
        ...

    @dataclass
    class UserInfo:
        email: str
        username: str
        last_name: str
        first_name: str

    @classmethod
    def create(cls, user: dict[str, Any], expires_delta: int = EXPIRES_DELTA) -> str:
        payload = {
            "sub": user["email"],
            "exp": datetime.utcnow() + timedelta(minutes=expires_delta),
            "username": user["username"],
            "last_name": user["last_name"],
            "first_name": user["first_name"],
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def decode(cls, access_token: str) -> dict:
        return jwt.decode(access_token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])

    @classmethod
    async def get_user_info(cls, access_token: str | None = Depends(JWT_COOKIE_AUTH)):
        try:
            if access_token is None:
                raise cls.CredentialsException
            payload = jwt.decode(access_token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
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
            )

        return user_info
