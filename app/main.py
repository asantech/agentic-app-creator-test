from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .models import ConfirmationRequest, OperationResponse
from .repository_service import confirm_repository, failed, preview_repository
from .config import ConfigurationError
from .repository_service import InventoryError

app = FastAPI(title="حذف امن فایل‌های مخزن")
_STATIC = Path(__file__).parent / "static"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse((_STATIC / "index.html").read_text(encoding="utf-8"))


@app.get("/static/{name}")
def static_file(name: str) -> HTMLResponse:
    allowed = {"styles.css": "text/css", "app.js": "application/javascript"}
    if name not in allowed:
        return HTMLResponse("Not found", status_code=404)
    return HTMLResponse((_STATIC / name).read_text(encoding="utf-8"), media_type=allowed[name])


@app.post("/api/preview", response_model=OperationResponse)
def api_preview() -> dict:
    try:
        return preview_repository()
    except (ConfigurationError, InventoryError, OSError) as exc:
        return failed("پیش‌نمایش شکست خورد و هیچ تغییری انجام نشد.", [str(exc)], str(exc))


@app.post("/api/confirm", response_model=OperationResponse)
def api_confirm(request: ConfirmationRequest) -> dict:
    return confirm_repository(request.preview_id, request.confirm)
