import datetime
from fastapi import APIRouter, status, Depends, Path, Body, HTTPException
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from app.entrypoints.fastapi.api_v1.todo import in_schemas, out_schemas
from app.entrypoints.fastapi.api_v1 import schemas as general_schemas, examples
from app.entrypoints.fastapi.api_v1.todo import enums
from app.service.todo.handlers import TodoRepoService, DailyTodoService
from app.service import exceptions
from app.adapters.todo.repository import TodoRepoRepository, DailyTodoRepository
from app.db import get_session


router = APIRouter()


@cbv(router)
class TodoRepo:
    session: AsyncSession = Depends(get_session)
    todo_service: TodoRepoService = Depends()

    @router.post("/todo-repos", status_code=status.HTTP_201_CREATED)
    async def create_todo_repo(self, create_in: in_schemas.TodoRepoCreateIn) -> out_schemas.TodoRepoResponse:
        repository: TodoRepoRepository = TodoRepoRepository(self.session)
        res = await self.todo_service.create_todo_repo(create_in.title, create_in.description, repository=repository)

        return out_schemas.TodoRepoResponse(
            ok=True, message=enums.ResponseMessage.CREATE_SUCCESS, data=out_schemas.TodoRepoOut(**res)
        )

    @router.patch(
        "/todo-repos/{todo_repo_id}",
        status_code=status.HTTP_200_OK,
        responses=examples.get_error_responses([status.HTTP_404_NOT_FOUND]),
    )
    async def update_todo_repo(
        self, todo_repo_id: int = Path(...), update_in: in_schemas.TodoRepoUpdateIn = Body(...)
    ) -> out_schemas.TodoRepoResponse:
        try:
            repository: TodoRepoRepository = TodoRepoRepository(self.session)
            res = await self.todo_service.update_todo_repo(
                todo_repo_id, update_in.title, update_in.description, repository=repository
            )
        except exceptions.TodoRepoNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        return out_schemas.TodoRepoResponse(
            ok=True, message=enums.ResponseMessage.UPDATE_SUCCESS, data=out_schemas.TodoRepoOut(**res)
        )

    @router.get("/todo-repos", status_code=status.HTTP_200_OK)
    async def get_todo_repos(
        self, pagination: general_schemas.PaginationQueryParams = Depends()
    ) -> out_schemas.TodoRepoPaginationResponse:
        repository: TodoRepoRepository = TodoRepoRepository(self.session)
        res = await self.todo_service.get_todo_repos(
            cursor=pagination.cursor, page_size=pagination.page_size, repository=repository
        )

        return out_schemas.TodoRepoPaginationResponse(ok=True, message=enums.ResponseMessage.SUCCESS, **res)


@cbv(router)
class DailyTodo:
    session: AsyncSession = Depends(get_session)
    daily_todo_service: DailyTodoService = Depends()

    @router.post(
        "/todo-repos/{todo_repo_id}/daily-todos",
        status_code=status.HTTP_201_CREATED,
        responses=examples.get_error_responses([status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]),
    )
    async def create_daily_todo(
        self, todo_repo_id: int = Path(), date: datetime.date = Body(embed=True)
    ) -> out_schemas.DailyTodoResponse:
        try:
            todo_repo_repository: TodoRepoRepository = TodoRepoRepository(self.session)
            daily_todo_repository: DailyTodoRepository = DailyTodoRepository(self.session)
            res = await self.daily_todo_service.create_daily_todo(
                todo_repo_id=todo_repo_id,
                date=date,
                todo_repo_repository=todo_repo_repository,
                daily_todo_repository=daily_todo_repository,
            )
        except exceptions.TodoRepoNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
        except exceptions.DailyTodoAlreadyExists as e:
            raise HTTPException(status_code=400, detail=str(e))

        return out_schemas.DailyTodoResponse(
            ok=True, message=enums.ResponseMessage.CREATE_SUCCESS, data=out_schemas.DailyTodoOut(**res)
        )

    @router.get(
        "/todo-repos/{todo_repo_id}/daily-todos/{date}",
        status_code=status.HTTP_200_OK,
        responses=examples.get_error_responses([status.HTTP_404_NOT_FOUND]),
    )
    async def get_daily_todo(
        self, todo_repo_id: int = Path(), date: datetime.date = Path()
    ) -> out_schemas.DailyTodoResponse:
        try:
            repository: DailyTodoRepository = DailyTodoRepository(self.session)
            res = await self.daily_todo_service.get_daily_todo(
                todo_repo_id=todo_repo_id,
                date=date,
                repository=repository,
            )
        except exceptions.DailyTodoNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        return out_schemas.DailyTodoResponse(
            ok=True, message=enums.ResponseMessage.SUCCESS, data=out_schemas.DailyTodoOut(**res)
        )

    @router.post(
        "/todo-repos/{todo_repo_id}/daily-todos/{date}/daily-todo-tasks",
        status_code=status.HTTP_201_CREATED,
        responses=examples.get_error_responses([status.HTTP_404_NOT_FOUND]),
    )
    async def create_daily_todo_task(
        self, todo_repo_id: int = Path(), date: datetime.date = Path(), content: str = Body(embed=True)
    ) -> out_schemas.DailyTodoTaskResponse:
        try:
            repository: DailyTodoRepository = DailyTodoRepository(self.session)
            res = await self.daily_todo_service.create_daily_todo_task(
                todo_repo_id=todo_repo_id,
                date=date,
                content=content,
                repository=repository,
            )
        except exceptions.DailyTodoNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        return out_schemas.DailyTodoTaskResponse(
            ok=True, message=enums.ResponseMessage.CREATE_SUCCESS, data=out_schemas.DailyTodoTaskOut(**res)
        )

    @router.get("/todo-repos/{todo_repo_id}/daily-todos/{date}/daily-todo-tasks", status_code=status.HTTP_200_OK)
    async def get_daily_todo_tasks(
        self, todo_repo_id: int = Path(), date: datetime.date = Path()
    ) -> out_schemas.DailyTodoTasksResponse:
        repository: DailyTodoRepository = DailyTodoRepository(self.session)
        res = await self.daily_todo_service.get_daily_todo_tasks(
            todo_repo_id=todo_repo_id,
            date=date,
            repository=repository,
        )

        return out_schemas.DailyTodoTasksResponse(
            ok=True, message=enums.ResponseMessage.SUCCESS, data=[out_schemas.DailyTodoTaskOut(**r) for r in res]
        )

    @router.patch(
        "/todo-repos/{todo_repo_id}/daily-todos/{date}/daily-todo-tasks/{daily_todo_task_id}/content",
        status_code=status.HTTP_200_OK,
        responses=examples.get_error_responses([status.HTTP_404_NOT_FOUND]),
    )
    async def update_daily_todo_task_for_content(
        self,
        todo_repo_id: int = Path(),
        date: datetime.date = Path(),
        daily_todo_task_id: int = Path(),
        content: str = Body(embed=True),
    ) -> out_schemas.DailyTodoTaskResponse:
        try:
            repository: DailyTodoRepository = DailyTodoRepository(self.session)
            res = await self.daily_todo_service.update_daily_todo_task_for_content(
                todo_repo_id=todo_repo_id,
                date=date,
                daily_todo_task_id=daily_todo_task_id,
                content=content,
                repository=repository,
            )
        except exceptions.DailyTodoNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
        except exceptions.DailyTodoTaskNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        return out_schemas.DailyTodoTaskResponse(
            ok=True, message=enums.ResponseMessage.UPDATE_SUCCESS, data=out_schemas.DailyTodoTaskOut(**res)
        )

    @router.patch(
        "/todo-repos/{todo_repo_id}/daily-todos/{date}/daily-todo-tasks/{daily_todo_task_id}/is-completed",
        status_code=status.HTTP_200_OK,
    )
    async def update_daily_todo_task_for_is_completed(
        self,
        todo_repo_id: int = Path(),
        date: datetime.date = Path(),
        daily_todo_task_id: int = Path(),
        is_completed: bool = Body(embed=True),
    ) -> out_schemas.DailyTodoTaskOut:
        try:
            repository: DailyTodoRepository = DailyTodoRepository(self.session)
            res = await self.daily_todo_service.update_daily_todo_task_for_is_completed(
                todo_repo_id=todo_repo_id,
                date=date,
                daily_todo_task_id=daily_todo_task_id,
                is_completed=is_completed,
                repository=repository,
            )
        except exceptions.DailyTodoNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))
        except exceptions.DailyTodoTaskNotFound as e:
            raise HTTPException(status_code=404, detail=str(e))

        return out_schemas.DailyTodoTaskOut(**res)
