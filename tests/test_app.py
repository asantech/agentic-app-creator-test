from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_page_references_local_stylesheet() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert '<link rel="stylesheet" href="/app.css">' in response.text


def test_stylesheet_contains_only_purple_body_rule() -> None:
    response = client.get("/app.css")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")
    assert response.text == "body { color: purple; }\n"
