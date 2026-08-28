from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


app = FastAPI(title="Safe Repository Cleaner")

IMMUTABLE_NAMES = {".git"}
CONFIRMATION_TOKEN = "DELETE"


class RepositoryRequest(BaseModel):
    repo_path: str


class DeleteRequest(RepositoryRequest):
    confirmation: str | None = None


def _contains_symlink(path: Path) -> bool:
    """Return whether any filesystem component of path is a symlink."""
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        try:
            if current.is_symlink():
                return True
        except OSError:
            return True
    return False


def sandbox_root() -> Path:
    """Return the explicitly configured sandbox root."""
    configured = os.environ.get("SANDBOX_ROOT")
    if configured is None or not configured.strip():
        raise HTTPException(
            status_code=400,
            detail="SANDBOX_ROOT must be explicitly configured",
        )

    try:
        root = Path(configured).absolute()
    except (TypeError, ValueError, OSError):
        raise HTTPException(status_code=400, detail="invalid sandbox root")

    if _contains_symlink(root):
        raise HTTPException(status_code=400, detail="sandbox root may not contain symlinks")
    if not root.exists() or not root.is_dir():
        raise HTTPException(status_code=400, detail="sandbox root does not exist or is not a directory")
    return root


def validate_repository_path(raw_path: str) -> Path:
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise HTTPException(status_code=400, detail="repo_path is required")

    try:
        candidate_input = Path(raw_path)
    except (TypeError, ValueError, OSError):
        raise HTTPException(status_code=400, detail="invalid repository path")

    if candidate_input.is_absolute():
        raise HTTPException(status_code=400, detail="absolute repository paths are not allowed")
    if any(part == ".." for part in candidate_input.parts):
        raise HTTPException(status_code=400, detail="parent traversal is not allowed")
    if any(part == "" for part in candidate_input.parts):
        raise HTTPException(status_code=400, detail="invalid repository path")

    root = sandbox_root()
    current = root
    for part in candidate_input.parts:
        current = current / part
        try:
            if current.is_symlink():
                raise HTTPException(status_code=400, detail="repository path contains a symlink")
        except OSError:
            raise HTTPException(status_code=400, detail="repository path contains an inaccessible component")

    try:
        resolved = current.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (FileNotFoundError, ValueError, OSError):
        raise HTTPException(status_code=400, detail="repository must be an existing sandbox-local directory")

    if not current.is_dir():
        raise HTTPException(status_code=400, detail="repository path is not a directory")
    return current


def display_path(repo: Path, child: Path) -> str:
    return child.relative_to(repo).as_posix()


def inventory(repo: Path) -> dict[str, list[str]]:
    deletable: list[str] = []
    excluded: list[str] = []
    failures: list[str] = []
    try:
        children = list(repo.iterdir())
    except OSError as exc:
        return {"deletable": [], "excluded": [], "failures": [str(exc)]}

    for child in sorted(children, key=lambda item: item.name):
        shown = display_path(repo, child)
        try:
            if child.name in IMMUTABLE_NAMES:
                excluded.append(f"{shown}: immutable")
            elif child.is_symlink():
                excluded.append(f"{shown}: symlink")
            else:
                deletable.append(shown)
        except OSError as exc:
            failures.append(f"{shown}: {exc}")
    return {"deletable": deletable, "excluded": excluded, "failures": failures}


def remaining_items(repo: Path) -> list[str]:
    try:
        return sorted(display_path(repo, child) for child in repo.iterdir())
    except OSError as exc:
        return [f"inventory error: {exc}"]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html_path = Path(__file__).resolve().parent.parent / "static" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.post("/preview")
def preview(request: RepositoryRequest) -> dict[str, Any]:
    repo = validate_repository_path(request.repo_path)
    result = inventory(repo)
    return {
        "repo_path": request.repo_path,
        "deletable": result["deletable"],
        "excluded": result["excluded"],
        "failures": result["failures"],
        "mutated": False,
    }


@app.post("/delete")
def delete_repository(request: DeleteRequest) -> dict[str, Any]:
    if request.confirmation != CONFIRMATION_TOKEN:
        raise HTTPException(
            status_code=400,
            detail=f"explicit confirmation must equal {CONFIRMATION_TOKEN}",
        )

    repo = validate_repository_path(request.repo_path)
    before = inventory(repo)
    deleted: list[str] = []
    failures = list(before["failures"])

    for relative in before["deletable"]:
        child = repo / relative
        try:
            if child.is_symlink():
                failures.append(f"{relative}: became a symlink")
            elif child.is_dir():
                shutil.rmtree(child)
                deleted.append(relative)
            else:
                child.unlink()
                deleted.append(relative)
        except OSError as exc:
            failures.append(f"{relative}: {exc}")

    after = inventory(repo)
    return {
        "repo_path": request.repo_path,
        "deleted": deleted,
        "excluded": after["excluded"],
        "failures": failures + after["failures"],
        "remaining": remaining_items(repo),
        "mutated": True,
    }
