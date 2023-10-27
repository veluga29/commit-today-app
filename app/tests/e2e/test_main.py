import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_main(testing_app):
    URL = testing_app.url_path_for("health_check")
    async with AsyncClient(app=testing_app, base_url="http://test") as ac:
        response = await ac.get(URL)

    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
