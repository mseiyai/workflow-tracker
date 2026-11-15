# Issue 007: Add the initial PostgreSQL schema

## User story

As the shop manager, I want workflow tasks stored in a relational
database so that they can eventually survive API restarts.

## Acceptance criteria

- SQLAlchemy 2 typed models define a `tasks` table.
- `tasks` has a database-generated integer primary key.
- `title` is required and limited to 120 characters.
- `status` is required and accepts only:
  - `pending`
  - `in_progress`
  - `done`
- `status` has an index.
- The connection URL comes from `DATABASE_URL`.
- No password or connection secret is committed.
- Alembic contains a reviewed initial migration.
- The migration upgrades a new database to `head`.
- A seed command imports `data/tasks.json` only when `tasks` is empty.
- Running the seed command twice does not duplicate tasks.
- Existing backend tests and the frontend build still pass.
- The FastAPI endpoints continue using the existing store in this issue.

## Out of scope

- Connecting API endpoints to PostgreSQL
- Docker or Docker Compose
- Authentication
- Frontend changes
- Editing `data/tasks.json`
- Deploying the database