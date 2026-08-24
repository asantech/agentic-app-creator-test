from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


app = FastAPI(title="Minimal FastAPI Application", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Minimal FastAPI App</title>
  <style>
    :root { color-scheme: light dark; font-family: system-ui, sans-serif; }
    body { display: grid; min-height: 100vh; place-items: center; margin: 0; }
    main { max-width: 42rem; padding: 2rem; text-align: center; }
    code { padding: .2rem .4rem; border-radius: .25rem; background: color-mix(in srgb, currentColor 12%, transparent); }
  </style>
</head>
<body>
  <main>
    <h1>Minimal FastAPI Application</h1>
    <p>The application is running successfully.</p>
    <p>Health endpoint: <code>/health</code></p>
  </main>
</body>
</html>"""
