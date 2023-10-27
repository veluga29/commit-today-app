from fastapi import APIRouter, status, Depends
from fastapi_restful.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from app.entrypoints.fastapi.api_v1.todo import in_schemas
from app.entrypoints.fastapi.api_v1.todo import out_schemas
from app.service.todo.handlers import TodoRepoService
from app.adapters.todo.repository import TodoRepoRepository
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
