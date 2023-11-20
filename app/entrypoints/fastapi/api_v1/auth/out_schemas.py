from pydantic import BaseModel


class UserOut(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
