import os
import unittest
from pathlib import Path
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import URL

from backend.database import create_database_engine, create_session_factory
from backend.db_models import Task
from scripts.check_ci_database import validate_database_url


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def require_safe_test_url(value: str | URL) -> None:
    try:
        validate_database_url("TEST_DATABASE_URL", value)
    except ValueError as error:
        raise RuntimeError(str(error)) from None


def require_test_database_url() -> str:
    database_url = os.environ.get("TEST_DATABASE_URL", "")
    require_safe_test_url(database_url)
    return database_url


class PostgresIntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.database_url = require_test_database_url()

        alembic_config = Config(PROJECT_ROOT / "alembic.ini")
        with patch.dict(os.environ, {"DATABASE_URL": cls.database_url}):
            command.upgrade(alembic_config, "head")

        cls.engine = create_database_engine(cls.database_url)
        cls.session_factory = create_session_factory(cls.engine)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.engine.dispose()
        super().tearDownClass()

    def setUp(self) -> None:
        super().setUp()
        self.reset_tasks()

    def reset_tasks(self) -> None:
        require_safe_test_url(self.engine.url)

        with self.engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY"))

    def insert_tasks(self, tasks: list[dict[str, object]]) -> None:
        with self.session_factory.begin() as session:
            session.add_all(Task(**task) for task in tasks)
            session.flush()
            session.execute(
                text(
                    "SELECT setval(pg_get_serial_sequence('tasks', 'id'), "
                    "(SELECT MAX(id) FROM tasks), true)"
                )
            )
