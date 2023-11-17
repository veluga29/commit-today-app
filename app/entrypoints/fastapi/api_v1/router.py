from fastapi import APIRouter

from app.entrypoints.fastapi.api_v1.todo.todo import router as todo_router
from app.entrypoints.fastapi.api_v1.auth.auth import router as user_router
from app import settings

api_router = APIRouter(prefix=settings.API_V1_STR)
external_router = APIRouter()
internal_router = APIRouter()

external_router.include_router(todo_router, prefix="/todo", tags=["todo"])
external_router.include_router(user_router, prefix="/auth", tags=["auth"])

api_router.include_router(external_router, prefix="/external")
api_router.include_router(internal_router, prefix="/internal")
