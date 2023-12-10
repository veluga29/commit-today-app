from pydantic import BaseModel

from app.entrypoints.fastapi.api_v1.schemas import Response


class UserOut(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str


class UserResponse(Response):
    data: UserOut


class LoginResponse(Response):
    data: None


class LogoutResponse(Response):
    data: None
