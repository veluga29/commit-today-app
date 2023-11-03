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
    MetaData,
    Date
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import registry, relationship

from app.domain.todo.models import TodoRepo, DailyTodo, DailyTodoTask

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

todo_repos = Table(
    "todo_repos",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "created_at",
        postgresql.TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    ),
    Column(
        "updated_at",
        postgresql.TIMESTAMP(timezone=True),
        default=func.now(),
        onupdate=func.current_timestamp(),
        server_default=func.now(),
        nullable=False,
    ),
    Column("title", String(50), nullable=False, default=""),
    Column("description", String(256), nullable=False, default=""),
    Column("user_id", Integer, nullable=False, index=True),
)

daily_todos = Table(
    "daily_todos",
    mapper_registry.metadata,
    Column("todo_repo_id", ForeignKey(todo_repos.name + ".id", ondelete="cascade"), primary_key=True),
    Column("date", Date, primary_key=True),
)

daily_todo_tasks = Table(
    "daily_todo_tasks",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "created_at",
        postgresql.TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    ),
    Column(
        "updated_at",
        postgresql.TIMESTAMP(timezone=True),
        default=func.now(),
        onupdate=func.current_timestamp(),
        server_default=func.now(),
        nullable=False,
    ),
    Column("content", Text, nullable=False),
    Column("is_completed", Boolean, nullable=False, default=False),
    Column("todo_repo_id", Integer, nullable=False),
    Column("date", postgresql.TIMESTAMP(timezone=True), nullable=False),
    ForeignKeyConstraint(
        ["todo_repo_id", "date"],
        ["daily_todos.todo_repo_id", "daily_todos.date"],
        name="fk_daily_todo_task_daily_todo",
    ),
    Index("fk_daily_todo_task_daily_todo", "todo_repo_id", "date"),
)


def start_mappers():
    mapper_registry.map_imperatively(
        TodoRepo,
        todo_repos,
        properties={
            "daily_todos": relationship(
                DailyTodo,
                back_populates="todo_repo",
                cascade="all, delete-orphan",
            )
        },
        eager_defaults=True,
    )
    mapper_registry.map_imperatively(
        DailyTodo,
        daily_todos,
        properties={
            "todo_repo": relationship(
                TodoRepo,
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
        daily_todo_tasks,
        properties={
            "daily_todo": relationship(
                DailyTodo,
                back_populates="daily_todo_tasks",
            ),
        },
        eager_defaults=True,
    )
