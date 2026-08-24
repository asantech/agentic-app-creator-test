from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_health_returns_successful_json() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_home_references_local_stylesheet() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert '<link rel="stylesheet" href="/app.css">' in response.text


@pytest.mark.anyio
async def test_stylesheet_is_served_and_has_red_body_background() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/app.css")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")
    assert "body" in response.text
    assert "background-color: red;" in response.text
    assert Path("app.css").read_text(encoding="utf-8") == response.text
