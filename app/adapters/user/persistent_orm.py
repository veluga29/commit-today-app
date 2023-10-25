from sqlalchemy import Table, Column, Integer, String, func, MetaData
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import registry

from app.domain.user.models import User

metadata = MetaData()
mapper_registry = registry(metadata=metadata)

user = Table(
    "user",
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
    Column("fullname", String(50), nullable=False),
    Column("username", String(50), nullable=False),
    Column("email", String(50), nullable=False),
    Column("password", String(64), nullable=False),
)


def start_mappers():
    mapper_registry.map_imperatively(User, user)
