# Workflow Tracker

A small-business application for tracking orders, quotations, and deliveries.

Current lesson: build a Python command that summarizes example tasks.

Product requirements: docs/product.md
Current issue: issues/002-testable-summary.md

Planned stack: React/TypeScript, FastAPI, PostgreSQL.

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
