import datetime
from fastapi import APIRouter, status, Depends, Path, Body, HTTPException
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from app.entrypoints.fastapi.api_v1.todo import in_schemas
from app.entrypoints.fastapi.api_v1.todo import out_schemas
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
    async def create_todo_repo(self, create_in: in_schemas.TodoRepoCreateIn) -> out_schemas.TodoRepoCreateOut:
        repository: TodoRepoRepository = TodoRepoRepository(self.session)
        res = await self.todo_service.create_todo_repo(create_in.title, create_in.description, repository=repository)

        return out_schemas.TodoRepoCreateOut(**res)

    @router.patch("/todo-repos/{todo_repo_id}", status_code=status.HTTP_200_OK)
    async def update_todo_repo(
        self, todo_repo_id: int = Path(...), update_in: in_schemas.TodoRepoUpdateIn = Body(...)
    ) -> out_schemas.TodoRepoUpdateOut:
        try:
            repository: TodoRepoRepository = TodoRepoRepository(self.session)
            res = await self.todo_service.update_todo_repo(
                todo_repo_id, update_in.title, update_in.description, repository=repository
            )
        except exceptions.NotFound:
            raise HTTPException(status_code=404, detail="Todo Repo not found")

        return out_schemas.TodoRepoUpdateOut(**res)

    @router.get("/todo-repos", status_code=status.HTTP_200_OK)
    async def get_todo_repos(self) -> list[out_schemas.TodoRepoOut]:
        repository: TodoRepoRepository = TodoRepoRepository(self.session)
        res = await self.todo_service.get_todo_repos(repository=repository)

        return [out_schemas.TodoRepoOut(**r) for r in res]


@cbv(router)
class DailyTodo:
    session: AsyncSession = Depends(get_session)
    daily_todo_service: DailyTodoService = Depends()

    @router.post("/todo-repos/{todo_repo_id}/daily-todos", status_code=status.HTTP_201_CREATED)
    async def create_daily_todo(
        self, todo_repo_id: int = Path(), date: datetime.date = Body(embed=True)
    ) -> out_schemas.DailyTodoCreateOut:
        try:
            todo_repo_repository: TodoRepoRepository = TodoRepoRepository(self.session)
            daily_todo_repository: DailyTodoRepository = DailyTodoRepository(self.session)
            res = await self.daily_todo_service.create_daily_todo(
                todo_repo_id=todo_repo_id,
                date=date,
                todo_repo_repository=todo_repo_repository,
                daily_todo_repository=daily_todo_repository,
            )
        except exceptions.NotFound:
            raise HTTPException(status_code=404, detail="Todo Repo not found")
        except exceptions.AlreadyExists:
            raise HTTPException(status_code=400, detail="DailyTodo already exists")

        return out_schemas.DailyTodoCreateOut(**res)
