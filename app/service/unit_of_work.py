from abc import ABCMeta, abstractmethod
from typing import Self

from app.db import async_session_factory
from app.adapters.todo.repository import TodoRepoRepository
from app.adapters.user.repository import UserRepository


DEFAULT_SESSION_FACTORY = async_session_factory


class AbstractUnitOfWork(metaclass=ABCMeta):
    async def __aenter__(self) -> Self:
        return self

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...

    @abstractmethod
    async def refresh(self, object):
        ...

    @abstractmethod
    async def flush(self):
        ...


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.todos = TodoRepoRepository(self.session)
        self.users = UserRepository(self.session)

        return await super().__aenter__()

    async def __aexit__(self, *args):
        await self.session.close()

    async def commit(self):
        await self._commit()

    async def _commit(self):
        await self.session.commit()

    async def rollback(self):
        await self._rollback()

    async def _rollback(self):
        await self.session.rollback()

    async def refresh(self, object):
        await self._refresh(object)

    async def _refresh(self, object):
        await self.session.refresh(object)

    async def flush(self):
        await self._flush()

    async def _flush(self):
        await self.session.flush()
