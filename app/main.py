from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Purple Color Demo")
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=FileResponse)
def index() -> Path:
    return BASE_DIR / "index.html"


@app.get("/app.css", response_class=FileResponse)
def stylesheet() -> FileResponse:
    return FileResponse(BASE_DIR / "app.css", media_type="text/css")
