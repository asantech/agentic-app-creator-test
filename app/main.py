from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .models import DeleteRequest, OperationResponse
from .repository import InventoryError, delete_confirmed, inventory

app = FastAPI(title="حذف امن مخزن")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def failed(message: str, verification: bool = True) -> dict[str, object]:
    return {
        "status": "failed",
        "error": message,
        "verification_error": message if verification else None,
        "failures": [],
        "deleted": [],
        "excluded": [],
        "deletable": [],
        "root": None,
        "counts": {"deleted": 0, "excluded": 0, "remaining": None},
        "remaining_unknown": True,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse((STATIC / "index.html").read_text(encoding="utf-8"))


@app.get("/api/preview", response_model=OperationResponse)
def preview() -> dict[str, object]:
    try:
        result = inventory()
    except InventoryError as exc:
        raise HTTPException(status_code=400, detail=failed(str(exc))) from exc
    return {
        "status": "preview",
        "root": str(result.root),
        "deletable": result.deletable,
        "excluded": result.excluded,
        "deleted": [],
        "failures": [],
        "counts": {
            "deleted": 0,
            "excluded": len(result.excluded),
            "remaining": len(result.deletable),
        },
        "remaining_unknown": False,
    }


@app.post("/api/delete", response_model=OperationResponse)
def delete(request: DeleteRequest) -> dict[str, object]:
    if request.confirmation is not True:
        raise HTTPException(
            status_code=400,
            detail=failed("تأیید صریح لازم است", verification=False),
        )
    try:
        result = delete_confirmed()
    except InventoryError as exc:
        raise HTTPException(status_code=400, detail=failed(str(exc))) from exc
    remaining = result["remaining"]
    failures = result["failures"]
    status = "completed" if not failures else "failed"
    return {
        "status": status,
        "root": result["root"],
        "deleted": result["deleted"],
        "excluded": result["excluded"],
        "failures": failures,
        "counts": {
            "deleted": len(result["deleted"]),
            "excluded": len(result["excluded"]),
            "remaining": remaining,
        },
        "remaining_unknown": remaining is None,
    }
