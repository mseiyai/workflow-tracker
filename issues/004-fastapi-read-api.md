# Issue 004: Expose tasks through a read-only HTTP API

## User story

As the shop owner, I want the workflow tracker's task list and summary
available over HTTP so that a browser dashboard can consume them later.

## Acceptance criteria

- Create `backend/app.py` containing a FastAPI application.
- `GET /health` returns HTTP 200 and `{"status": "ok"}`.
- `GET /tasks` returns all tasks in their existing order.
- `GET /tasks?status=<status>` reuses the existing filtering function.
- Valid statuses are `pending`, `in_progress`, and `done`.
- An unsupported status produces HTTP 422.
- `GET /summary` reuses the existing summary function.
- Add API tests in `tests/test_api.py`.
- Record Python dependencies in `requirements.txt`.
- Document local startup and `/docs` in `README.md`.
- All existing tests continue to pass.
- `data/tasks.json` is not modified.

## Out of scope

- Creating, editing, or deleting tasks
- Authentication
- CORS configuration
- React
- PostgreSQL
- Docker
- Deployment

## Verification

- `python -m unittest discover -s tests -p "test_api.py" -v`
- `python -m unittest discover -s tests -v`
- `fastapi dev backend/app.py`
- Manual requests to `/health`, `/tasks`, and `/summary`