import unittest
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from backend.database import Base
from backend.db_models import Task
from backend.seed import TASKS_PATH, seed_tasks


class SeedTasksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.addCleanup(self.engine.dispose)

    def task_count(self, session: Session) -> int:
        return session.scalar(select(func.count()).select_from(Task)) or 0

    def test_seed_imports_json_only_once_without_modifying_it(self) -> None:
        original_tasks = TASKS_PATH.read_bytes()

        with Session(self.engine) as session, session.begin():
            first_insert_count = seed_tasks(session)

        with Session(self.engine) as session, session.begin():
            second_insert_count = seed_tasks(session)
            tasks = session.scalars(select(Task).order_by(Task.id)).all()
            task_values = [(task.title, task.status) for task in tasks]

        self.assertEqual(first_insert_count, 4)
        self.assertEqual(second_insert_count, 0)
        self.assertEqual(
            task_values,
            [
                ("Confirm paper order", "pending"),
                ("Prepare school quotation", "in_progress"),
                ("Deliver printer cartridges", "done"),
                ("Call exercise-book supplier", "pending"),
            ],
        )
        self.assertEqual(TASKS_PATH.read_bytes(), original_tasks)

    def test_seed_skips_a_non_empty_table(self) -> None:
        with Session(self.engine) as session, session.begin():
            session.add(Task(title="Existing task", status="done"))

        with Session(self.engine) as session, session.begin():
            insert_count = seed_tasks(session, Path("missing-tasks.json"))

        with Session(self.engine) as session:
            self.assertEqual(insert_count, 0)
            self.assertEqual(self.task_count(session), 1)


if __name__ == "__main__":
    unittest.main()
