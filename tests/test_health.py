import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from backend.app import create_app
from backend.database import get_session_factory


class HealthEndpointTests(unittest.TestCase):
    def test_liveness_does_not_access_the_database(self) -> None:
        session_factory = MagicMock(
            side_effect=AssertionError("liveness accessed the database")
        )
        client = TestClient(create_app(session_factory=session_factory))
        self.addCleanup(client.close)

        response = client.get("/health/live")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        session_factory.assert_not_called()

    def test_readiness_returns_ok_when_database_responds(self) -> None:
        session_factory = MagicMock()
        session = session_factory.return_value.__enter__.return_value
        client = TestClient(create_app(session_factory=session_factory))
        self.addCleanup(client.close)

        response = client.get("/health/ready")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        session.execute.assert_called_once()
        self.assertEqual(str(session.execute.call_args.args[0]), "SELECT 1")
        session_factory.return_value.__exit__.assert_called_once()

    def test_readiness_returns_generic_503_when_database_is_unavailable(
        self,
    ) -> None:
        session_factory = MagicMock()
        session = session_factory.return_value.__enter__.return_value
        session.execute.side_effect = SQLAlchemyError(
            "postgresql://user:secret@db.internal/workflow_tracker"
        )
        client = TestClient(create_app(session_factory=session_factory))
        self.addCleanup(client.close)

        response = client.get("/health/ready")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Service unavailable"})
        for sensitive_value in (
            "postgresql",
            "user",
            "secret",
            "db.internal",
            "workflow_tracker",
        ):
            self.assertNotIn(sensitive_value, response.text)
        session_factory.return_value.__exit__.assert_called_once()

    def test_readiness_returns_generic_503_on_configuration_failure(
        self,
    ) -> None:
        with patch(
            "backend.app.get_session_factory",
            side_effect=RuntimeError(
                "DATABASE_URL contains postgresql://user:secret@db.internal"
            ),
        ):
            client = TestClient(create_app(), raise_server_exceptions=False)
            self.addCleanup(client.close)

            response = client.get("/health/ready")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Service unavailable"})
        self.assertNotIn("DATABASE_URL", response.text)
        self.assertNotIn("secret", response.text)

    def test_readiness_returns_generic_503_for_malformed_database_port(
        self,
    ) -> None:
        get_session_factory.cache_clear()
        self.addCleanup(get_session_factory.cache_clear)
        database_url = "postgresql+psycopg://localhost:notaport/workflow_tracker_test"

        with patch.dict("os.environ", {"DATABASE_URL": database_url}):
            with TestClient(create_app(), raise_server_exceptions=False) as client:
                response = client.get("/health/ready")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Service unavailable"})


    def test_readiness_returns_generic_503_when_database_driver_is_missing(self) -> None:
        get_session_factory.cache_clear()
        self.addCleanup(get_session_factory.cache_clear)

        with (
            patch.dict("os.environ", {"DATABASE_URL": "postgresql:///workflow_tracker_test"}),
            patch(
                "backend.database.create_engine",
                side_effect=ModuleNotFoundError("No module named 'psycopg2'"),
            ),
            TestClient(create_app(), raise_server_exceptions=False) as client,
        ):
            response = client.get("/health/ready")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Service unavailable"})


if __name__ == "__main__":
    unittest.main()
