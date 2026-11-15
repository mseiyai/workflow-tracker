from collections.abc import Iterable, Mapping
from threading import Lock

from backend.models import TaskStatus


TaskRecord = dict[str, object]


class TaskStore:
    def __init__(self, initial_tasks: Iterable[Mapping[str, object]]) -> None:
        self._tasks = [dict(task) for task in initial_tasks]
        self._lock = Lock()

    def list_tasks(self) -> list[TaskRecord]:
        with self._lock:
            return [task.copy() for task in self._tasks]

    def get_task(self, task_id: int) -> TaskRecord | None:
        with self._lock:
            for task in self._tasks:
                if task["id"] == task_id:
                    return task.copy()

        return None

    def create_task(self, title: str) -> TaskRecord:
        with self._lock:
            next_id = max(
                (int(task["id"]) for task in self._tasks),
                default=0,
            ) + 1
            task: TaskRecord = {
                "id": next_id,
                "title": title,
                "status": "pending",
            }
            self._tasks.append(task)
            return task.copy()

    def update_task_status(
        self,
        task_id: int,
        status: TaskStatus,
    ) -> TaskRecord | None:
        with self._lock:
            for task in self._tasks:
                if task["id"] == task_id:
                    task["status"] = status
                    return task.copy()

        return None
