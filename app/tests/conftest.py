import asyncio
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
import pytest
import pytest_asyncio

from app.main import app
from app.adapters.auth.persistent_orm import start_mappers as auth_start_mappers
from app.adapters.todo.persistent_orm import start_mappers as todo_start_mappers
from app.adapters.auth.persistent_orm import metadata as auth_metadata
from app.adapters.todo.persistent_orm import metadata as todo_metadata
from app import settings
from app.db import get_session


# TODO: deprecated for pytest-asyncio 0.23
@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()

    yield loop
    loop.close()


# TODO: upgrade pytest-asyncio 0.23
# def pytest_collection_modifyitems(items):
#     pytest_asyncio_tests = (item for item in items if pytest_asyncio.is_async_test(item))
#     session_scope_marker = pytest.mark.asyncio(scope="session")
#     for async_test in pytest_asyncio_tests:
#         async_test.add_marker(session_scope_marker)


@pytest_asyncio.fixture(scope="session")
async def create_test_db():
    async_engine = create_async_engine("postgresql+asyncpg:///", isolation_level="AUTOCOMMIT", future=True)
    test_db = settings.POSTGRES_SETTINGS.test_db

    async with async_engine.begin() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {test_db}"))
        await conn.execute(text(f"CREATE DATABASE {test_db}"))

    yield

    async with async_engine.begin() as conn:
        await conn.execute(text(f"DROP DATABASE {test_db}"))


@pytest_asyncio.fixture(scope="session")
async def mappers(create_test_db):
    auth_start_mappers()
    todo_start_mappers()
    yield
    clear_mappers()


@pytest_asyncio.fixture(scope="session")
async def async_engine(mappers):
    async_engine = create_async_engine(settings.POSTGRES_SETTINGS.get_test_dsn(), future=True)

    async with async_engine.begin() as conn:
        await conn.run_sync(auth_metadata.create_all)
        await conn.run_sync(todo_metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        await conn.run_sync(auth_metadata.drop_all)
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

        stmt = "TRUNCATE TABLE {} RESTART IDENTITY CASCADE;"
        for table in reversed(auth_metadata.sorted_tables):
            await session.execute(text(stmt.format(table)))
        for table in reversed(todo_metadata.sorted_tables):
            await session.execute(text(stmt.format(table)))

        await session.commit()


@pytest_asyncio.fixture(scope="function")
def testing_app(async_session):
    app.dependency_overrides[get_session] = lambda: async_session

    yield app
    app.dependency_overrides = {}
