from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import settings
from app.entrypoints.fastapi.api_v1.router import api_router as api_v1_router
from app.entrypoints.fastapi.api_v1 import schemas

app = FastAPI(
    title="Commit Today: TODO List with Progress Visualization",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(api_v1_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=schemas.Response(ok=False, message=str(exc.detail), data=None).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=schemas.Response(ok=False, message=str(exc), data=None).model_dump(),
    )


@app.get("/")
async def health_check():
    return {"ping": "pong"}
