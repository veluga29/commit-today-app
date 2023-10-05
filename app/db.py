from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)

from app import settings


engine = create_async_engine(settings.POSTGRES_SETTINGS.get_dsn(), future=True)


async def get_session():
    async_session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )
    async with async_session_factory() as session:
        yield session
