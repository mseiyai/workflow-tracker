import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import backend.app as app_module


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASKS_PATH = PROJECT_ROOT / "data" / "tasks.json"


class ApiWriteTests(unittest.TestCase):
    def setUp(self) -> None:
        initial_tasks = [
            {"id": 1, "title": "First task", "status": "pending"},
            {"id": 2, "title": "Second task", "status": "in_progress"},
            {"id": 3, "title": "Third task", "status": "done"},
        ]
        self.client = TestClient(app_module.create_app(initial_tasks))
        self.addCleanup(self.client.close)

    def test_create_task_returns_created_task_and_updates_reads(self) -> None:
        response = self.client.post("/tasks", json={"title": "  Prepare invoice  "})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {"id": 4, "title": "Prepare invoice", "status": "pending"},
        )
        self.assertEqual(
            self.client.get("/tasks").json()[-1],
            {"id": 4, "title": "Prepare invoice", "status": "pending"},
        )
        self.assertEqual(
            self.client.get("/summary").json(),
            {
                "total": 4,
                "pending": 2,
                "in_progress": 1,
                "done": 1,
                "open": 3,
            },
        )

    def test_create_task_rejects_blank_title(self) -> None:
        response = self.client.post("/tasks", json={"title": "   "})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(len(self.client.get("/tasks").json()), 3)

    def test_create_task_rejects_overlong_title_and_unexpected_fields(self) -> None:
        for body in (
            {"title": "x" * 121},
            {"title": "Valid title", "status": "done"},
        ):
            with self.subTest(body=body):
                response = self.client.post("/tasks", json=body)

                self.assertEqual(response.status_code, 422)

        self.assertEqual(len(self.client.get("/tasks").json()), 3)

    def test_update_status_returns_updated_task_and_updates_reads(self) -> None:
        response = self.client.patch("/tasks/2/status", json={"status": "done"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"id": 2, "title": "Second task", "status": "done"},
        )
        self.assertEqual(
            self.client.get("/tasks/2").json(),
            {"id": 2, "title": "Second task", "status": "done"},
        )
        self.assertEqual(
            self.client.get("/summary").json(),
            {
                "total": 3,
                "pending": 1,
                "in_progress": 0,
                "done": 2,
                "open": 1,
            },
        )

    def test_update_status_rejects_invalid_status(self) -> None:
        response = self.client.patch(
            "/tasks/2/status",
            json={"status": "cancelled"},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.get("/tasks/2").json()["status"], "in_progress")

    def test_update_status_returns_404_for_missing_task(self) -> None:
        response = self.client.patch(
            "/tasks/999/status",
            json={"status": "done"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Task not found"})

    def test_cors_preflight_allows_only_configured_write_methods(self) -> None:
        for method in ("POST", "PATCH"):
            with self.subTest(method=method):
                response = self.client.options(
                    "/tasks",
                    headers={
                        "Origin": "http://localhost:5173",
                        "Access-Control-Request-Method": method,
                    },
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.headers["access-control-allow-methods"],
                    "GET, POST, PATCH",
                )

    def test_api_writes_do_not_modify_tasks_file(self) -> None:
        original_tasks = TASKS_PATH.read_bytes()

        created = self.client.post("/tasks", json={"title": "Temporary task"})
        self.client.patch(
            f"/tasks/{created.json()['id']}/status",
            json={"status": "done"},
        )

        self.assertEqual(TASKS_PATH.read_bytes(), original_tasks)


if __name__ == "__main__":
    unittest.main()
