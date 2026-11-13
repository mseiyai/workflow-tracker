import argparse
import json
from pathlib import Path


TASKS_PATH = Path(__file__).resolve().parent.parent / "data" / "tasks.json"
SUPPORTED_STATUSES = ("pending", "in_progress", "done")


def filter_tasks(tasks: list[dict], status: str | None = None) -> list[dict]:
    if status is not None and status not in SUPPORTED_STATUSES:
        raise ValueError(f"Unsupported status: {status}")

    if status is None:
        return list(tasks)

    return [task for task in tasks if task["status"] == status]


def main() -> None:
    parser = argparse.ArgumentParser(description="List tasks by status.")
    parser.add_argument("--status", choices=SUPPORTED_STATUSES)
    arguments = parser.parse_args()

    with TASKS_PATH.open(encoding="utf-8") as tasks_file:
        tasks = json.load(tasks_file)

    for task in filter_tasks(tasks, arguments.status):
        print(f"{task['id']} | {task['status']} | {task['title']}")


if __name__ == "__main__":
    main()
