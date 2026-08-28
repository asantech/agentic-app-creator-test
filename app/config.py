from __future__ import annotations

import os
from pathlib import Path


class ConfigurationError(ValueError):
    """Raised when the configured repository is unsafe or invalid."""


def _absolute_without_traversal(value: str, label: str) -> Path:
    if not value:
        raise ConfigurationError(f"{label} is not configured")
    path = Path(value)
    if not path.is_absolute():
        raise ConfigurationError(f"{label} must be an absolute path")
    if ".." in path.parts:
        raise ConfigurationError(f"{label} must not contain parent traversal")
    return path


def _has_symlink_component(path: Path) -> bool:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            return True
    return False


def _validate_sandbox(sandbox: Path) -> Path:
    if _has_symlink_component(sandbox):
        raise ConfigurationError("SANDBOX_ROOT contains a symlink")
    if not sandbox.exists():
        raise ConfigurationError("sandbox root does not exist")
    if not sandbox.is_dir():
        raise ConfigurationError("sandbox root is not a directory")
    return sandbox


def configured_repository_root() -> Path:
    """Return and validate the explicitly configured sandbox-local repository."""
    root = _absolute_without_traversal(
        os.environ.get("REPOSITORY_ROOT", ""), "REPOSITORY_ROOT"
    )
    sandbox = _absolute_without_traversal(
        os.environ.get("SANDBOX_ROOT", ""), "SANDBOX_ROOT"
    )
    _validate_sandbox(sandbox)

    if _has_symlink_component(root):
        raise ConfigurationError("REPOSITORY_ROOT contains a symlink")
    try:
        root.relative_to(sandbox)
    except ValueError as exc:
        raise ConfigurationError("REPOSITORY_ROOT is outside SANDBOX_ROOT") from exc
    if not root.exists():
        raise ConfigurationError("repository root does not exist")
    if not root.is_dir():
        raise ConfigurationError("repository root is not a directory")
    return root


def validate_candidate_root(root: Path, sandbox: Path | None = None) -> Path:
    """Validate an existing absolute root and, when supplied, its sandbox."""
    if not root.is_absolute() or ".." in root.parts:
        raise ConfigurationError("repository root must be absolute and traversal-free")
    if _has_symlink_component(root):
        raise ConfigurationError("repository root contains a symlink")
    if sandbox is not None:
        if not sandbox.is_absolute() or ".." in sandbox.parts:
            raise ConfigurationError("sandbox root is invalid")
        _validate_sandbox(sandbox)
        try:
            root.relative_to(sandbox)
        except ValueError as exc:
            raise ConfigurationError("repository root is outside sandbox") from exc
    if not root.exists() or not root.is_dir():
        raise ConfigurationError("repository root must be an existing directory")
    return root
