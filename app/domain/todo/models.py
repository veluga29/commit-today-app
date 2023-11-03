from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.domain.base_models import Base


@dataclass
class TodoRepo(Base):
    title: str = field(default="")
    description: str = field(default="")
    user_id: int = field(default=0)

    # relationships
    daily_todos: list[DailyTodo] = field(default_factory=list)
    
    def dict(self) -> dict:
        return dict(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            title=self.title,
            description=self.description,
            user_id=self.user_id,
        )


@dataclass
class DailyTodo:
    todo_repo_id: int = field(default=0)
    date: date = field(default=date.today())
    
    # relationships
    todo_repo: TodoRepo = field(init=False)
    daily_todo_tasks: list[DailyTodoTask] = field(default_factory=list)
    
    def dict(self) -> dict:
        return dict(
            todo_repo_id=self.todo_repo_id,
            date=self.date,
        )


@dataclass
class DailyTodoTask(Base):
    content: str = field(default="")
    is_completed: bool = field(default=False)
    daily_todo_id: int = field(default=0)

    # relationships
    daily_todo: DailyTodo = field(init=False)
    
    def dict(self) -> dict:
        return dict(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            content=self.content,
            is_completed=self.is_completed,
            daily_todo_id=self.daily_todo_id,
        )
