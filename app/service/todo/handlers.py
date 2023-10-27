from app.domain.todo import models as todo_models
from app.adapters.todo.repository import TodoRepoRepository
from dataclasses import asdict


class TodoRepoService:
    @staticmethod
    async def create_todo_repo(title: str, description: str, user_id: int = 0, *, repository: TodoRepoRepository) -> dict:
        todo_repo = todo_models.TodoRepo(title=title, description=description, user_id=user_id)
        res = await repository.create_todo_repo(todo_repo)

        return asdict(res)
