import datetime
from faker import Faker

from app.domain.todo import models as todo_models


ID_MAX_LIMIT = 100000
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


def create_daily_todo(todo_repo: todo_models.TodoRepo, date: datetime.date = datetime.date.today()):
    daily_todo = todo_models.DailyTodo(
        date=date,
    )
    daily_todo.todo_repo = todo_repo

    return daily_todo


def str_to_date(date: str):
    return datetime.datetime.strptime(date, "%Y-%m-%d").date()


def get_random_date():
    return str_to_date(fake.date())