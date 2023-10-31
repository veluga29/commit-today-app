from faker import Faker

from app.domain.todo import models as todo_models


fake = Faker()


def create_todo_repo(user_id: int = 0):
    todo_repo = todo_models.TodoRepo(
        title=fake.word(),
        description=fake.text(),
        user_id=user_id,
    )

    return todo_repo


def create_todo_repos(user_id: int = 0, n: int = 10):
    return [create_todo_repo(user_id) for _ in range(n)]