from __future__ import annotations

import os
from pathlib import Path


class ConfigurationError(ValueError):
    """Raised when the configured repository root is unsafe or invalid."""


def _reject_symlink_components(path: Path) -> None:
    current = Path(path.anchor)
    for component in path.parts[1:]:
        current /= component
        try:
            if current.is_symlink():
                raise ConfigurationError(f"مسیر شامل symlink است: {current}")
            current.stat()
        except FileNotFoundError as exc:
            raise ConfigurationError("ریشه یا یکی از اجزای مسیر وجود ندارد") from exc


def get_repository_root() -> Path:
    raw = os.environ.get("REPOSITORY_ROOT")
    if not raw:
        raise ConfigurationError("REPOSITORY_ROOT تنظیم نشده است")
    supplied = Path(raw)
    if not supplied.is_absolute() or ".." in supplied.parts:
        raise ConfigurationError("ریشه باید یک مسیر مطلق و بدون parent traversal باشد")
    _reject_symlink_components(supplied)
    root = supplied.resolve(strict=True)
    if not root.is_dir():
        raise ConfigurationError("ریشهٔ مخزن باید directory باشد")
    return root
