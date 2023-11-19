from abc import ABCMeta, abstractmethod
from typing import TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.auth import models as auth_models


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
    
    async def get_user_by_email(self, email: str) -> auth_models.User:
        return await self._get_user_by_email(email)
    
    async def _get_user_by_email(self, email: str) -> auth_models.User:
        stmt = select(auth_models.User).where(auth_models.User.email == email)
        q = await self.session.execute(stmt)
        return q.scalar()

    async def create_user(self, user: auth_models.User) -> auth_models.User:
        return await self._create_user(user)

    async def _create_user(self, user: auth_models.User) -> auth_models.User:
        self.session.add(user)
        await self.session.commit()
        return user