from pydantic import BaseModel, EmailStr, Field


class UserSignUpIn(BaseModel):
    email: EmailStr
    password: str
    username: str
    first_name: str
    last_name: str


class UserLoginIn(BaseModel):
    email: EmailStr = Field(..., alias="username")
    password: str
