from pathlib import Path

import pytest

from app.config import ConfigurationError, validate_candidate_root
from app.repository import InventoryError, delete_confirmed, inventory


def test_preview_does_not_mutate_and_excludes_git(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "folder").mkdir()
    (tmp_path / "folder" / "b.txt").write_text("y")
    result = inventory(tmp_path)
    assert result.excluded == [".git"]
    assert set(result.deletable) == {"a.txt", "folder", "folder/b.txt"}
    assert (tmp_path / "a.txt").exists()


def test_confirmed_delete_preserves_root_and_git(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    (tmp_path / "a").write_text("x")
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "b").write_text("y")
    monkeypatch.setenv("SANDBOX_ROOT", str(tmp_path))
    monkeypatch.setenv("REPOSITORY_ROOT", str(tmp_path))
    outcome = delete_confirmed()
    assert outcome["remaining"] == 0
    assert tmp_path.exists() and (tmp_path / ".git").exists()
    assert not (tmp_path / "a").exists()


def test_rejects_traversal_and_symlinks(tmp_path):
    with pytest.raises(ConfigurationError):
        validate_candidate_root(Path(str(tmp_path) + "/../other"))
    target = tmp_path / "real"
    target.mkdir()
    link = tmp_path / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    with pytest.raises(ConfigurationError):
        validate_candidate_root(link)


def test_inventory_rejects_nested_symlink_without_following(tmp_path):
    (tmp_path / "folder").mkdir()
    outside = tmp_path.parent / "outside-file"
    outside.write_text("safe")
    try:
        (tmp_path / "folder" / "link").symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    with pytest.raises(InventoryError):
        inventory(tmp_path)
    assert outside.read_text() == "safe"
