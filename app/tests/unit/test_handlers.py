import datetime
import random
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from copy import deepcopy

from app.tests import helpers
from app.domain.todo import models
from app.service.todo.handlers import TodoRepoService, DailyTodoService
from app.service import exceptions
from app.adapters.todo.repository import TodoRepoRepository, DailyTodoRepository


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
        with pytest.raises(exceptions.TodoRepoNotFound):
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


class TestDailyTodo:
    @pytest.mark.asyncio
    async def test_create_daily_todo(self, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        repo = helpers.create_todo_repo()
        async_session.add(repo)
        await async_session.commit()

        # WHEN
        todo_repo_repository = TodoRepoRepository(async_session)
        daily_todo_repository = DailyTodoRepository(async_session)
        res = await DailyTodoService.create_daily_todo(
            repo.id, date, todo_repo_repository=todo_repo_repository, daily_todo_repository=daily_todo_repository
        )
        q = await async_session.execute(select(models.DailyTodo).filter_by(todo_repo_id=repo.id, date=date))
        daily_todo = q.scalar()

        # THEN
        assert res
        assert daily_todo

        assert res["todo_repo_id"] == daily_todo.todo_repo_id
        assert res["date"] == daily_todo.date

    @pytest.mark.asyncio
    async def test_create_daily_todo_if_todo_repo_does_not_exist(self, async_session: AsyncSession):
        # GIVEN
        todo_repo_id = helpers.ID_MAX_LIMIT
        date = helpers.get_random_date()

        # WHEN
        todo_repo_repository = TodoRepoRepository(async_session)
        daily_todo_repository = DailyTodoRepository(async_session)
        with pytest.raises(exceptions.TodoRepoNotFound):
            # THEN
            await DailyTodoService.create_daily_todo(
                todo_repo_id,
                date,
                todo_repo_repository=todo_repo_repository,
                daily_todo_repository=daily_todo_repository,
            )

    @pytest.mark.asyncio
    async def test_create_daily_todo_if_daily_todo_already_exists(self, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()

        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        # WHEN
        todo_repo_repository = TodoRepoRepository(async_session)
        daily_todo_repository = DailyTodoRepository(async_session)
        with pytest.raises(exceptions.DailyTodoAlreadyExists):
            # THEN
            await DailyTodoService.create_daily_todo(
                todo_repo.id,
                date,
                todo_repo_repository=todo_repo_repository,
                daily_todo_repository=daily_todo_repository,
            )

    @pytest.mark.asyncio
    async def test_get_daily_todo(self, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        # WHEN
        repository = DailyTodoRepository(async_session)
        res = await DailyTodoService.get_daily_todo(todo_repo.id, date, repository=repository)

        # THEN
        assert res

        assert daily_todo.todo_repo_id == res["todo_repo_id"]
        assert daily_todo.date == res["date"]

    @pytest.mark.asyncio
    async def test_create_daily_todo_task(self, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        content = helpers.fake.text()

        # WHEN
        repository = DailyTodoRepository(async_session)
        res = await DailyTodoService.create_daily_todo_task(
            daily_todo.todo_repo_id, daily_todo.date, content, repository=repository
        )
        q = await async_session.execute(select(models.DailyTodoTask).filter_by(id=res["id"]))
        daily_todo_task = q.scalar()

        # THEN
        assert res
        assert daily_todo_task

        assert res["id"] == daily_todo_task.id
        assert res["created_at"] == daily_todo_task.created_at
        assert res["updated_at"] == daily_todo_task.updated_at
        assert res["content"] == daily_todo_task.content
        assert res["is_completed"] == daily_todo_task.is_completed
        assert res["todo_repo_id"] == daily_todo_task.todo_repo_id
        assert res["date"] == daily_todo_task.date

    @pytest.mark.asyncio
    async def test_create_daily_todo_task_if_there_is_no_daily_todo(self, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo_id = helpers.ID_MAX_LIMIT

        content = helpers.fake.text()

        # WHEN
        repository = DailyTodoRepository(async_session)
        with pytest.raises(exceptions.DailyTodoNotFound):
            # THEN
            await DailyTodoService.create_daily_todo_task(todo_repo_id, date, content, repository=repository)

    @pytest.mark.asyncio
    async def test_get_daily_todo_tasks(self, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        daily_todo_tasks = helpers.create_daily_todo_tasks(daily_todo=daily_todo)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        # WHEN
        repository = DailyTodoRepository(async_session)
        res_list = await DailyTodoService.get_daily_todo_tasks(
            daily_todo.todo_repo_id, daily_todo.date, repository=repository
        )

        # THEN
        assert res_list

        for daily_todo_task, res in zip(daily_todo_tasks, res_list):
            assert daily_todo_task.id == res["id"]
            assert daily_todo_task.created_at == res["created_at"]
            assert daily_todo_task.updated_at == res["updated_at"]
            assert daily_todo_task.content == res["content"]
            assert daily_todo_task.is_completed == res["is_completed"]
            assert daily_todo_task.todo_repo_id == res["todo_repo_id"]
            assert daily_todo_task.date == res["date"]

    @pytest.mark.asyncio
    async def test_get_daily_todo_tasks_if_there_are_no_tasks(self, async_session: AsyncSession):
        # GIVEN
        todo_repo_id = helpers.ID_MAX_LIMIT
        date = helpers.get_random_date()

        # WHEN
        repository = DailyTodoRepository(async_session)
        res_list = await DailyTodoService.get_daily_todo_tasks(todo_repo_id, date, repository=repository)

        # THEN
        assert res_list == []

    @pytest.mark.asyncio
    async def test_update_daily_todo_task_content(self, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        daily_todo_task = helpers.create_daily_todo_task(daily_todo=daily_todo)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()

        task_before_update = daily_todo_task.dict()
        content = "updated content"

        # WHEN
        repository = DailyTodoRepository(async_session)
        res = await DailyTodoService.update_daily_todo_task_content(
            daily_todo.todo_repo_id, daily_todo.date, daily_todo_task.id, content, repository=repository
        )

        # THEN
        assert res

        assert task_before_update["id"] == res["id"]
        assert task_before_update["created_at"] == res["created_at"]
        assert task_before_update["updated_at"] <= res["updated_at"]
        assert task_before_update["content"] != res["content"] == content
        assert task_before_update["is_completed"] == res["is_completed"]
        assert task_before_update["todo_repo_id"] == res["todo_repo_id"]
        assert task_before_update["date"] == res["date"]

    @pytest.mark.asyncio
    async def test_update_daily_todo_task_content_if_there_is_no_daily_todo(self, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo_id = helpers.ID_MAX_LIMIT
        daily_todo_task_id = helpers.ID_MAX_LIMIT
        content = "updated content"

        # WHEN
        repository = DailyTodoRepository(async_session)
        with pytest.raises(exceptions.DailyTodoNotFound):
            # THEN
            await DailyTodoService.update_daily_todo_task_content(
                todo_repo_id, date, daily_todo_task_id, content, repository=repository
            )

    @pytest.mark.asyncio
    async def test_update_daily_todo_task_content_if_there_is_no_daily_todo_task(self, async_session: AsyncSession):
        # GIVEN
        date = helpers.get_random_date()
        todo_repo = helpers.create_todo_repo()
        daily_todo = helpers.create_daily_todo(todo_repo=todo_repo, date=date)
        async_session.add_all([todo_repo, daily_todo])
        await async_session.commit()
        
        daily_todo_task_id = helpers.ID_MAX_LIMIT
        content = "updated content"

        # WHEN
        repository = DailyTodoRepository(async_session)
        with pytest.raises(exceptions.DailyTodoTaskNotFound):
            # THEN
            await DailyTodoService.update_daily_todo_task_content(
                todo_repo.id, date, daily_todo_task_id, content, repository=repository
            )
