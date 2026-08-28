from fastapi.testclient import TestClient

from app.main import app


def test_health_and_rtl_page():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    page = client.get("/").text
    assert 'dir="rtl"' in page
    assert "پیش‌نمایش" in page
    assert "/api/preview" in client.get("/static/app.js").text
    assert client.get("/static/style.css").status_code == 200


def test_preview_and_confirmation_api(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    (tmp_path / "file.txt").write_text("data")
    monkeypatch.setenv("SANDBOX_ROOT", str(tmp_path))
    monkeypatch.setenv("REPOSITORY_ROOT", str(tmp_path))
    client = TestClient(app)
    preview = client.get("/api/preview")
    assert preview.status_code == 200
    assert preview.json()["deleted"] == []
    assert (tmp_path / "file.txt").exists()
    rejected = client.post("/api/delete", json={"confirmation": False})
    assert rejected.status_code == 400
    assert (tmp_path / "file.txt").exists()
    done = client.post("/api/delete", json={"confirmation": True})
    assert done.status_code == 200
    body = done.json()
    assert body["status"] == "completed"
    assert body["counts"]["deleted"] >= 1
    assert not (tmp_path / "file.txt").exists()
    assert (tmp_path / ".git").exists()


def test_unconfigured_root_is_structured_error(monkeypatch):
    monkeypatch.delenv("REPOSITORY_ROOT", raising=False)
    monkeypatch.delenv("SANDBOX_ROOT", raising=False)
    response = TestClient(app).get("/api/preview")
    assert response.status_code == 400
    assert response.json()["detail"]["status"] == "failed"
