from abc import ABCMeta, abstractmethod
from typing import TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.todo import models as todo_models


ModelType = TypeVar("ModelType")


class AbstractRepository(metaclass=ABCMeta):
    def add(self, model):
        self._add(model)

    def add_all(self, models):
        self._add_all(models)

    async def get(self, id):
        return await self._get(id)

    @abstractmethod
    def _add(self, model):
        ...

    @abstractmethod
    def _add_all(self, models):
        ...

    @abstractmethod
    async def _get(self, id):
        ...


class TodoRepoRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _add(self, model):
        self.session.add(model)

    def _add_all(self, models):
        self.session.add_all(models)

    async def _get(self, id):
        q = await self.session.execute(select(todo_models.TodoRepo).where(todo_models.TodoRepo.id == id))
        return q.scalar()

    async def create_todo_repo(self, todo_repo: todo_models.TodoRepo):
        self.session.add(todo_repo)
        await self.session.commit()
        return todo_repo

    async def get_todo_repos_by_user_id(self, user_id):
        q = await self.session.execute(select(todo_models.TodoRepo).where(todo_models.TodoRepo.user_id == user_id))
        return q.scalars().all()
    
    async def update_todo_repo(self, todo_repo: todo_models.TodoRepo):
        self.session.add(todo_repo)
        await self.session.commit()
        return todo_repo


class DailyTodoRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _add(self, model):
        self.session.add(model)

    def _add_all(self, models):
        self.session.add_all(models)
