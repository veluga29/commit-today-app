import random
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus

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


# @pytest.mark.asyncio
# async def test_create_todo_repo_if_repo_already_exists(client: TestClient, async_session: AsyncSession):
#     # GIVEN
#     user_id = random.choice(range(1, 100))
#     repo = helpers.create_todo_repo(user_id)
#     async_session.add(repo)
#     await async_session.commit()

#     # WHEN
#     body = {"title": helpers.fake.title(), "description": helpers.fake.text()}

#     response = client.post(
#         f"{settings.API_V1_STR}/todo-repos",
#         json=body,
#     )
#     q = await async_session.execute(select(models.TodoRepo).filter_by(user_id=user_id))
#     repo = q.scalar()

#     # THEN
#     assert response.status_code == HTTPStatus.BAD_REQUEST
