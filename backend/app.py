from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import (
    CreateTaskRequest,
    TaskResponse,
    TaskStatus,
    UpdateTaskStatusRequest,
)
from backend.store import TaskStore
from backend.summary import summarize_tasks
from backend.tasks import filter_tasks, load_tasks


def create_app(initial_tasks: list[dict] | None = None) -> FastAPI:
    task_store = TaskStore(load_tasks() if initial_tasks is None else initial_tasks)
    application = FastAPI(title="Workflow Tracker")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET", "POST", "PATCH"],
    )

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/tasks", response_model=list[TaskResponse])
    def tasks(status: TaskStatus | None = None) -> list[dict]:
        return filter_tasks(task_store.list_tasks(), status)

    @application.post(
        "/tasks",
        response_model=TaskResponse,
        status_code=201,
    )
    def create_task(request: CreateTaskRequest) -> dict:
        return task_store.create_task(request.title)

    @application.get("/tasks/{task_id}", response_model=TaskResponse)
    def task(task_id: int) -> dict:
        existing_task = task_store.get_task(task_id)
        if existing_task is not None:
            return existing_task

        raise HTTPException(status_code=404, detail="Task not found")

    @application.patch(
        "/tasks/{task_id}/status",
        response_model=TaskResponse,
    )
    def update_task_status(
        task_id: int,
        request: UpdateTaskStatusRequest,
    ) -> dict:
        updated_task = task_store.update_task_status(task_id, request.status)
        if updated_task is not None:
            return updated_task

        raise HTTPException(status_code=404, detail="Task not found")

    @application.get("/summary")
    def summary() -> dict[str, int]:
        return summarize_tasks(task_store.list_tasks())

    return application


app = create_app()
