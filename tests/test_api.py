from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app import create_app
from tests.database_integration import PostgresIntegrationTestCase


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASKS_PATH = PROJECT_ROOT / "data" / "tasks.json"


class ApiTests(PostgresIntegrationTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.insert_tasks(
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
            ]
        )
        self.client = TestClient(create_app(session_factory=self.session_factory))
        self.addCleanup(self.client.close)

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_create_app_does_not_load_json_tasks(self) -> None:
        with patch("backend.tasks.load_tasks") as load_tasks_mock:
            application = create_app(session_factory=self.session_factory)

        load_tasks_mock.assert_not_called()
        self.assertIsNotNone(application)

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

    def test_database_connection_is_returned_after_request(self) -> None:
        response = self.client.get("/tasks")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.engine.pool.checkedout(), 0)

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

    def test_summary_reuses_summary_function(self) -> None:
        summary = {
            "total": 4,
            "pending": 2,
            "in_progress": 1,
            "done": 1,
            "open": 3,
        }

        with patch(
            "backend.app.summarize_tasks", return_value=summary
        ) as summary_mock:
            response = self.client.get("/summary")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), summary)
        summarized_tasks = summary_mock.call_args.args[0]
        self.assertEqual([task["id"] for task in summarized_tasks], [1, 2, 3, 4])

    def test_read_endpoints_do_not_modify_tasks_file(self) -> None:
        original_tasks = TASKS_PATH.read_bytes()

        self.client.get("/tasks")
        self.client.get("/summary")

        self.assertEqual(TASKS_PATH.read_bytes(), original_tasks)


if __name__ == "__main__":
    unittest.main()
