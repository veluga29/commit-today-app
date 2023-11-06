from abc import ABCMeta, abstractmethod
from typing import TypeVar
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.todo import models as todo_models


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


class TodoRepoRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _add(self, model):
        self.session.add(model)

    def _add_all(self, models):
        self.session.add_all(models)

    async def get(self, id):
        return await self._get(id)

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

    async def get(self, todo_repo_id, date):
        return await self._get(todo_repo_id, date)

    async def _get(self, todo_repo_id, date):
        q = await self.session.execute(
            select(todo_models.DailyTodo)
            .where(todo_models.DailyTodo.todo_repo_id == todo_repo_id, todo_models.DailyTodo.date == date)
            .options(selectinload(todo_models.DailyTodo.daily_todo_tasks))
        )
        return q.scalar()

    async def create_daily_todo(self, daily_todo: todo_models.DailyTodo):
        return await self._create_daily_todo(daily_todo)

    async def _create_daily_todo(self, daily_todo: todo_models.DailyTodo):
        self.session.add(daily_todo)
        await self.session.commit()
        return daily_todo

    async def update_daily_todo(self):
        return await self._update_daily_todo()

    async def _update_daily_todo(self):
        await self.session.commit()
