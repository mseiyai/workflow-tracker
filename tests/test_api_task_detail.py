import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app import create_app
from backend.repository import TaskRepository
from tests.database_integration import PostgresIntegrationTestCase


class TaskDetailApiTests(PostgresIntegrationTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.task = {
            "id": 1,
            "title": "Prepare school quotation",
            "status": "in_progress",
        }
        self.insert_tasks([self.task])
        self.client = TestClient(create_app(session_factory=self.session_factory))
        self.addCleanup(self.client.close)

    def test_task_by_id_returns_matching_task(self) -> None:
        response = self.client.get("/tasks/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.task)

    def test_task_by_id_returns_404_when_task_is_missing(self) -> None:
        response = self.client.get("/tasks/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Task not found"})

    def test_task_by_id_uses_repository_get(self) -> None:
        with patch.object(TaskRepository, "get", return_value=self.task) as get_mock:
            response = self.client.get("/tasks/1")

        self.assertEqual(response.status_code, 200)
        get_mock.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
