from fastapi import FastAPI

from app import settings

app = FastAPI(
    title="Commit Today: TODO List with Progress Visualization",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


@app.get("/")
def health_check():
    return {"ping": "pong"}
