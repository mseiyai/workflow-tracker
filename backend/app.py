from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.summary import summarize_tasks
from backend.tasks import filter_tasks, load_tasks


TaskStatus = Literal["pending", "in_progress", "done"]

app = FastAPI(title="Workflow Tracker")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks")
def tasks(status: TaskStatus | None = None) -> list[dict]:
    return filter_tasks(load_tasks(), status)


@app.get("/tasks/{task_id}")
def task(task_id: int) -> dict:
    for existing_task in load_tasks():
        if existing_task["id"] == task_id:
            return existing_task

    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/summary")
def summary() -> dict[str, int]:
    return summarize_tasks(load_tasks())
