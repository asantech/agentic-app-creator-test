from pathlib import Path

from fastapi.testclient import TestClient

from app.main import PROJECT_ROOT, app, project_inventory


client = TestClient(app)


def test_health_returns_success() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_page_contains_report() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "گزارش عملیات حذف فایل‌ها" in response.text
    assert "app.main:app" in response.text


def test_status_is_pending_and_matches_real_inventory() -> None:
    before = project_inventory()
    response = client.get("/api/status")
    after = project_inventory()

    assert response.status_code == 200
    payload = response.json()
    assert payload["operation_state"] == "در انتظار تأیید دامنه و استثناها"
    assert payload["confirmation_required"] is True
    assert payload["deletion_performed"] is False
    assert payload["deleted_items"] == []
    assert payload["pre_operation_inventory"] == before
    assert payload["remaining_items"] == before
    assert payload["preserved_items"] == before
    assert after == before
    assert "app/main.py" in before
    assert "app/__init__.py" in before
    assert all(not item.startswith("../") for item in before)


def test_inventory_is_limited_to_project_root() -> None:
    outside = Path(PROJECT_ROOT).parent / "outside-inventory-sentinel.txt"
    assert outside.as_posix() not in project_inventory()
    assert "مسیرهای خارج از ریشهٔ پروژه" in client.get("/api/status").json()["out_of_scope"][0]


def test_status_declares_scope_policies() -> None:
    rules = client.get("/api/status").json()["scope_rules"]
    assert any("مخفی" in rule for rule in rules)
    assert any("وابستگی" in rule for rule in rules)
    assert any("تولیدشده" in rule for rule in rules)
    assert any("app/main.py" in rule for rule in rules)
