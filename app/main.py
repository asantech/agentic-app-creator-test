from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSS_FILE = PROJECT_ROOT / "app.css"

app = FastAPI(title="Red Background Demo")


class HealthResponse(BaseModel):
    status: str


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>صفحه قرمز</title>
  <link rel="stylesheet" href="/app.css">
</head>
<body>
  <main class="card">
    <h1>صفحه اصلی</h1>
    <p>پس‌زمینه این صفحه از فایل محلی <code>app.css</code> خوانده می‌شود.</p>
  </main>
</body>
</html>"""


@app.get("/app.css", response_class=FileResponse)
def stylesheet() -> FileResponse:
    return FileResponse(CSS_FILE, media_type="text/css")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
