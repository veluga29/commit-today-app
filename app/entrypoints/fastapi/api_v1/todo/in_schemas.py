from pydantic import BaseModel


class TodoRepoCreateIn(BaseModel):
    title: str
    description: str
