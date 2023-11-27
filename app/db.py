from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)

from app import settings
from app.adapters.auth.persistent_orm import start_mappers as auth_start_mappers
from app.adapters.todo.persistent_orm import start_mappers as todo_start_mappers


if settings.STAGE != "testing":
    auth_start_mappers()
    todo_start_mappers()


engine = create_async_engine(settings.POSTGRES_SETTINGS.get_dsn(), future=True)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False, class_=AsyncSession)


async def get_session():
    async with async_session_factory() as session:
        yield session

