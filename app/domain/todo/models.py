from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.domain.base_models import Base


@dataclass
class TodoRepository(Base):
    title: str = field(default="")
    description: str = field(default="")
    user_id: int = field(default=0)

    # relationships
    daily_todos: list[DailyTodo] = field(default_factory=list)


@dataclass
class DailyTodo:
    date: date

    # relationships
    todo_repository_id: int = field(default=0)
    daily_todo_tasks: list[DailyTodoTask] = field(default_factory=list)


@dataclass
class DailyTodoTask(Base):
    content: str = field(default="")
    is_completed: bool = field(default=False)

    # relationships
    daily_todo_id: int = field(default=0)
