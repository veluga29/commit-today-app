from sqlalchemy import Table, Column, Integer, String, func, MetaData
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import registry

from app.domain.auth.models import User

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

users = Table(
    "users",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column(
        "created_at",
        sqlite.TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
    ),
    Column(
        "updated_at",
        sqlite.TIMESTAMP(timezone=True),
        default=func.now(),
        onupdate=func.current_timestamp(),
        server_default=func.now(),
        nullable=False,
    ),
    Column("email", String, index=True, nullable=False),
    Column("password", String(64), nullable=False),
    Column("username", String(50), nullable=False),
    Column("last_name", String(30), nullable=False),
    Column("first_name", String(30), nullable=False),
)


def start_mappers():
    mapper_registry.map_imperatively(User, users)
