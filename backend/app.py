from collections.abc import Iterator

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.database import (
    SessionFactory,
    get_session_factory,
)
from backend.models import (
    CreateTaskRequest,
    TaskResponse,
    TaskStatus,
    UpdateTaskStatusRequest,
)
from backend.repository import HealthRepository, TaskRepository
from backend.summary import summarize_tasks


def create_app(session_factory: SessionFactory | None = None) -> FastAPI:
    application = FastAPI(title="Workflow Tracker")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET", "POST", "PATCH"],
    )

    def get_session() -> Iterator[Session]:
        factory = session_factory or get_session_factory()
        with factory() as session:
            yield session

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/health/live")
    def health_live() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/health/ready")
    def health_ready() -> dict[str, str]:
        try:
            factory = session_factory or get_session_factory()
        except (ImportError, RuntimeError, SQLAlchemyError, ValueError):
            raise HTTPException(status_code=503, detail="Service unavailable") from None

        try:
            with factory() as session:
                HealthRepository(session).check_connection()
        except (RuntimeError, SQLAlchemyError):
            raise HTTPException(
                status_code=503,
                detail="Service unavailable",
            ) from None

        return {"status": "ok"}

    @application.get("/tasks", response_model=list[TaskResponse])
    def tasks(
        status: TaskStatus | None = None,
        session: Session = Depends(get_session),
    ) -> list[dict]:
        return TaskRepository(session).list_tasks(status)

    @application.post(
        "/tasks",
        response_model=TaskResponse,
        status_code=201,
    )
    def create_task(
        request: CreateTaskRequest,
        session: Session = Depends(get_session),
    ) -> dict:
        task = TaskRepository(session).create_task(request.title)
        session.commit()
        return task

    @application.get("/tasks/{task_id}", response_model=TaskResponse)
    def task(
        task_id: int,
        session: Session = Depends(get_session),
    ) -> dict:
        existing_task = TaskRepository(session).get(task_id)
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
        session: Session = Depends(get_session),
    ) -> dict:
        updated_task = TaskRepository(session).update_task_status(
            task_id,
            request.status,
        )
        if updated_task is not None:
            session.commit()
            return updated_task

        raise HTTPException(status_code=404, detail="Task not found")

    @application.get("/summary")
    def summary(session: Session = Depends(get_session)) -> dict[str, int]:
        return summarize_tasks(TaskRepository(session).list_tasks())

    return application


app = create_app()
