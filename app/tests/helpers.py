import datetime
from faker import Faker
from typing import Any

from app.domain.todo import models as todo_models


fake = Faker()

ID_MAX_LIMIT = 100000

user: dict[str, Any] = dict(
    user_id=0,
    email="happypuppy@google.com",
    username="happypuppy",
    last_name="Cho",
    first_name="Lucian",
)


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


def create_daily_todo_task(daily_todo: todo_models.DailyTodo):
    daily_todo_task = todo_models.DailyTodoTask(
        content=fake.text(),
        is_completed=fake.boolean(),
    )
    daily_todo.daily_todo_tasks.append(daily_todo_task)

    return daily_todo_task


def create_daily_todo_tasks(daily_todo: todo_models.DailyTodo, n: int = 10):
    return [create_daily_todo_task(daily_todo) for _ in range(n)]


def str_to_date(date: str):
    return datetime.datetime.strptime(date, "%Y-%m-%d").date()


def get_random_date():
    return str_to_date(fake.date())
