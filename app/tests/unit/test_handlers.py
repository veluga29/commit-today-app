import random
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from copy import deepcopy

from app.tests import helpers
from app.domain.todo import models
from app.service.todo.handlers import TodoRepoService
from app.service import exceptions
from app.adapters.todo.repository import TodoRepoRepository


class TestTodoRepo:
    @pytest.mark.asyncio
    async def test_create_todo_repo(self, async_session: AsyncSession):
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

    @pytest.mark.asyncio
    async def test_update_todo_repo(self, async_session: AsyncSession):
        # GIVEN
        user_id = random.choice(range(1, 100))
        repo = helpers.create_todo_repo(user_id=user_id)
        async_session.add(repo)
        await async_session.commit()

        repo_before_update = deepcopy(repo)

        title = helpers.fake.word()
        description = helpers.fake.text()

        # WHEN
        repository = TodoRepoRepository(async_session)
        res = await TodoRepoService.update_todo_repo(repo.id, title, description, repository=repository)

        # THEN
        assert res

        assert repo_before_update.id == res["id"]
        assert repo_before_update.created_at == res["created_at"]
        assert repo_before_update.updated_at < res["updated_at"]
        assert repo_before_update.title != res["title"]
        assert repo_before_update.description != res["description"]
        assert repo_before_update.user_id == res["user_id"]

    @pytest.mark.asyncio
    async def test_update_todo_repo_if_repo_does_not_exist(self, async_session: AsyncSession):
        # GIVEN
        repo_id = helpers.ID_MAX_LIMIT
        title = helpers.fake.word()
        description = helpers.fake.text()

        # WHEN
        repository = TodoRepoRepository(async_session)
        with pytest.raises(exceptions.NotFound):
            # THEN
            await TodoRepoService.update_todo_repo(repo_id, title, description, repository=repository)
        
    @pytest.mark.asyncio
    async def test_get_todo_repos(self, async_session: AsyncSession):
        # GIVEN
        # user_id = random.choice(range(1, 100))  # TODO
        repos = helpers.create_todo_repos(n=20)
        async_session.add_all(repos)
        await async_session.commit()

        # WHEN
        repository = TodoRepoRepository(async_session)
        res_list = await TodoRepoService.get_todo_repos(0, repository=repository)

        # THEN
        assert res_list

        for repo, res in zip(repos, res_list):
            assert repo.id == res["id"]
            assert repo.created_at == res["created_at"]
            assert repo.updated_at == res["updated_at"]
            assert repo.title == res["title"]
            assert repo.description == res["description"]
            assert repo.user_id == res["user_id"]
