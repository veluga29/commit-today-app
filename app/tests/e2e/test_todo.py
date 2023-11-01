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
