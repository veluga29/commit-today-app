from sqlalchemy import Table, Column, Integer, String, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import registry

from app.domain.user.models import User

mapper_registry = registry()

user = Table(
    "user",
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
    Column("fullname", String(50), nullable=False),
    Column("username", String(50), nullable=False),
    Column("email", String(50), nullable=False),
    Column("password", String(64), nullable=False),
)


def start_mappers():
    mapper_registry.map_imperatively(User, user)
