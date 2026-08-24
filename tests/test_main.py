from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_page_is_persian_cleanup_form():
    response = client.get("/")
    assert response.status_code == 200
    assert "دامنه پاک‌سازی ریپو" in response.text
    assert "فقط پیش‌نمایش" in response.text


def test_preview_requires_explicit_confirmation():
    response = client.post("/api/preview", json={})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "confirmation_required"
    assert body["destructive_action_performed"] is False


def test_preview_reports_selected_scope_without_deleting():
    response = client.post(
        "/api/preview",
        json={
            "delete_working_files": True,
            "delete_hidden_files": True,
            "preserve_git_metadata": True,
            "preserve_app_skeleton": False,
            "explicit_confirmation": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "preview_only"
    assert len(body["included"]) == 3
    assert "متادیتای Git مانند .git" in body["preserved"]
    assert body["destructive_action_performed"] is False


def test_unknown_fields_are_rejected():
    response = client.post("/api/preview", json={"unexpected": True})
    assert response.status_code == 422
