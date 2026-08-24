from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
ROOT = Path(__file__).resolve().parent.parent


def test_health_endpoint_returns_success() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_css_file_contains_purple_color() -> None:
    css = (ROOT / "app.css").read_text(encoding="utf-8")

    assert "color: purple;" in css


def test_css_route_returns_css_content() -> None:
    response = client.get("/app.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert "color: purple;" in response.text


def test_homepage_references_stylesheet() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert 'href="/app.css"' in response.text
