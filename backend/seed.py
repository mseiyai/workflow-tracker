import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import create_database_engine, create_session_factory
from backend.db_models import Task
from backend.tasks import SUPPORTED_STATUSES


TASKS_PATH = Path(__file__).resolve().parent.parent / "data" / "tasks.json"


def load_seed_tasks(tasks_path: Path = TASKS_PATH) -> list[dict[str, str]]:
    with tasks_path.open(encoding="utf-8") as tasks_file:
        records = json.load(tasks_file)

    if not isinstance(records, list):
        raise ValueError("Task seed data must be a list")

    tasks: list[dict[str, str]] = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each seeded task must be an object")

        title = record.get("title")
        status = record.get("status")
        if not isinstance(title, str) or not 1 <= len(title) <= 120:
            raise ValueError("Each seeded task needs a title of 1 to 120 characters")
        if status not in SUPPORTED_STATUSES:
            raise ValueError(f"Unsupported seeded task status: {status}")

        tasks.append({"title": title, "status": status})

    return tasks


def seed_tasks(session: Session, tasks_path: Path = TASKS_PATH) -> int:
    if session.scalar(select(Task.id).limit(1)) is not None:
        return 0

    tasks = load_seed_tasks(tasks_path)
    session.add_all(Task(**task) for task in tasks)
    return len(tasks)


def main() -> None:
    engine = create_database_engine()
    session_factory = create_session_factory(engine)

    try:
        with session_factory.begin() as session:
            inserted_count = seed_tasks(session)
    finally:
        engine.dispose()

    if inserted_count:
        print(f"Seeded {inserted_count} tasks.")
    else:
        print("Tasks table is not empty; skipping seed.")


if __name__ == "__main__":
    main()
