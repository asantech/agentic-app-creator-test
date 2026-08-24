from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_references_local_stylesheet() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert '<link rel="stylesheet" href="/static/app.css">' in response.text


def test_stylesheet_is_served_and_non_empty() -> None:
    response = client.get("/static/app.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert "@media" in response.text
    assert "body" in response.text
    assert len(response.content) > 100
