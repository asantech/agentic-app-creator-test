from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_success() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_homepage_serves_persian_form() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert 'lang="fa"' in response.text
    assert 'dir="rtl"' in response.text
    assert "ارسال پیام" in response.text
    assert "نام و نام خانوادگی" in response.text
    assert 'id="contact-form"' in response.text


def test_form_technical_attributes_are_preserved() -> None:
    html = client.get("/").text

    assert 'id="name" name="name" type="text"' in html
    assert 'id="email" name="email" type="email"' in html
    assert 'id="message" name="message"' in html
    assert "addEventListener('submit'" in html
