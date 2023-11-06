from datetime import datetime, date

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
    

class TodoRepoOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    title: str
    description: str
    user_id: int


class DailyTodoOut(BaseModel):
    date: date
    todo_repo_id: int


class DailyTodoTaskOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    content: str
    is_completed: bool
    todo_repo_id: int
    date: date