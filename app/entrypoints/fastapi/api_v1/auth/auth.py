from fastapi import APIRouter, status, Depends, Path, Body, HTTPException, Response
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.auth.repository import UserRepository
from app.entrypoints.fastapi.api_v1 import enums, examples
from app.entrypoints.fastapi.api_v1.auth import in_schemas, out_schemas
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        return out_schemas.UserResponse(
            ok=True, message=enums.ResponseMessage.CREATE_SUCCESS, data=out_schemas.UserOut(**res)
        )

    @router.post(
        "/login",
        status_code=status.HTTP_200_OK,
        responses=examples.get_error_responses([status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]),
    )
    async def user_login(self, login_in: in_schemas.UserLoginIn, response: Response):
        try:
            repository: UserRepository = UserRepository(self.session)
            res = await self.user_service.login_user(login_in.email, login_in.password, repository=repository)
            response.set_cookie(key="access_token", value=res["access_token"], httponly=True, secure=True)
        except exceptions.UserNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
        except exceptions.PasswordNotMatch as e:
            raise HTTPException(status_code=401, detail=str(e))

        return out_schemas.LoginResponse(ok=True, message=enums.ResponseMessage.LOGIN_SUCCESS, data=None)

    # @router.post("/log-out", status_code=200)
    # async def user_log_out():
    #     ...
