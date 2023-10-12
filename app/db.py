from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)

from app import settings


engine = create_async_engine(settings.POSTGRES_SETTINGS.get_dsn(), future=True)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False, class_=AsyncSession)


async def get_session():
    async with async_session_factory() as session:
        yield session
