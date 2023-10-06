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
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import registry, relationship

from app.domain.todo.models import TodoRepository, DailyTodo, DailyTodoTask


mapper_registry = registry()

todo_repository = Table(
    "todo_repository",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "create_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    ),
    Column(
        "update_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=func.now(),
        onupdate=func.current_timestamp(),
        server_default=func.now(),
        nullable=False,
    ),
    Column("title", String(50), nullable=False, default=""),
    Column("description", String(256), nullable=False, default=""),
)

daily_todo = Table(
    "daily_todo",
    mapper_registry.metadata,
    Column(
        "todo_repository_id",
        ForeignKey(todo_repository.name + ".id", ondelete="cascade"),
        primary_key=True,
    ),
    Column(
        "date",
        postgresql.TIMESTAMP(timezone=True),
        primary_key=True,
        default=func.now(),
        server_default=func.now(),
    ),
)

daily_todo_task = Table(
    "daily_todo_task",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "create_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    ),
    Column(
        "update_dt",
        postgresql.TIMESTAMP(timezone=True),
        default=func.now(),
        onupdate=func.current_timestamp(),
        server_default=func.now(),
        nullable=False,
    ),
    Column("content", Text, nullable=False),
    Column("is_completed", Boolean, nullable=False, default=False),
    Column("todo_repository_id", Integer, nullable=False),
    Column("date", postgresql.TIMESTAMP(timezone=True), nullable=False),
    ForeignKeyConstraint(
        ["todo_repository_id", "date"],
        ["daily_todo.todo_repository_id", "daily_todo.date"],
        name="fk_daily_todo_task_daily_todo",
    ),
    Index("fk_daily_todo_task_daily_todo", "todo_repository_id", "date"),
)


def start_mappers():
    mapper_registry.map_imperatively(
        TodoRepository,
        todo_repository,
        properties={
            "daily_todos": relationship(
                DailyTodo,
                back_populates="todo_repository",
                cascade="all, delete-orphan",
            )
        },
        eager_defaults=True,
    )
    mapper_registry.map_imperatively(
        DailyTodo,
        daily_todo,
        properties={
            "todo_repository": relationship(
                TodoRepository,
                back_populates="daily_todos",
            ),
            "daily_todo_tasks": relationship(
                DailyTodoTask,
                back_populates="daily_todo",
                cascade="all, delete-orphan",
            ),
        },
        eager_defaults=True,
    )
    mapper_registry.map_imperatively(
        DailyTodoTask,
        daily_todo_task,
        properties={
            "daily_todo": relationship(
                DailyTodo,
                back_populates="daily_todo_tasks",
            ),
        },
        eager_defaults=True,
    )
