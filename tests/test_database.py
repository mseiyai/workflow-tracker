import os
import unittest
from unittest.mock import patch

from sqlalchemy import CheckConstraint


class DatabaseModelTests(unittest.TestCase):
    def test_database_url_comes_from_environment(self) -> None:
        from backend.database import get_database_url

        expected_url = "postgresql+psycopg://user:password@localhost/workflow_tracker"

        with patch.dict(os.environ, {"DATABASE_URL": expected_url}, clear=True):
            self.assertEqual(get_database_url(), expected_url)

    def test_database_url_is_required(self) -> None:
        from backend.database import get_database_url

        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "DATABASE_URL"):
                get_database_url()

    def test_task_table_matches_the_initial_schema(self) -> None:
        from backend.db_models import Task

        table = Task.__table__

        self.assertEqual(table.name, "tasks")
        self.assertTrue(table.c.id.primary_key)
        self.assertIsNotNone(table.c.id.server_default)
        self.assertFalse(table.c.title.nullable)
        self.assertEqual(table.c.title.type.length, 120)
        self.assertFalse(table.c.status.nullable)
        self.assertEqual(table.c.status.type.length, 11)

        status_constraints = [
            constraint
            for constraint in table.constraints
            if isinstance(constraint, CheckConstraint)
        ]
        self.assertEqual(len(status_constraints), 1)
        constraint_sql = str(status_constraints[0].sqltext)
        for status in ("pending", "in_progress", "done"):
            self.assertIn(status, constraint_sql)

        self.assertTrue(
            any(
                [column.name for column in index.columns] == ["status"]
                for index in table.indexes
            )
        )


if __name__ == "__main__":
    unittest.main()
