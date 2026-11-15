import os
import unittest
from pathlib import Path
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import make_url

from backend.database import create_database_engine, create_session_factory
from backend.db_models import Task


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def require_test_database_url() -> str:
    try:
        database_url = os.environ["TEST_DATABASE_URL"]
    except KeyError as error:
        raise RuntimeError("TEST_DATABASE_URL is not set") from error

    database_name = make_url(database_url).database
    if database_name is None or not database_name.endswith("_test"):
        raise RuntimeError("TEST_DATABASE_URL database name must end with '_test'")

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
        database_name = self.engine.url.database
        if database_name is None or not database_name.endswith("_test"):
            raise RuntimeError("Refusing to clean a database without an '_test' suffix")

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
