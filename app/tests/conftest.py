import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
import pytest
import pytest_asyncio

from app.main import app
from app.adapters.user.persistent_orm import start_mappers as user_start_mappers
from app.adapters.todo.persistent_orm import start_mappers as todo_start_mappers
from app.adapters.user.persistent_orm import metadata as user_metadata
from app.adapters.todo.persistent_orm import metadata as todo_metadata
from app import settings


@pytest_asyncio.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()

    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def create_test_db():
    async_engine = create_async_engine("postgresql+asyncpg:///", isolation_level="AUTOCOMMIT", future=True)
    test_db = settings.POSTGRES_SETTINGS.test_db

    async with async_engine.begin() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {test_db}"))
        await conn.execute(text(f"CREATE DATABASE {test_db}"))

        yield
        await conn.execute(text(f"DROP DATABASE {test_db}"))


@pytest_asyncio.fixture(scope="session")
async def mappers(create_test_db):
    user_start_mappers()
    todo_start_mappers()
    yield
    clear_mappers()


@pytest_asyncio.fixture(scope="session")
async def async_engine(mappers):
    async_engine = create_async_engine(settings.POSTGRES_SETTINGS.get_test_dsn(), future=True)

    async with async_engine.begin() as conn:
        await conn.run_sync(user_metadata.create_all)
        await conn.run_sync(todo_metadata.create_all)

        yield async_engine

        await conn.run_sync(user_metadata.drop_all)
        await conn.run_sync(todo_metadata.drop_all)

    await async_engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def async_session_factory(async_engine):
    session_factory: sessionmaker = sessionmaker(
        async_engine,
        expire_on_commit=False,
        autoflush=False,
        class_=AsyncSession,
    )
    yield session_factory


@pytest_asyncio.fixture(scope="function")
async def async_session(async_session_factory):
    async with async_session_factory() as session:
        yield session
