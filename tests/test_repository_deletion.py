from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def make_repo(tmp_path, monkeypatch):
    root = tmp_path / "sandbox"
    root.mkdir()
    repo = root / "repo"
    repo.mkdir()
    (repo / "file.txt").write_text("data")
    (repo / "folder").mkdir()
    (repo / "folder" / "nested.txt").write_text("nested")
    (repo / ".git").mkdir()
    (repo / ".git" / "config").write_text("immutable")
    monkeypatch.setenv("SANDBOX_ROOT", str(root))
    return repo


def test_health_and_entrypoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_preview_does_not_mutate(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, monkeypatch)
    response = client.post("/preview", json={"repo_path": "repo"})
    assert response.status_code == 200
    body = response.json()
    assert body["mutated"] is False
    assert set(body["deletable"]) == {"file.txt", "folder"}
    assert any(item.startswith(".git") for item in body["excluded"])
    assert (repo / "file.txt").exists()
    assert (repo / "folder" / "nested.txt").exists()


def test_delete_requires_confirmation_without_mutation(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, monkeypatch)
    response = client.post("/delete", json={"repo_path": "repo"})
    assert response.status_code == 400
    assert (repo / "file.txt").exists()


def test_confirmed_delete_preserves_root_and_git(tmp_path, monkeypatch):
    repo = make_repo(tmp_path, monkeypatch)
    response = client.post("/delete", json={"repo_path": "repo", "confirmation": "DELETE"})
    assert response.status_code == 200
    body = response.json()
    assert set(body["deleted"]) == {"file.txt", "folder"}
    assert any(item.startswith(".git") for item in body["excluded"])
    assert body["remaining"] == [".git"]
    assert repo.exists()
    assert (repo / ".git" / "config").exists()


def test_rejects_absolute_and_traversal_paths(tmp_path, monkeypatch):
    make_repo(tmp_path, monkeypatch)
    assert client.post("/preview", json={"repo_path": str(tmp_path / "outside")}).status_code == 400
    assert client.post("/preview", json={"repo_path": "../repo"}).status_code == 400


def test_rejects_symlink_repository(tmp_path, monkeypatch):
    root = tmp_path / "sandbox"
    root.mkdir()
    actual = tmp_path / "actual"
    actual.mkdir()
    (actual / "file.txt").write_text("x")
    (root / "link").symlink_to(actual, target_is_directory=True)
    monkeypatch.setenv("SANDBOX_ROOT", str(root))
    response = client.post("/preview", json={"repo_path": "link"})
    assert response.status_code == 400


def test_requires_explicit_sandbox_root_for_preview_and_delete(tmp_path, monkeypatch):
    monkeypatch.delenv("SANDBOX_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "file.txt").write_text("data")

    preview = client.post("/preview", json={"repo_path": "repo"})
    delete = client.post(
        "/delete", json={"repo_path": "repo", "confirmation": "DELETE"}
    )

    assert preview.status_code == 400
    assert delete.status_code == 400
    assert (repo / "file.txt").exists()


def test_rejects_symlink_ancestor_of_sandbox_root(tmp_path, monkeypatch):
    actual_parent = tmp_path / "actual-parent"
    actual_parent.mkdir()
    root = actual_parent / "sandbox"
    root.mkdir()
    (root / "repo").mkdir()
    (root / "repo" / "file.txt").write_text("data")

    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(actual_parent, target_is_directory=True)
    monkeypatch.setenv("SANDBOX_ROOT", str(linked_parent / "sandbox"))

    preview = client.post("/preview", json={"repo_path": "repo"})
    delete = client.post(
        "/delete", json={"repo_path": "repo", "confirmation": "DELETE"}
    )

    assert preview.status_code == 400
    assert delete.status_code == 400
    assert (root / "repo" / "file.txt").exists()


def test_html_contains_required_controls():
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="repoPath"' in response.text
    assert 'id="previewButton"' in response.text
    assert 'id="confirm"' in response.text
    assert "حذف واقعی" in response.text
    assert 'dir="rtl"' in response.text
