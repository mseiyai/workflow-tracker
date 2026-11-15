# Issue 008: Persist the task API in PostgreSQL

Status: ready

## User story

As the stationery shop manager, I want task changes to survive API
restarts so that the workflow tracker remains reliable.

## Acceptance criteria

- Replace runtime use of the in-memory TaskStore with PostgreSQL.
- Preserve the existing GET /tasks response and status filter.
- Preserve GET /summary.
- Preserve POST /tasks and its 201 response.
- Preserve PATCH /tasks/{task_id}/status.
- Preserve existing 404 and 422 behavior.
- Do not load data/tasks.json during normal API startup.
- Add a TaskRepository that owns SQLAlchemy task queries.
- Give each HTTP request a separate SQLAlchemy Session.
- Commit successful create and update operations.
- Return database-generated task IDs.
- PostgreSQL data survives creating a new application instance.
- Integration tests use workflow_tracker_test, never the development database.
- Reset task rows before each integration test.
- Apply Alembic migrations to the test database before running tests.
- Existing pure unit tests and the frontend build still pass.
- No schema change or new Alembic revision is required.
- Do not modify data/tasks.json.

## Out of scope

- Docker and Docker Compose
- Authentication or users
- Pagination
- Deleting tasks
- Changing API response shapes
- Frontend redesign
- Deployment

## Verification

- alembic check
- python -m unittest discover -s tests -v
- npm run build
- manual restart-persistence check
- git diff --check
- git diff -- data/tasks.json

Do not commit.