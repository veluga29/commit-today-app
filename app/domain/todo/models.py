from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.base_models import Base


@dataclass
class TodoRepository(Base):
    title: str
    description: str
    user_id: int

    # relationships
    daily_todos: list[DailyTodo]


@dataclass
class DailyTodo:
    date: date

    # relationships
    todo_repository_id: int
    daily_todo_tasks: list[DailyTodoTask]


@dataclass
class DailyTodoTask(Base):
    content: str
    is_completed: bool

    # relationships
    daily_todo_id: int
