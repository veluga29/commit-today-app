import datetime

from app.domain.todo import models as todo_models
from app.adapters.todo.repository import TodoRepoRepository, DailyTodoRepository
from app.service import exceptions
from app.utils.pagination import CursorPagination


class TodoRepoService:
    @staticmethod
    async def create_todo_repo(
        title: str, description: str, user_id: int = 0, *, repository: TodoRepoRepository
    ) -> dict:
        todo_repo = todo_models.TodoRepo(title=title, description=description, user_id=user_id)
        res = await repository.create_todo_repo(todo_repo)

        return res.dict()

    @staticmethod
    async def update_todo_repo(
        id: int, title: str | None, description: str | None, *, repository: TodoRepoRepository
    ) -> dict:
        if (todo_repo := await repository.get(id)) is None:
            raise exceptions.TodoRepoNotFound(f"TodoRepo with id {id} not found")

        if title:
            todo_repo.title = title
        if description:
            todo_repo.description = description

        res = await repository.update_todo_repo(todo_repo)

        return res.dict()

    @staticmethod
    async def get_todo_repos(
        user_id: int = 0, cursor: int | None = None, page_size: int = 10, *, repository: TodoRepoRepository
    ) -> dict:
        curr_items = await repository.get_todo_repos_by_user_id(user_id, cursor, page_size)

        # Pagination
        cursor_pagination = CursorPagination(cursor=cursor, page_size=page_size, curr_items=curr_items)
        next_cursor = cursor_pagination.next_cursor

        prev_items, next_items = await repository.get_prev_todo_repos_and_next_todo_repos(
            user_id=user_id, cursor=cursor, next_cursor=next_cursor, page_size=page_size
        )

        return cursor_pagination.get_pagiantion_response(prev_items=prev_items, next_items=next_items)


class DailyTodoService:
    @staticmethod
    async def create_daily_todo(
        todo_repo_id: int,
        date: datetime.date,
        *,
        todo_repo_repository: TodoRepoRepository,
        daily_todo_repository: DailyTodoRepository,
    ) -> dict:
        if (todo_repo := await todo_repo_repository.get(todo_repo_id)) is None:
            raise exceptions.TodoRepoNotFound(f"TodoRepo with id {todo_repo_id} not found")
        if await daily_todo_repository.get(todo_repo_id, date):
            raise exceptions.DailyTodoAlreadyExists(f"DailyTodo with id ({todo_repo_id}, {date}) already exists")

        daily_todo = todo_models.DailyTodo(date=date)
        daily_todo.todo_repo = todo_repo

        await daily_todo_repository.create_daily_todo(daily_todo)

        return daily_todo.dict()

    @staticmethod
    async def get_daily_todo(todo_repo_id: int, date: datetime.date, *, repository: DailyTodoRepository) -> dict:
        if (daily_todo := await repository.get(todo_repo_id, date)) is None:
            raise exceptions.DailyTodoNotFound(f"DailyTodo with id ({todo_repo_id}, {date}) not found")

        return daily_todo.dict()

    @staticmethod
    async def create_daily_todo_task(
        todo_repo_id: int, date: datetime.date, content: str, *, repository: DailyTodoRepository
    ) -> dict:
        if (daily_todo := await repository.get(todo_repo_id, date)) is None:
            raise exceptions.DailyTodoNotFound(f"DailyTodo with id ({todo_repo_id}, {date}) not found")

        daily_todo_task = todo_models.DailyTodoTask(content=content)
        daily_todo.daily_todo_tasks.append(daily_todo_task)

        await repository.update_daily_todo()

        return daily_todo_task.dict()

    @staticmethod
    async def get_daily_todo_tasks(
        todo_repo_id: int, date: datetime.date, *, repository: DailyTodoRepository
    ) -> list[dict]:
        daily_todo: todo_models.DailyTodo = await repository.get(todo_repo_id, date)

        return [t.dict() for t in daily_todo.daily_todo_tasks] if daily_todo else []

    @staticmethod
    async def update_daily_todo_task_for_content(
        todo_repo_id: int,
        date: datetime.date,
        daily_todo_task_id: int,
        content: str,
        *,
        repository: DailyTodoRepository,
    ) -> dict:
        if (daily_todo := await repository.get(todo_repo_id, date)) is None:
            raise exceptions.DailyTodoNotFound(f"DailyTodo with id ({todo_repo_id}, {date}) not found")

        if (daily_todo_task := daily_todo.get_daily_todo_task_by_id(daily_todo_task_id)) is None:
            raise exceptions.DailyTodoTaskNotFound(f"DailyTodoTask with id {daily_todo_task_id} not found")

        daily_todo_task.content = content

        await repository.update_daily_todo()

        return daily_todo_task.dict()

    @staticmethod
    async def update_daily_todo_task_for_is_completed(
        todo_repo_id: int,
        date: datetime.date,
        daily_todo_task_id: int,
        is_completed: bool,
        *,
        repository: DailyTodoRepository,
    ) -> dict:
        if (daily_todo := await repository.get(todo_repo_id, date)) is None:
            raise exceptions.DailyTodoNotFound(f"DailyTodo with id ({todo_repo_id}, {date}) not found")

        if (daily_todo_task := daily_todo.get_daily_todo_task_by_id(daily_todo_task_id)) is None:
            raise exceptions.DailyTodoTaskNotFound(f"DailyTodoTask with id {daily_todo_task_id} not found")

        daily_todo_task.is_completed = is_completed

        await repository.update_daily_todo()

        return daily_todo_task.dict()
