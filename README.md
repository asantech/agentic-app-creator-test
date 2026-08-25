# Form Demo

A small FastAPI application serving an HTML5 page with a visible semantic form.

## Run

From the project root:

```text
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/` to view the page. The form is intentionally presentational and does not submit data to a backend endpoint.

## Test

```text
pytest
```

The health check is available at `/health` and returns `{"status":"ok"}`.
