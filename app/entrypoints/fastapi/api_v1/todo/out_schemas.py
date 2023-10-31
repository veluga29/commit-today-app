from datetime import datetime

from pydantic import BaseModel


class TodoRepoCreateOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    title: str
    description: str
    user_id: int


class TodoRepoUpdateOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    title: str
    description: str
    user_id: int