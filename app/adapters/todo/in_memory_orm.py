from sqlalchemy import (
    Text,
    ForeignKeyConstraint,
    Index,
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    func,
    Boolean,
)
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import registry, relationship

from app.domain.todo.models import TodoRepository, DailyTodo, DailyTodoTask


mapper_registry = registry()

todo_repositories = Table(
    "todo_repositories",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "create_dt",
        sqlite.TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    ),
    Column(
        "update_dt",
        sqlite.TIMESTAMP(timezone=True),
        default=func.now(),
        onupdate=func.current_timestamp(),
        server_default=func.now(),
        nullable=False,
    ),
    Column("title", String(50), nullable=False, default=""),
    Column("description", String(256), nullable=False, default=""),
)

daily_todos = Table(
    "daily_todos",
    mapper_registry.metadata,
    Column(
        "todo_repository_id",
        ForeignKey(todo_repositories.name + ".id", ondelete="cascade"),
        primary_key=True,
    ),
    Column(
        "date",
        sqlite.TIMESTAMP(timezone=True),
        primary_key=True,
        default=func.now(),
        server_default=func.now(),
    ),
)

daily_todo_tasks = Table(
    "daily_todo_tasks",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "create_dt",
        sqlite.TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    ),
    Column(
        "update_dt",
        sqlite.TIMESTAMP(timezone=True),
        default=func.now(),
        onupdate=func.current_timestamp(),
        server_default=func.now(),
        nullable=False,
    ),
    Column("content", Text, nullable=False),
    Column("is_completed", Boolean, nullable=False, default=False),
    Column("todo_repository_id", Integer, nullable=False),
    Column("date", sqlite.TIMESTAMP(timezone=True), nullable=False),
    ForeignKeyConstraint(
        ["todo_repository_id", "date"],
        ["daily_todos.todo_repository_id", "daily_todos.date"],
        name="fk_daily_todo_task_daily_todo",
    ),
    Index("fk_daily_todo_task_daily_todo", "todo_repository_id", "date"),
)


def start_mappers():
    mapper_registry.map_imperatively(
        TodoRepository,
        todo_repositories,
        properties={
            "daily_todos": relationship(
                DailyTodo,
                back_populates="todo_repositories",
                cascade="all, delete-orphan",
            )
        },
        eager_defaults=True,
    )
    mapper_registry.map_imperatively(
        DailyTodo,
        daily_todos,
        properties={
            "todo_repositories": relationship(
                TodoRepository,
                back_populates="daily_todos",
            ),
            "daily_todo_tasks": relationship(
                DailyTodoTask,
                back_populates="daily_todos",
                cascade="all, delete-orphan",
            ),
        },
        eager_defaults=True,
    )
    mapper_registry.map_imperatively(
        DailyTodoTask,
        daily_todo_tasks,
        properties={
            "daily_todos": relationship(
                DailyTodo,
                back_populates="daily_todo_tasks",
            ),
        },
        eager_defaults=True,
    )
