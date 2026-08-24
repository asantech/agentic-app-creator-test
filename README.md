# Purple Body Color App

A small FastAPI application that serves a page using the root-level `app.css` stylesheet.

## Run

```text
uvicorn app.main:app
```

The application provides:

- `GET /` — HTML page referencing `/app.css`
- `GET /app.css` — stylesheet containing only `body { color: purple; }`
- `GET /health` — JSON health response

## Test

```text
pytest
```
