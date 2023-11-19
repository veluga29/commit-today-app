from fastapi import APIRouter, status, Depends, Path, Body, HTTPException
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.auth.repository import UserRepository
from app.entrypoints.fastapi.api_v1.auth import in_schemas, out_schemas
from app.service.auth.handlers import UserService
from app.db import get_session
from app.service import exceptions


router = APIRouter()


@cbv(router)
class Auth:
    session: AsyncSession = Depends(get_session)
    user_service: UserService = Depends()

    @router.post("/sign-up", status_code=201)
    async def user_sign_up(self, sign_up_in: in_schemas.UserSignUpIn) -> out_schemas.UserOut:
        try:
            repository: UserRepository = UserRepository(self.session)
            res = await self.user_service.sign_up_user(
                sign_up_in.email,
                sign_up_in.password,
                sign_up_in.username,
                sign_up_in.last_name,
                sign_up_in.first_name,
                repository=repository,
            )
        except exceptions.UserAlreadyExists as e:
            raise HTTPException(status_code=400, detail=str(e))

        return out_schemas.UserOut(**res)

    @router.post("/login", status_code=200)
    async def user_login(self, login_in: in_schemas.UserLoginIn) -> out_schemas.JWTOut:
        try:
            repository: UserRepository = UserRepository(self.session)
            res = await self.user_service.login_user(login_in.email, login_in.password, repository=repository)
        except exceptions.UserNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
        except exceptions.PasswordNotMatch as e:
            raise HTTPException(status_code=401, detail=str(e))
        
        return out_schemas.JWTOut(**res)

    # @router.post("/log-out", status_code=200)
    # async def user_log_out():
    #     ...
