# Workflow Tracker

A small-business application for tracking orders, quotations, and deliveries.

Current lesson: display workflow data in a React dashboard.

Product requirements: docs/product.md
Current issue: issues/005-react-dashboard.md

Planned stack: React/TypeScript, FastAPI, PostgreSQL.

## Set up the environment

Create and activate a virtual environment, then install the dependencies:

```sh
python3 -m venv .venv
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
Total: 3
Pending: 1
In progress: 1
Done: 1
Open: 2
```

## Run the tests

From the project root:

```sh
python3 -m unittest discover -s tests -v
```

## List tasks

List all tasks:

```sh
python3 -m backend.tasks
```

List tasks with a specific status:

```sh
python3 -m backend.tasks --status pending
```
