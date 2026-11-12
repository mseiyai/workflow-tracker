import json
from collections import Counter
from pathlib import Path


TASKS_PATH = Path(__file__).resolve().parent.parent / "data" / "tasks.json"


def summarize_tasks(tasks: list[dict]) -> dict[str, int]:
    status_counts = Counter(task["status"] for task in tasks)

    return {
        "total": len(tasks),
        "pending": status_counts["pending"],
        "in_progress": status_counts["in_progress"],
        "done": status_counts["done"],
        "open": status_counts["pending"] + status_counts["in_progress"],
    }


def main() -> None:
    with TASKS_PATH.open(encoding="utf-8") as tasks_file:
        tasks = json.load(tasks_file)

    summary = summarize_tasks(tasks)

    print(f"Total: {summary['total']}")
    print(f"Pending: {summary['pending']}")
    print(f"In progress: {summary['in_progress']}")
    print(f"Done: {summary['done']}")
    print(f"Open: {summary['open']}")


if __name__ == "__main__":
    main()
