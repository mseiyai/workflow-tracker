import unittest

from backend.summary import summarize_tasks


class SummarizeTasksTests(unittest.TestCase):
    def test_empty_list(self) -> None:
        tasks = []

        self.assertEqual(
            summarize_tasks(tasks),
            {
                "total": 0,
                "pending": 0,
                "in_progress": 0,
                "done": 0,
                "open": 0,
            },
        )
        self.assertEqual(tasks, [])

    def test_all_documented_statuses(self) -> None:
        tasks = [
            {"id": 1, "title": "First", "status": "pending"},
            {"id": 2, "title": "Second", "status": "in_progress"},
            {"id": 3, "title": "Third", "status": "done"},
        ]
        original_tasks = [task.copy() for task in tasks]

        self.assertEqual(
            summarize_tasks(tasks),
            {
                "total": 3,
                "pending": 1,
                "in_progress": 1,
                "done": 1,
                "open": 2,
            },
        )
        self.assertEqual(tasks, original_tasks)

    def test_all_done(self):
        tasks = [{"status": "done"}, {"status": "done"}]

        self.assertEqual(
            summarize_tasks(tasks),
            {
                "total": 2,
                "pending": 0,
                "in_progress": 0,
                "done": 2,
                "open": 0,
            },
        )

if __name__ == "__main__":
    unittest.main()
