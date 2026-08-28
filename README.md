# Safe Repository Cleaner

A small FastAPI application for safely previewing and, only after explicit confirmation, deleting the contents of a configured sandbox-local repository.

## Run

Set `SANDBOX_ROOT` to the local directory that contains the target repository, then start the ASGI application with Uvicorn using `app.main:app`.

Repository paths submitted to the API must be relative to `SANDBOX_ROOT`. Absolute paths, parent traversal, and symlink repository paths are rejected. The repository root and `.git` are preserved.

- `GET /health` returns a health response.
- `POST /preview` accepts `{ "repo_path": "repo" }` and performs no mutation.
- `POST /delete` requires `{ "repo_path": "repo", "confirmation": "DELETE" }`.

The delete response reports `deleted`, `excluded`, `failures`, and `remaining` based on the resulting filesystem state.

## Tests

Run `pytest` from the project directory.
