import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from backend.tasks import filter_tasks


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class FilterTasksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tasks = [
            {"id": 1, "title": "First", "status": "pending"},
            {"id": 2, "title": "Second", "status": "in_progress"},
            {"id": 3, "title": "Third", "status": "done"},
            {"id": 4, "title": "Fourth", "status": "pending"},
        ]

    def test_no_status_returns_new_list_in_original_order(self) -> None:
        original_tasks = [task.copy() for task in self.tasks]

        result = filter_tasks(self.tasks)

        self.assertEqual(result, self.tasks)
        self.assertIsNot(result, self.tasks)
        self.assertEqual(self.tasks, original_tasks)

    def test_status_returns_only_matches_in_original_order(self) -> None:
        original_tasks = [task.copy() for task in self.tasks]

        self.assertEqual(
            filter_tasks(self.tasks, "pending"),
            [self.tasks[0], self.tasks[3]],
        )
        self.assertEqual(filter_tasks(self.tasks, "in_progress"), [self.tasks[1]])
        self.assertEqual(filter_tasks(self.tasks, "done"), [self.tasks[2]])
        self.assertEqual(self.tasks, original_tasks)

    def test_unsupported_status_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            filter_tasks(self.tasks, "cancelled")


class TasksCommandTests(unittest.TestCase):
    def run_command(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT)

        with tempfile.TemporaryDirectory() as working_directory:
            return subprocess.run(
                [sys.executable, "-m", "backend.tasks", *arguments],
                cwd=working_directory,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_no_status_prints_all_tasks(self) -> None:
        result = self.run_command()

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "1 | pending | Confirm paper order",
                "2 | in_progress | Prepare school quotation",
                "3 | done | Deliver printer cartridges",
                "4 | pending | Call exercise-book supplier",
            ],
        )
        self.assertEqual(result.stderr, "")

    def test_status_prints_only_matching_tasks(self) -> None:
        result = self.run_command("--status", "pending")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "1 | pending | Confirm paper order",
                "4 | pending | Call exercise-book supplier",
            ],
        )
        self.assertEqual(result.stderr, "")

    def test_unsupported_status_is_rejected(self) -> None:
        result = self.run_command("--status", "cancelled")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)
        self.assertEqual(result.stdout, "")

def test_filter_preserves_source_order(self):
    tasks = [
        {"id": 9, "title": "First entered", "status": "pending"},
        {"id": 2, "title": "Second entered", "status": "pending"},
        {"id": 5, "title": "Completed", "status": "done"},
    ]

    result = filter_tasks(tasks, "pending")

    self.assertEqual([task["id"] for task in result], [9, 2])


if __name__ == "__main__":
    unittest.main()
