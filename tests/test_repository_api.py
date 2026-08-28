from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def client(monkeypatch, root):
    monkeypatch.setenv("REPOSITORY_ROOT", str(root))
    return TestClient(app)


def test_health_and_preview_are_non_destructive(monkeypatch, tmp_path):
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "folder").mkdir()
    (tmp_path / "folder" / "b.txt").write_text("y")
    (tmp_path / ".git").mkdir()
    c = client(monkeypatch, tmp_path)
    assert c.get("/health").json() == {"status": "ok"}
    result = c.post("/api/preview").json()
    assert result["status"] == "preview"
    assert set(result["deleted"]) == {"a.txt", "folder", "folder/b.txt"}
    assert result["excluded"] == [".git"]
    assert (tmp_path / "a.txt").exists() and (tmp_path / ".git").exists()


def test_confirmation_requires_explicit_flag_and_then_deletes(monkeypatch, tmp_path):
    (tmp_path / "a").write_text("a")
    (tmp_path / ".git").mkdir()
    c = client(monkeypatch, tmp_path)
    preview = c.post("/api/preview").json()
    refused = c.post("/api/confirm", json={"preview_id": preview["preview_id"], "confirm": False}).json()
    assert refused["status"] == "failed" and (tmp_path / "a").exists()
    done = c.post("/api/confirm", json={"preview_id": preview["preview_id"], "confirm": True}).json()
    assert done["status"] == "confirmed"
    assert done["counts"] == {"deleted": 1, "excluded": 1, "remaining": 0}
    assert tmp_path.is_dir() and (tmp_path / ".git").is_dir() and not (tmp_path / "a").exists()


def test_symlink_in_tree_rejected_without_mutation(monkeypatch, tmp_path):
    target = tmp_path / "outside"
    target.write_text("safe")
    link = tmp_path / "link"
    try:
        link.symlink_to(target)
    except OSError:
        return
    result = client(monkeypatch, tmp_path).post("/api/preview").json()
    assert result["status"] == "failed"
    assert result["remaining_unknown"] is True
    assert target.exists()


def test_changed_tree_after_preview_is_rejected(monkeypatch, tmp_path):
    (tmp_path / "a").write_text("a")
    c = client(monkeypatch, tmp_path)
    preview = c.post("/api/preview").json()
    (tmp_path / "new").write_text("new")
    result = c.post("/api/confirm", json={"preview_id": preview["preview_id"], "confirm": True}).json()
    assert result["status"] == "failed"
    assert result["remaining_unknown"] is True
    assert (tmp_path / "a").exists() and (tmp_path / "new").exists()
