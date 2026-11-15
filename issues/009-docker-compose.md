# Issue 009: Run the API and PostgreSQL with Docker Compose

Status: ready

## User story

As the Workflow Tracker developer, I want one reproducible command to
start the API and database so that development does not depend on
manually configured host services.

## Acceptance criteria

- Add a Dockerfile for the FastAPI application.
- Use a versioned official Python base image.
- Install dependencies before copying frequently changed source files.
- Run the API process as a non-root user.
- Do not copy .env, .git, virtual environments, caches, or frontend
  dependencies into the image.
- Add a Compose file with `api` and `db` services.
- Pin PostgreSQL to major version 17.
- Store PostgreSQL data in a named volume.
- Do not publish the PostgreSQL port to the host.
- Read the database password from an ignored .env file.
- Do not embed credentials in the image.
- The API connects to the Compose service name `db`, not localhost.
- PostgreSQL has a readiness health check.
- The API waits for PostgreSQL to become healthy.
- Alembic upgrades the database before FastAPI starts.
- The API publishes port 8001.
- GET /health succeeds.
- API writes survive API and database container replacement.
- Existing host integration tests and frontend build still pass.
- Update README.md with start, stop, logs, shell, seed, and verification
  commands.
- Do not modify data/tasks.json.
- Do not use `docker compose down -v`.

## Out of scope

- Publishing images
- GitHub Actions
- Kubernetes
- Production deployment
- Containerizing the React frontend
- Changing the API contract

## Verification

- docker compose config --quiet
- docker compose build
- docker compose up -d
- docker compose ps
- curl http://127.0.0.1:8001/health
- docker compose exec api alembic current
- persistence check after docker compose down/up
- existing backend tests
- npm run build
- git diff --check

Do not commit.