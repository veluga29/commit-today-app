from abc import ABCMeta, abstractmethod
from typing import TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


ModelType = TypeVar("ModelType")


class AbstractRepository(metaclass=ABCMeta):
    def add(self, model):
        self._add(model)

    def add_all(self, models):
        self._add_all(models)

    @abstractmethod
    def _add(self, model):
        ...

    @abstractmethod
    def _add_all(self, models):
        ...


class UserRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _add(self, model):
        self.session.add(model)

    def _add_all(self, models):
        self.session.add_all(models)
