import random
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus
from copy import deepcopy
from dateutil.parser import parse

from app.tests import helpers
from app.domain.todo import models


class TestTodoRepo:
    @pytest.mark.asyncio
    async def test_create_todo_repo(self, testing_app):
        # GIVEN
        # user_id = random.choice(range(1, 100))  # TODO
        body = {"title": helpers.fake.word(), "description": helpers.fake.text()}

        # WHEN
        URL = testing_app.url_path_for("create_todo_repo")

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.post(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.CREATED
        repo_for_test = response.json()

        assert repo_for_test["id"]
        assert repo_for_test["created_at"]
        assert repo_for_test["updated_at"]
        assert repo_for_test["title"] == body["title"]
        assert repo_for_test["description"] == body["description"]
        # assert repo_for_test["user_id"] == user_id  # TODO

    @pytest.mark.asyncio
    async def test_update_todo_repo(self, testing_app, async_session: AsyncSession):
        # GIVEN
        user_id = random.choice(range(1, 100))
        repo = helpers.create_todo_repo(user_id=user_id)
        async_session.add(repo)
        await async_session.commit()

        repo_before_update = deepcopy(repo)

        body = {"title": "updated_title", "description": "updated_description"}

        # WHEN
        URL = testing_app.url_path_for("update_todo_repo", todo_repo_id=repo.id)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.patch(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.OK
        repo_for_test = response.json()

        assert repo_before_update.id == repo_for_test["id"]
        assert repo_before_update.created_at == parse(repo_for_test["created_at"])
        assert repo_before_update.updated_at < parse(repo_for_test["updated_at"])
        assert repo_before_update.title != repo_for_test["title"] == body["title"]
        assert repo_before_update.description != repo_for_test["description"] == body["description"]
        assert user_id == repo_for_test["user_id"]

    @pytest.mark.asyncio
    async def test_update_todo_repo_if_not_sending_request_body(self, testing_app, async_session: AsyncSession):
        # GIVEN
        repo = helpers.create_todo_repo()
        async_session.add(repo)
        await async_session.commit()

        # WHEN
        URL = testing_app.url_path_for("update_todo_repo", todo_repo_id=repo.id)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.patch(URL)

        # THEN
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_update_todo_repo_if_repo_does_not_exist(self, testing_app):
        # GIVEN
        repo_id = helpers.ID_MAX_LIMIT
        body = {"title": "updated_title", "description": "updated_description"}

        # WHEN
        URL = testing_app.url_path_for("update_todo_repo", todo_repo_id=repo_id)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.patch(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_todo_repos(self, testing_app, async_session: AsyncSession):
        # GIVEN
        # user_id = random.choice(range(1, 100)) # TODO
        repos = helpers.create_todo_repos(n=20)
        async_session.add_all(repos)
        await async_session.commit()

        # WHEN
        URL = testing_app.url_path_for("get_todo_repos")

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.get(URL)

        # THEN
        assert response.status_code == HTTPStatus.OK
        repos_for_test = response.json()

        for repo, repo_for_test in zip(repos, repos_for_test):
            assert repo.id == repo_for_test["id"]
            assert repo.created_at == parse(repo_for_test["created_at"])
            assert repo.updated_at == parse(repo_for_test["updated_at"])
            assert repo.title == repo_for_test["title"]
            assert repo.description == repo_for_test["description"]
            assert repo.user_id == repo_for_test["user_id"]


class TestDailyTodo:
    @pytest.mark.asyncio
    async def test_create_daily_todo(self, testing_app, async_session: AsyncSession):
        # GIVEN
        repo = helpers.create_todo_repo()
        async_session.add(repo)
        await async_session.commit()

        body = {"date": helpers.fake.date()}

        # WHEN
        URL = testing_app.url_path_for("create_daily_todo", todo_repo_id=repo.id)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.post(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.CREATED
        repo_for_test = response.json()

        assert repo_for_test["todo_repo_id"]
        assert repo_for_test["date"]

    @pytest.mark.asyncio
    async def test_create_daily_todo_if_todo_repo_does_not_exist(self, testing_app):
        # GIVEN
        todo_repo_id = helpers.ID_MAX_LIMIT
        body = {"date": helpers.fake.date()}

        # WHEN
        URL = testing_app.url_path_for("create_daily_todo", todo_repo_id=todo_repo_id)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.post(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_daily_todo_if_daily_todo_already_exists(self, testing_app, async_session: AsyncSession):
        # GIVEN
        date = helpers.fake.date()
        body = {"date": date}

        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=helpers.str_to_date(date))
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        # WHEN
        URL = testing_app.url_path_for("create_daily_todo", todo_repo_id=todo_repo.id)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.post(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @pytest.mark.asyncio
    async def test_get_daily_todo(self, testing_app, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        # WHEN
        URL = testing_app.url_path_for("get_daily_todo", todo_repo_id=todo_repo.id, date=date)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.get(URL)

        # THEN
        assert response.status_code == HTTPStatus.OK
        repo_for_test = response.json()

        assert daily_todo.todo_repo_id == repo_for_test["todo_repo_id"]
        assert daily_todo.date == parse(repo_for_test["date"]).date()

    @pytest.mark.asyncio
    async def test_create_daily_todo_task(self, testing_app, async_session: AsyncSession):
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        content = helpers.fake.text()
        body = {"content": content}

        # WHEN
        URL = testing_app.url_path_for("create_daily_todo_task", todo_repo_id=todo_repo.id, date=date)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.post(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.CREATED
        daily_todo_task_for_test = response.json()

        assert daily_todo_task_for_test["id"]
        assert daily_todo_task_for_test["created_at"]
        assert daily_todo_task_for_test["updated_at"]
        assert daily_todo_task_for_test["content"] == content
        assert daily_todo_task_for_test["is_completed"] is False
        assert daily_todo_task_for_test["todo_repo_id"] == daily_todo.todo_repo_id
        assert parse(daily_todo_task_for_test["date"]).date() == daily_todo.date

    @pytest.mark.asyncio
    async def test_create_daily_todo_task_if_there_is_no_daily_todo(self, testing_app, async_session: AsyncSession):
        date = helpers.get_random_date()
        todo_repo_id = helpers.ID_MAX_LIMIT
        content = helpers.fake.text()
        body = {"content": content}

        # WHEN
        URL = testing_app.url_path_for("create_daily_todo_task", todo_repo_id=todo_repo_id, date=date)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.post(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_daily_todo_tasks(self, testing_app, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        daily_todo_tasks = helpers.create_daily_todo_tasks(daily_todo=daily_todo)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        # WHEN
        URL = testing_app.url_path_for("get_daily_todo_tasks", todo_repo_id=todo_repo.id, date=date)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.get(URL)

        # THEN
        assert response.status_code == HTTPStatus.OK
        daily_todo_tasks_for_test = response.json()

        for daily_todo_task, daily_todo_task_for_test in zip(daily_todo_tasks, daily_todo_tasks_for_test):
            assert daily_todo_task.id == daily_todo_task_for_test["id"]
            assert daily_todo_task.created_at == parse(daily_todo_task_for_test["created_at"])
            assert daily_todo_task.updated_at == parse(daily_todo_task_for_test["updated_at"])
            assert daily_todo_task.content == daily_todo_task_for_test["content"]
            assert daily_todo_task.is_completed == daily_todo_task_for_test["is_completed"]
            assert daily_todo_task.todo_repo_id == daily_todo_task_for_test["todo_repo_id"]
            assert daily_todo_task.date == parse(daily_todo_task_for_test["date"]).date()

    @pytest.mark.asyncio
    async def test_get_daily_todo_tasks_if_there_are_no_tasks(self, testing_app):
        # GIVEN
        todo_repo_id = helpers.ID_MAX_LIMIT
        date = helpers.get_random_date()

        # WHEN
        URL = testing_app.url_path_for("get_daily_todo_tasks", todo_repo_id=todo_repo_id, date=date)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.get(URL)

        # THEN
        assert response.status_code == HTTPStatus.OK
        daily_todo_tasks_for_test = response.json()

        assert daily_todo_tasks_for_test == []

    @pytest.mark.asyncio
    async def test_update_daily_todo_task_for_content(self, testing_app, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        daily_todo_task = helpers.create_daily_todo_task(daily_todo=daily_todo)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        task_before_update = daily_todo_task.dict()
        content = helpers.fake.text()
        body = {"content": content}

        # WHEN
        URL = testing_app.url_path_for(
            "update_daily_todo_task_for_content",
            todo_repo_id=todo_repo.id,
            date=date,
            daily_todo_task_id=daily_todo_task.id,
        )

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.patch(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.OK
        daily_todo_task_for_test = response.json()

        assert task_before_update["id"] == daily_todo_task_for_test["id"]
        assert task_before_update["created_at"] == parse(daily_todo_task_for_test["created_at"])
        assert task_before_update["updated_at"] <= parse(daily_todo_task_for_test["updated_at"])
        assert task_before_update["content"] != daily_todo_task_for_test["content"]
        assert task_before_update["is_completed"] == daily_todo_task_for_test["is_completed"]
        assert task_before_update["todo_repo_id"] == daily_todo_task_for_test["todo_repo_id"]
        assert task_before_update["date"] == parse(daily_todo_task_for_test["date"]).date()

    @pytest.mark.asyncio
    async def test_update_daily_todo_task_for_content_if_there_is_no_daily_todo(self, testing_app):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo_id = helpers.ID_MAX_LIMIT
        daily_todo_task_id = helpers.ID_MAX_LIMIT
        content = helpers.fake.text()
        body = {"content": content}

        # WHEN
        URL = testing_app.url_path_for(
            "update_daily_todo_task_for_content",
            todo_repo_id=todo_repo_id,
            date=date,
            daily_todo_task_id=daily_todo_task_id,
        )

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.patch(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_daily_todo_task_for_content_if_there_is_no_daily_todo_task(
        self, testing_app, async_session: AsyncSession
    ):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        daily_todo_task_id = helpers.ID_MAX_LIMIT
        content = helpers.fake.text()
        body = {"content": content}

        # WHEN
        URL = testing_app.url_path_for(
            "update_daily_todo_task_for_content",
            todo_repo_id=todo_repo.id,
            date=date,
            daily_todo_task_id=daily_todo_task_id,
        )

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.patch(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_daily_todo_task_for_is_completed(self, testing_app, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        daily_todo_task = helpers.create_daily_todo_task(daily_todo=daily_todo)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        task_before_update = daily_todo_task.dict()
        is_completed = not (daily_todo_task.is_completed)
        body = {"is_completed": is_completed}

        # WHEN
        URL = testing_app.url_path_for(
            "update_daily_todo_task_for_is_completed",
            todo_repo_id=todo_repo.id,
            date=date,
            daily_todo_task_id=daily_todo_task.id,
        )

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.patch(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.OK
        daily_todo_task_for_test = response.json()

        assert task_before_update["id"] == daily_todo_task_for_test["id"]
        assert task_before_update["created_at"] == parse(daily_todo_task_for_test["created_at"])
        assert task_before_update["updated_at"] <= parse(daily_todo_task_for_test["updated_at"])
        assert task_before_update["content"] == daily_todo_task_for_test["content"]
        assert task_before_update["is_completed"] != daily_todo_task_for_test["is_completed"] == is_completed
        assert task_before_update["todo_repo_id"] == daily_todo_task_for_test["todo_repo_id"]
        assert task_before_update["date"] == parse(daily_todo_task_for_test["date"]).date()

    @pytest.mark.asyncio
    async def test_update_daily_todo_task_for_is_completed_if_there_is_no_daily_todo(self, testing_app):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo_id = helpers.ID_MAX_LIMIT
        daily_todo_task_id = helpers.ID_MAX_LIMIT
        is_completed = helpers.fake.boolean()
        body = {"is_completed": is_completed}

        # WHEN
        URL = testing_app.url_path_for(
            "update_daily_todo_task_for_is_completed",
            todo_repo_id=todo_repo_id,
            date=date,
            daily_todo_task_id=daily_todo_task_id,
        )

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.patch(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_daily_todo_task_for_is_completed_if_there_is_no_daily_todo_task(
        self, testing_app, async_session: AsyncSession
    ):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        daily_todo_task_id = helpers.ID_MAX_LIMIT
        is_completed = helpers.fake.boolean()
        body = {"is_completed": is_completed}

        # WHEN
        URL = testing_app.url_path_for(
            "update_daily_todo_task_for_is_completed",
            todo_repo_id=todo_repo.id,
            date=date,
            daily_todo_task_id=daily_todo_task_id,
        )

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.patch(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.NOT_FOUND
