import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, JWTError
from typing import Any, Annotated
from email_validator import validate_email, EmailNotValidError, EmailSyntaxError, EmailUndeliverableError

from app import settings


class OAuth2PasswordRequestFormWithValidation(OAuth2PasswordRequestForm):
    def __init__(
        self,
        *,
        grant_type: Annotated[str | None, Form(pattern="password")] = None,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        scope: Annotated[str, Form()] = "",
        client_id: Annotated[str | None, Form()] = None,
        client_secret: Annotated[str | None, Form()] = None,
    ):
        try:
            validated_email = validate_email(username)
        except (EmailNotValidError, EmailSyntaxError, EmailUndeliverableError):
            raise HTTPException(status_code=422, detail="Invalid email")

        self.grant_type = grant_type
        self.email = validated_email.email
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


class JWTFromAuthorizationOrCookie(OAuth2PasswordBearer):
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
        return await self.get_access_token_from_authorization(request) or await self.get_access_token_from_cookie(
            request
        )

    async def get_access_token_from_authorization(self, request: Request) -> str | None:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer" or param == "undefined":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param

    async def get_access_token_from_cookie(self, request: Request) -> str | None:
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
    REFRESH_EXPIRES_DELTA = settings.AUTH_SETTINGS.JWT_REFRESH_EXPIRES_DELTA
    JWT_COOKIE_AUTH = JWTFromAuthorizationOrCookie(tokenUrl="api/v1/external/auth/login", auto_error=False)

    class CredentialsException(Exception):
        ...

    @dataclass
    class UserInfo:
        email: str
        username: str
        last_name: str
        first_name: str

    @classmethod
    def create(cls, user: dict[str, Any], is_refresh: bool = False) -> str:
        expires_delta = cls.REFRESH_EXPIRES_DELTA if is_refresh else cls.EXPIRES_DELTA
        payload = dict(
            sub=user["email"],
            exp=datetime.utcnow() + timedelta(minutes=expires_delta),
            iat=datetime.utcnow(),
            jti=uuid.uuid4().hex,
        )
        if is_refresh is False:
            payload |= dict(username=user["username"], last_name=user["last_name"], first_name=user["first_name"])

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
