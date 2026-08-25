from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse


app = FastAPI(title="Form Demo")
BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "src" / "index.html"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(INDEX_FILE, media_type="text/html")
