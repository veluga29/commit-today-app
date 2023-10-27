from fastapi import FastAPI

from app import settings
from app.entrypoints.fastapi.api_v1.router import api_router as api_v1_router

app = FastAPI(
    title="Commit Today: TODO List with Progress Visualization",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(api_v1_router)


@app.get("/")
async def health_check():
    return {"ping": "pong"}
