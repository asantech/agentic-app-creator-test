from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from .config import ConfigurationError, configured_repository_root, validate_candidate_root

IMMUTABLE_NAMES = frozenset({".git"})


class InventoryError(RuntimeError):
    pass


@dataclass
class Inventory:
    root: Path
    deletable: list[str]
    excluded: list[str]


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def inventory(root: Path | None = None) -> Inventory:
    try:
        checked = configured_repository_root() if root is None else validate_candidate_root(root)
        deletable: list[str] = []
        excluded: list[str] = []

        def visit(directory: Path) -> None:
            try:
                children = sorted(directory.iterdir(), key=lambda item: item.name)
            except OSError as exc:
                raise InventoryError(f"cannot read {directory}: {exc}") from exc
            for child in children:
                relative = _relative(child, checked)
                if child.is_symlink():
                    raise InventoryError(f"symlink target rejected: {relative}")
                if child.name in IMMUTABLE_NAMES and child.parent == checked:
                    excluded.append(relative)
                    continue
                deletable.append(relative)
                if child.is_dir():
                    visit(child)

        visit(checked)
        return Inventory(checked, deletable, excluded)
    except ConfigurationError as exc:
        raise InventoryError(str(exc)) from exc


def _safe_path(root: Path, relative: str) -> Path:
    candidate = root / Path(relative)
    if not candidate.is_relative_to(root) or ".." in Path(relative).parts:
        raise InventoryError(f"invalid target path: {relative}")
    if candidate.is_symlink():
        raise InventoryError(f"symlink target rejected: {relative}")
    return candidate


def delete_confirmed() -> dict[str, object]:
    """Re-inventory immediately before mutation and remove only verified children."""
    first = inventory()
    root = first.root
    # Delete deepest entries first. A second inventory prevents preview-time races.
    paths = sorted(first.deletable, key=lambda item: (len(Path(item).parts), item), reverse=True)
    deleted: list[str] = []
    failures: list[dict[str, str]] = []
    for relative in paths:
        try:
            target = _safe_path(root, relative)
            if not target.exists() and not target.is_symlink():
                continue
            if target.is_dir():
                # The complete subtree was checked and contains no symlink.
                shutil.rmtree(target)
            else:
                target.unlink()
            deleted.append(relative)
        except (OSError, InventoryError) as exc:
            failures.append({"path": relative, "error": str(exc)})

    try:
        after = inventory(root)
        remaining = len(after.deletable)
        excluded = after.excluded
    except InventoryError as exc:
        remaining = None
        excluded = first.excluded
        failures.append({"path": ".", "error": str(exc)})
    return {
        "root": str(root),
        "deleted": sorted(deleted),
        "excluded": excluded,
        "failures": failures,
        "remaining": remaining,
    }
