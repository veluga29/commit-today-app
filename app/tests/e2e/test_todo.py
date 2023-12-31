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
from app.entrypoints.fastapi.api_v1 import enums as api_enums
from app.tests import utils


class TestTodoRepo:
    @pytest.mark.asyncio
    async def test_create_todo_repo(self, testing_app):
        # GIVEN
        user_id = helpers.user["user_id"]
        body = {"title": helpers.fake.word(), "description": helpers.fake.text()}

        # WHEN
        URL = testing_app.url_path_for("create_todo_repo")

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.post(URL, json=body)

        # THEN
        assert response.status_code == HTTPStatus.CREATED
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.CREATE_SUCCESS
        assert (repo_for_test := res["data"])

        assert repo_for_test["id"]
        assert repo_for_test["created_at"]
        assert repo_for_test["updated_at"]
        assert repo_for_test["title"] == body["title"]
        assert repo_for_test["description"] == body["description"]
        assert repo_for_test["user_id"] == user_id

    @pytest.mark.asyncio
    async def test_update_todo_repo(self, testing_app, async_session: AsyncSession):
        # GIVEN
        user_id = helpers.user["user_id"]
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
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.UPDATE_SUCCESS
        assert (repo_for_test := res["data"])

        assert repo_before_update.id == repo_for_test["id"]
        assert repo_before_update.created_at == parse(repo_for_test["created_at"])
        assert repo_before_update.updated_at < parse(repo_for_test["updated_at"])
        assert repo_before_update.title != repo_for_test["title"] == body["title"]
        assert repo_before_update.description != repo_for_test["description"] == body["description"]
        assert user_id == repo_for_test["user_id"]

    @pytest.mark.asyncio
    async def test_update_todo_repo_if_not_sending_request_body(self, testing_app, async_session: AsyncSession):
        # GIVEN
        user_id = helpers.user["user_id"]
        repo = helpers.create_todo_repo(user_id=user_id)
        async_session.add(repo)
        await async_session.commit()

        # WHEN
        URL = testing_app.url_path_for("update_todo_repo", todo_repo_id=repo.id)

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.patch(URL)

        # THEN
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        res = response.json()
        assert res["ok"] is False
        assert res["message"]
        assert res["data"] is None

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
        res = response.json()
        assert res["ok"] is False
        assert res["message"]
        assert res["data"] is None

    @pytest.mark.asyncio
    async def test_get_todo_repos(self, testing_app, async_session: AsyncSession):
        # GIVEN
        user_id = helpers.user["user_id"]
        repos = helpers.create_todo_repos(user_id=user_id, n=20)
        async_session.add_all(repos)
        await async_session.commit()

        # WHEN
        URL = testing_app.url_path_for("get_todo_repos")

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.get(URL)

        # THEN
        assert response.status_code == HTTPStatus.OK
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.SUCCESS
        assert res["data"]
        assert res["paging"]
        assert res["paging"]["cursors"]
        assert res["paging"]["cursors"]["prev"] is None
        assert res["paging"]["cursors"]["next"] == 11
        assert res["paging"]["has_prev"] is False
        assert res["paging"]["has_next"] is True
        repos_for_test = res["data"]

        for repo, repo_for_test in zip(repos[-1::-1], repos_for_test):
            assert repo.id == repo_for_test["id"]
            assert repo.created_at == parse(repo_for_test["created_at"])
            assert repo.updated_at == parse(repo_for_test["updated_at"])
            assert repo.title == repo_for_test["title"]
            assert repo.description == repo_for_test["description"]
            assert repo.user_id == repo_for_test["user_id"]

    @pytest.mark.asyncio
    async def test_get_todo_repos_for_pagination(self, testing_app, async_session: AsyncSession):
        # GIVEN
        user_id = helpers.user["user_id"]
        n = 20
        page_size = 10
        repos = helpers.create_todo_repos(user_id=user_id, n=n)
        async_session.add_all(repos)
        await async_session.commit()

        # WHEN
        URL = testing_app.url_path_for("get_todo_repos")

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.get(utils.get_url_with_query_string(URL, cursor=None, page_size=page_size))

        # THEN
        assert response.status_code == HTTPStatus.OK
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.SUCCESS

        assert (data := res["data"])
        assert len(data) == page_size
        assert data[0]["id"] == 20
        assert data[-1]["id"] == 11

        assert res["paging"]
        assert res["paging"]["cursors"]
        assert res["paging"]["cursors"]["prev"] is None
        assert res["paging"]["cursors"]["next"] == 11
        assert res["paging"]["has_prev"] is False
        assert res["paging"]["has_next"] is True

        # WHEN
        next_cursor = res["paging"]["cursors"]["next"]
        URL = testing_app.url_path_for("get_todo_repos")

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.get(utils.get_url_with_query_string(URL, cursor=next_cursor, page_size=page_size))

        # THEN
        assert response.status_code == HTTPStatus.OK
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.SUCCESS

        assert (data := res["data"])
        assert len(data) == page_size
        assert data[0]["id"] == 10
        assert data[-1]["id"] == 1

        assert res["paging"]
        assert res["paging"]["cursors"]
        assert res["paging"]["cursors"]["prev"] == None
        assert res["paging"]["cursors"]["next"] == None
        assert res["paging"]["has_prev"] is True
        assert res["paging"]["has_next"] is False

        # WHEN
        prev_cursor = res["paging"]["cursors"]["prev"]
        URL = testing_app.url_path_for("get_todo_repos")

        async with AsyncClient(app=testing_app, base_url="http://test") as ac:
            response = await ac.get(utils.get_url_with_query_string(URL, cursor=prev_cursor, page_size=page_size))

        # THEN
        assert response.status_code == HTTPStatus.OK
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.SUCCESS

        assert (data := res["data"])
        assert len(data) == page_size
        assert data[0]["id"] == 20
        assert data[-1]["id"] == 11

        assert res["paging"]
        assert res["paging"]["cursors"]
        assert res["paging"]["cursors"]["prev"] is None
        assert res["paging"]["cursors"]["next"] == 11
        assert res["paging"]["has_prev"] is False
        assert res["paging"]["has_next"] is True


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
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.CREATE_SUCCESS
        assert (repo_for_test := res["data"])

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
        res = response.json()
        assert res["ok"] is False
        assert res["message"]
        assert res["data"] is None

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
        res = response.json()
        assert res["ok"] is False
        assert res["message"]
        assert res["data"] is None

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
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.SUCCESS
        assert (repo_for_test := res["data"])

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
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.CREATE_SUCCESS
        assert (daily_todo_task_for_test := res["data"])

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
        res = response.json()
        assert res["ok"] is False
        assert res["message"]
        assert res["data"] is None

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
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.SUCCESS
        assert (daily_todo_tasks_for_test := res["data"])

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
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.SUCCESS
        assert res["data"] == []

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
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.UPDATE_SUCCESS
        assert (daily_todo_task_for_test := res["data"])

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
        res = response.json()
        assert res["ok"] is False
        assert res["message"]
        assert res["data"] is None

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
        res = response.json()
        assert res["ok"] is False
        assert res["message"]
        assert res["data"] is None

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
        res = response.json()
        assert res["ok"]
        assert res["message"] == api_enums.ResponseMessage.UPDATE_SUCCESS
        assert (daily_todo_task_for_test := res["data"])

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
        res = response.json()
        assert res["ok"] is False
        assert res["message"]
        assert res["data"] is None

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
        res = response.json()
        assert res["ok"] is False
        assert res["message"]
        assert res["data"] is None
