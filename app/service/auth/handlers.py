from app.domain.auth import models as auth_models
from app.adapters.auth.repository import UserRepository
from app.service import exceptions
from app.entrypoints.fastapi.security import JWTAuthorizer


class UserService:
    @staticmethod
    async def signup_user(
        email: str, password: str, user_name: str, last_name: str, first_name: str, *, repository: UserRepository
    ) -> dict:
        if await repository.get_user_by_email(email):
            raise exceptions.UserAlreadyExists(f"User with email ({email}) already exists")

        user = auth_models.User(
            email=email, password=password, username=user_name, last_name=last_name, first_name=first_name
        )
        user.hash_password()
        res = await repository.create_user(user)

        return res.dict()

    @staticmethod
    async def login_user(email: str, password: str, *, repository: UserRepository) -> dict:
        if (user := await repository.get_user_by_email(email)) is None:
            raise exceptions.UserNotFound(f"User with email ({email}) not found")
        if not user.verify_password(password):
            raise exceptions.PasswordNotMatch(f"Not Authorized: Input password does not match")

        return dict(
            access_token=JWTAuthorizer.create(user.dict()),
            refresh_token=JWTAuthorizer.create(user.dict(), is_refresh=True),
        )

    @staticmethod
    async def refresh_login(refresh_token: str | None, *, repository: UserRepository) -> dict:
        if refresh_token is None:
            raise exceptions.NoTokenExists(f"Refresh token doesn't exist")

        payload = JWTAuthorizer.decode(refresh_token, is_refresh=True)
        email = payload.get("sub")

        if not email:
            raise exceptions.InvalidToken(f"Refresh token is invalid")
        if (user := await repository.get_user_by_email(email)) is None:
            raise exceptions.UserNotFound(f"User with email ({email}) not found")

        return dict(
            access_token=JWTAuthorizer.create(user.dict()),
            refresh_token=JWTAuthorizer.create(user.dict(), is_refresh=True),
        )
