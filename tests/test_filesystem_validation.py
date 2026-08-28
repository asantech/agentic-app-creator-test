from fastapi.testclient import TestClient

from app.main import app


def test_missing_root_and_unsafe_configuration(monkeypatch, tmp_path):
    c = TestClient(app)
    monkeypatch.delenv("REPOSITORY_ROOT", raising=False)
    assert c.post("/api/preview").json()["status"] == "failed"
    monkeypatch.setenv("REPOSITORY_ROOT", str(tmp_path / "missing"))
    assert c.post("/api/preview").json()["status"] == "failed"


def test_symlink_parent_and_root_rejected(monkeypatch, tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    parent_link = tmp_path / "parent-link"
    root_link = tmp_path / "root-link"
    try:
        parent_link.symlink_to(tmp_path / "missing-parent", target_is_directory=True)
        root_link.symlink_to(real, target_is_directory=True)
    except OSError:
        return
    c = TestClient(app)
    monkeypatch.setenv("REPOSITORY_ROOT", str(root_link))
    assert c.post("/api/preview").json()["status"] == "failed"
    monkeypatch.setenv("REPOSITORY_ROOT", str(parent_link / "child"))
    assert c.post("/api/preview").json()["status"] == "failed"


def test_absolute_and_parent_traversal_are_not_user_inputs(monkeypatch, tmp_path):
    monkeypatch.setenv("REPOSITORY_ROOT", str(tmp_path / ".." / tmp_path.name))
    # The configured path itself contains parent traversal and is rejected.
    assert TestClient(app).post("/api/preview").json()["status"] == "failed"


def test_ui_is_persian_rtl_and_two_stage(monkeypatch, tmp_path):
    monkeypatch.setenv("REPOSITORY_ROOT", str(tmp_path))
    html = TestClient(app).get("/").text
    assert 'dir="rtl"' in html
    assert "پیش‌نمایش" in html and "تأیید و حذف واقعی" in html
    assert "confirm" in html and "/api/preview" in TestClient(app).get("/static/app.js").text
