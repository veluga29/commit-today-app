from fastapi import APIRouter, status, Depends, Path, Body, HTTPException, Response, Cookie
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.adapters.auth.repository import UserRepository
from app.entrypoints.fastapi.api_v1 import enums, examples
from app.entrypoints.fastapi.api_v1.auth import in_schemas, out_schemas
from app.entrypoints.fastapi.security import OAuth2PasswordRequestFormWithValidation, JWTAuthorizer
from app.service.auth.handlers import UserService
from app.db import get_session
from app.service import exceptions


router = APIRouter()


@cbv(router)
class Auth:
    session: AsyncSession = Depends(get_session)
    user_service: UserService = Depends()

    @router.post(
        "/signup",
        status_code=status.HTTP_201_CREATED,
        responses=examples.get_error_responses([status.HTTP_400_BAD_REQUEST]),
    )
    async def user_signup(self, sign_up_in: in_schemas.UserSignUpIn) -> out_schemas.UserResponse:
        try:
            repository: UserRepository = UserRepository(self.session)
            res = await self.user_service.signup_user(
                sign_up_in.email,
                sign_up_in.password,
                sign_up_in.username,
                sign_up_in.last_name,
                sign_up_in.first_name,
                repository=repository,
            )
        except exceptions.UserAlreadyExists as e:
            raise HTTPException(status_code=400, detail=str(e))

        return out_schemas.UserResponse(
            ok=True, message=enums.ResponseMessage.CREATE_SUCCESS, data=out_schemas.UserOut(**res)
        )

    @router.post(
        "/login",
        status_code=status.HTTP_200_OK,
        responses=examples.get_error_responses([status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]),
    )
    async def user_login(
        self, login_in: Annotated[OAuth2PasswordRequestFormWithValidation, Depends()], response: Response
    ):
        try:
            repository: UserRepository = UserRepository(self.session)
            res = await self.user_service.login_user(login_in.email, login_in.password, repository=repository)
            response.set_cookie(key="access_token", value=res["access_token"], httponly=True, secure=True)
            response.set_cookie(key="refresh_token", value=res["refresh_token"], httponly=True, secure=True)
        except exceptions.UserNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
        except exceptions.PasswordNotMatch as e:
            raise HTTPException(status_code=401, detail=str(e))

        return out_schemas.LoginResponse(ok=True, message=enums.ResponseMessage.LOGIN_SUCCESS, data=None)

    @router.post("/logout", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTAuthorizer.get_user_info)])
    async def user_logout(self, response: Response) -> out_schemas.LogoutResponse:
        response.set_cookie(key="access_token", expires=0, max_age=0, httponly=True, secure=True)
        response.set_cookie(key="refresh_token", expires=0, max_age=0, httponly=True, secure=True)

        return out_schemas.LogoutResponse(ok=True, message=enums.ResponseMessage.LOGOUT_SUCCESS, data=None)

    @router.get("/login-refresh", status_code=status.HTTP_200_OK)
    async def refresh_login(self, response: Response, refresh_token: str = Cookie(...)):
        try:
            repository: UserRepository = UserRepository(self.session)
            res = await self.user_service.refresh_login(refresh_token=refresh_token, repository=repository)
            response.set_cookie(key="access_token", value=res["access_token"], httponly=True, secure=True)
            response.set_cookie(key="refresh_token", value=res["refresh_token"], httponly=True, secure=True)
        except exceptions.InvalidToken as e:
            raise HTTPException(status_code=401, detail=str(e))
        except exceptions.UserNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        return out_schemas.LoginResponse(ok=True, message=enums.ResponseMessage.REFRESH_SUCCESS, data=None)
