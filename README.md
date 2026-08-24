# Local CSS Starter

A small FastAPI application demonstrating a locally served stylesheet.

## Run

```text
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/` in a browser. The stylesheet is available at `/static/app.css`, and `/health` returns a JSON status response.

## Test

```text
pytest
```

The project uses only FastAPI, Python standard-library file handling, and vanilla HTML/CSS. No CDN or external asset is required.
