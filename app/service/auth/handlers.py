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
