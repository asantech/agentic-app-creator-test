from __future__ import annotations

import shutil
import stat
import uuid
from dataclasses import dataclass
from pathlib import Path

from .config import ConfigurationError, get_repository_root


class InventoryError(ValueError):
    """Raised when the repository tree cannot be safely inventoried."""


@dataclass(frozen=True)
class Entry:
    relative: str
    kind: str


@dataclass(frozen=True)
class Preview:
    root: Path
    entries: tuple[Entry, ...]
    excluded: tuple[str, ...]


_previews: dict[str, Preview] = {}


def _safe_lstat(path: Path) -> str:
    """Return a supported entry kind, rejecting symlinks and special files."""
    try:
        if path.is_symlink():
            raise InventoryError(f"symlink در درخت هدف مجاز نیست: {path}")
        mode = path.lstat().st_mode
    except InventoryError:
        raise
    except OSError as exc:
        raise InventoryError(f"خطا در خواندن {path}: {exc}") from exc

    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "file"
    raise InventoryError(f"نوع فایل پشتیبانی‌نشده در {path}")


def inventory(root: Path) -> tuple[tuple[Entry, ...], tuple[str, ...]]:
    entries: list[Entry] = []
    excluded: list[str] = []

    def walk(directory: Path, prefix: str = "") -> None:
        try:
            children = sorted(directory.iterdir(), key=lambda item: item.name)
        except OSError as exc:
            raise InventoryError(f"خطا در فهرست‌کردن {directory}: {exc}") from exc

        for child in children:
            relative = f"{prefix}/{child.name}" if prefix else child.name
            # This check intentionally occurs before the .git exclusion. An
            # excluded entry must still be a safe, ordinary directory.
            kind = _safe_lstat(child)
            if not prefix and child.name == ".git":
                if kind != "directory":
                    raise InventoryError(".git باید یک directory معمولی باشد")
                excluded.append(relative)
                continue

            entries.append(Entry(relative, kind))
            if kind == "directory":
                walk(child, relative)

    if _safe_lstat(root) != "directory":
        raise InventoryError("ریشهٔ مخزن directory نیست")
    walk(root)
    return tuple(entries), tuple(excluded)


def _snapshot(root: Path) -> Preview:
    entries, excluded = inventory(root)
    return Preview(root=root, entries=entries, excluded=excluded)


def preview_repository() -> dict:
    root = get_repository_root()
    record = _snapshot(root)
    token = uuid.uuid4().hex
    _previews[token] = record
    deletable = [entry.relative for entry in record.entries]
    return {
        "status": "preview",
        "preview_id": token,
        "deleted": deletable,
        "excluded": list(record.excluded),
        "failures": [],
        "counts": {
            "deleted": len(deletable),
            "excluded": len(record.excluded),
            "remaining": len(deletable),
        },
        "remaining_unknown": False,
        "message": "پیش‌نمایش انجام شد؛ برای حذف واقعی تأیید صریح لازم است.",
    }


def failed(
    message: str,
    failures: list[str] | None = None,
    verification_error: str | None = None,
) -> dict:
    return {
        "status": "failed",
        "preview_id": None,
        "deleted": [],
        "excluded": [],
        "failures": failures or [message],
        "counts": {"deleted": 0, "excluded": 0, "remaining": 0},
        "remaining_unknown": True,
        "message": message,
        "verification_error": verification_error,
    }


def confirm_repository(preview_id: str, confirm: bool) -> dict:
    if not confirm:
        return failed("تأیید صریح برای حذف لازم است.")

    record = _previews.get(preview_id)
    if record is None:
        return failed("پیش‌نمایش معتبر یا موجود نیست.")

    try:
        # Revalidate the configured path and every path component. Do not use
        # the Path captured during preview until this check has succeeded.
        current_root = get_repository_root()
        if current_root != record.root:
            raise InventoryError("ریشهٔ تنظیم‌شده پس از پیش‌نمایش تغییر کرده است")
        current = _snapshot(current_root)
    except (ConfigurationError, InventoryError, OSError) as exc:
        return failed(
            "اعتبارسنجی مجدد شکست خورد؛ هیچ حذفی انجام نشد.",
            [str(exc)],
            str(exc),
        )

    if current.entries != record.entries or current.excluded != record.excluded:
        return failed(
            "درخت مخزن پس از پیش‌نمایش تغییر کرده است؛ هیچ حذفی انجام نشد.",
            ["inventory mismatch"],
            "inventory mismatch",
        )

    deleted: list[str] = []
    failures: list[str] = []
    top_level = [entry for entry in record.entries if "/" not in entry.relative]

    for entry in top_level:
        target = record.root / entry.relative
        try:
            if target.is_symlink():
                raise InventoryError(f"symlink هنگام حذف ظاهر شد: {entry.relative}")
            if entry.kind == "directory":
                shutil.rmtree(target)
            else:
                target.unlink()
            deleted.extend(
                item.relative
                for item in record.entries
                if item.relative == entry.relative
                or item.relative.startswith(entry.relative + "/")
            )
        except (OSError, InventoryError) as exc:
            failures.append(f"{entry.relative}: {exc}")

    _previews.pop(preview_id, None)
    if failures:
        return {
            "status": "failed",
            "preview_id": preview_id,
            "deleted": deleted,
            "excluded": list(record.excluded),
            "failures": failures,
            "counts": {
                "deleted": len(deleted),
                "excluded": len(record.excluded),
                "remaining": -1,
            },
            "remaining_unknown": True,
            "message": "حذف ناقص انجام شد؛ وضعیت باقی‌مانده نامشخص است.",
            "verification_error": None,
        }

    return {
        "status": "confirmed",
        "preview_id": preview_id,
        "deleted": deleted,
        "excluded": list(record.excluded),
        "failures": [],
        "counts": {
            "deleted": len(deleted),
            "excluded": len(record.excluded),
            "remaining": 0,
        },
        "remaining_unknown": False,
        "message": "حذف با موفقیت انجام شد و ریشه حفظ شد.",
        "verification_error": None,
    }


__all__ = [
    "InventoryError",
    "confirm_repository",
    "failed",
    "inventory",
    "preview_repository",
]
