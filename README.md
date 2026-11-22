# Workflow Tracker

A small-business application for tracking orders, quotations, and deliveries.

Current lesson: recover CI and harden configuration.

Product requirements: docs/product.md
Current issue: issues/010b-ci-recovery.md

Planned stack: React/TypeScript, FastAPI, PostgreSQL.

## Set up the environment

Create and activate a virtual environment, then install the dependencies:

```sh
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the API

With the virtual environment active, start the development server from the
project root:

```sh
fastapi dev backend/app.py --port 8001
```

The API is available at `http://127.0.0.1:8001`. Open
`http://127.0.0.1:8001/docs` for the interactive API documentation.

Create a task:

```sh
curl -X POST http://127.0.0.1:8001/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title":"Prepare customer invoice"}'
```

Update a task's status:

```sh
curl -X PATCH http://127.0.0.1:8001/tasks/1/status \
  -H 'Content-Type: application/json' \
  -d '{"status":"done"}'
```

The API stores tasks in PostgreSQL using the connection in `DATABASE_URL`.
Apply the Alembic migrations before starting the API:

```sh
alembic upgrade head
```

To import the example tasks into an empty database, run:

```sh
python3 -m backend.seed
```

API writes are committed to PostgreSQL and survive application restarts.
`data/tasks.json` is used only by the optional seed command and the standalone
task-summary scripts; normal API startup does not load it.

## Run with Docker Compose

Copy the example environment file and replace the placeholder with a
URL-safe database password:

```sh
cp .env.example .env
```

Build and start the API and PostgreSQL:

```sh
docker compose up --build -d
```

The API is available at `http://127.0.0.1:8001`. PostgreSQL is available only
to other Compose services and is not published to the host. The API container
waits for PostgreSQL to become healthy and applies Alembic migrations before
starting FastAPI.

Check service state and follow API logs:

```sh
docker compose ps
docker compose logs --follow api
```

Open a shell in the API container:

```sh
docker compose exec api sh
```

Run the optional one-shot seed service. The command applies migrations first,
imports the example tasks only when the table is empty, and then exits:

```sh
docker compose --profile tools run --rm seed
```

Verify the API and current migration revision:

```sh
curl --fail http://127.0.0.1:8001/health
docker compose exec api alembic current
```

Stop and remove the containers and network while preserving the named database
volume:

```sh
docker compose down
```

Do not add `-v` to the stop command; that would delete the database volume and
its persisted tasks.

## Run the frontend

Install the frontend packages:

```sh
cd frontend
npm install
```

The dashboard uses `http://localhost:8001` by default. To use a different API
URL, copy `.env.example` to `.env` and update `VITE_API_URL`.

Start the Vite development server:

```sh
cd frontend
npm run dev
```

Open `http://localhost:5173` in a browser. For full-stack development, keep the
FastAPI and Vite development servers running in separate terminals.

## Run the task summary

From the project root:

```sh
python3 backend/summary.py
```

Example output:

```text
Total: 4
Pending: 2
In progress: 1
Done: 1
Open: 3
```

## Run the tests

Create a separate PostgreSQL database whose name ends in `_test`, apply the
migrations, and run the suite from the project root:

```sh
DATABASE_URL=postgresql+psycopg:///workflow_tracker_test \
TEST_DATABASE_URL=postgresql+psycopg:///workflow_tracker_test \
  python -m unittest discover -s tests -v
```

The integration tests refuse to reset rows unless the parsed database name
ends in `_test`.

## List tasks

List all tasks:

```sh
python3 -m backend.tasks
```

List tasks with a specific status:

```sh
python3 -m backend.tasks --status pending
```
