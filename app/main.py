from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse

app = FastAPI(title="Purple Body Color App")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSS_PATH = PROJECT_ROOT / "app.css"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Purple Body Color</title>
  <link rel="stylesheet" href="/app.css">
</head>
<body>
  <main>
    <h1>Purple body text</h1>
    <p>The body text color is provided by app.css.</p>
  </main>
</body>
</html>"""


@app.get("/app.css")
def stylesheet() -> FileResponse:
    return FileResponse(CSS_PATH, media_type="text/css")
