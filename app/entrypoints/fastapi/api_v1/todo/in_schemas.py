from pydantic import BaseModel, model_validator


class TodoRepoCreateIn(BaseModel):
    title: str
    description: str


class TodoRepoUpdateIn(BaseModel):
    title: str
    description: str
