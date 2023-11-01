from dataclasses import asdict

from app.domain.todo import models as todo_models
from app.adapters.todo.repository import TodoRepoRepository
from app.service import exceptions


class TodoRepoService:
    @staticmethod
    async def create_todo_repo(
        title: str, description: str, user_id: int = 0, *, repository: TodoRepoRepository
    ) -> dict:
        todo_repo = todo_models.TodoRepo(title=title, description=description, user_id=user_id)
        res = await repository.create_todo_repo(todo_repo)

        return asdict(res)

    @staticmethod
    async def update_todo_repo(
        id: int, title: str | None, description: str | None, *, repository: TodoRepoRepository
    ) -> dict:
        if (todo_repo := await repository.get(id)) is None:
            raise exceptions.NotFound(f"TodoRepo with id {id} not found")

        if title:
            todo_repo.title = title
        if description:
            todo_repo.description = description

        res = await repository.update_todo_repo(todo_repo)

        return asdict(res)

    @staticmethod
    async def get_todo_repos(user_id: int = 0, *, repository: TodoRepoRepository) -> list[dict]:
        res = await repository.get_todo_repos_by_user_id(user_id)

        return [asdict(r) for r in res]
