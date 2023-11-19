from pydantic import BaseModel, EmailStr


class UserSignUpIn(BaseModel):
    email: EmailStr
    password: str
    username: str
    first_name: str
    last_name: str