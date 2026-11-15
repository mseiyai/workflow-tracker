import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app import create_app


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASKS_PATH = PROJECT_ROOT / "data" / "tasks.json"


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())
        self.addCleanup(self.client.close)

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_local_vite_origins_are_allowed(self) -> None:
        for origin in ("http://localhost:5173", "http://127.0.0.1:5173"):
            with self.subTest(origin=origin):
                response = self.client.get("/health", headers={"Origin": origin})

                self.assertEqual(response.headers["access-control-allow-origin"], origin)

    def test_other_origins_are_not_allowed(self) -> None:
        response = self.client.get(
            "/health",
            headers={"Origin": "https://example.com"},
        )

        self.assertNotIn("access-control-allow-origin", response.headers)

    def test_tasks_returns_all_tasks_in_existing_order(self) -> None:
        response = self.client.get("/tasks")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {"id": 1, "title": "Confirm paper order", "status": "pending"},
                {
                    "id": 2,
                    "title": "Prepare school quotation",
                    "status": "in_progress",
                },
                {
                    "id": 3,
                    "title": "Deliver printer cartridges",
                    "status": "done",
                },
                {
                    "id": 4,
                    "title": "Call exercise-book supplier",
                    "status": "pending",
                },
            ],
        )

    def test_tasks_filters_each_supported_status_in_existing_order(self) -> None:
        expected_ids = {
            "pending": [1, 4],
            "in_progress": [2],
            "done": [3],
        }

        for status, task_ids in expected_ids.items():
            with self.subTest(status=status):
                response = self.client.get("/tasks", params={"status": status})

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [task["id"] for task in response.json()],
                    task_ids,
                )

    def test_tasks_rejects_unsupported_status(self) -> None:
        response = self.client.get("/tasks", params={"status": "cancelled"})

        self.assertEqual(response.status_code, 422)

    def test_tasks_reuses_loading_and_filtering_functions(self) -> None:
        tasks = [{"id": 10, "title": "Test task", "status": "pending"}]

        with (
            patch("backend.app.load_tasks", return_value=tasks) as load_mock,
            patch("backend.app.filter_tasks", return_value=tasks) as filter_mock,
        ):
            client = TestClient(create_app())
            self.addCleanup(client.close)
            response = client.get("/tasks", params={"status": "pending"})

        self.assertEqual(response.status_code, 200)
        load_mock.assert_called_once_with()
        filter_mock.assert_called_once_with(tasks, "pending")

    def test_task_by_id_returns_matching_task(self) -> None:
        response = self.client.get("/tasks/2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "id": 2,
                "title": "Prepare school quotation",
                "status": "in_progress",
            },
        )

    def test_task_by_id_returns_404_when_task_is_missing(self) -> None:
        response = self.client.get("/tasks/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Task not found"})

    def test_summary_reuses_loading_and_summary_functions(self) -> None:
        tasks = [{"id": 10, "title": "Test task", "status": "done"}]
        summary = {
            "total": 1,
            "pending": 0,
            "in_progress": 0,
            "done": 1,
            "open": 0,
        }

        with (
            patch("backend.app.load_tasks", return_value=tasks) as load_mock,
            patch("backend.app.summarize_tasks", return_value=summary) as summary_mock,
        ):
            client = TestClient(create_app())
            self.addCleanup(client.close)
            response = client.get("/summary")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), summary)
        load_mock.assert_called_once_with()
        summary_mock.assert_called_once_with(tasks)

    def test_read_endpoints_do_not_modify_tasks_file(self) -> None:
        original_tasks = TASKS_PATH.read_bytes()

        self.client.get("/tasks")
        self.client.get("/summary")

        self.assertEqual(TASKS_PATH.read_bytes(), original_tasks)


if __name__ == "__main__":
    unittest.main()
