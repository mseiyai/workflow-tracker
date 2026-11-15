from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db_models import Task
from backend.models import TaskStatus


TaskRecord = dict[str, object]


def task_record(task: Task) -> TaskRecord:
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
    }


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_tasks(self, status: TaskStatus | None = None) -> list[TaskRecord]:
        statement = select(Task).order_by(Task.id)
        if status is not None:
            statement = statement.where(Task.status == status)

        tasks = self._session.scalars(statement).all()
        return [task_record(task) for task in tasks]

    def get(self, task_id: int) -> TaskRecord | None:
        task = self._session.get(Task, task_id)
        return None if task is None else task_record(task)

    def create_task(self, title: str) -> TaskRecord:
        task = Task(title=title, status="pending")
        self._session.add(task)
        self._session.flush()
        return task_record(task)

    def update_task_status(
        self,
        task_id: int,
        status: TaskStatus,
    ) -> TaskRecord | None:
        task = self._session.get(Task, task_id)
        if task is None:
            return None

        task.status = status
        return task_record(task)
