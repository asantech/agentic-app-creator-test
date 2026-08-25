from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI(title="فرم فارسی")
BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "src" / "index.html"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def homepage() -> HTMLResponse:
    return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))
