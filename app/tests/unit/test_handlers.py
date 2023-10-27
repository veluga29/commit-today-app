import random
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests import helpers
from app.domain.todo import models
from app.service.todo.handlers import TodoRepoService
from app.adapters.todo.repository import TodoRepoRepository


@pytest.mark.asyncio
async def test_create_todo_repo(async_session: AsyncSession):
    # GIVEN
    user_id = random.choice(range(1, 100))
    title = helpers.fake.word()
    description = helpers.fake.text()

    # WHEN
    repository = TodoRepoRepository(async_session)
    res = await TodoRepoService.create_todo_repo(title, description, user_id, repository=repository)
    q = await async_session.execute(select(models.TodoRepo).filter_by(id=res["id"]))
    repo = q.scalar()

    # THEN
    assert res
    assert repo

    assert res["id"] == repo.id
    assert res["created_at"] == repo.created_at
    assert res["updated_at"] == repo.updated_at
    assert res["title"] == repo.title
    assert res["description"] == repo.description
    assert res["user_id"] == repo.user_id


# @pytest.mark.asyncio
# async def test_create_todo_repo_if_repo_already_exists(async_session: AsyncSession):
#     # GIVEN
#     user_id = random.choice(range(1, 100))
#     title = helpers.fake.title()
#     description = helpers.fake.text()

#     repo = helpers.create_todo_repo(user_id)
#     async_session.add(repo)
#     await async_session.commit()

#     # WHEN
#     repository = TodoRepoRepository(async_session)
#     with pytest.raises(exceptions.AlreadyExists):
#         # THEN
#         res = await TodoService.create_todo_repo(title, description, user_id, repository=repository)
