import io
import os
import subprocess
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import check_ci_database, check_tracked_env


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class CiDatabaseGuardTests(unittest.TestCase):
    safe_url = (
        "postgresql+psycopg://ci-user:super-secret@database.example/"
        "workflow_tracker_test"
    )

    def run_guard(self, environment: dict[str, str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()

        with (
            patch.dict(os.environ, environment, clear=True),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            result = check_ci_database.main()

        return result, stdout.getvalue(), stderr.getvalue()

    def test_safe_database_urls_are_accepted(self) -> None:
        result, stdout, stderr = self.run_guard(
            {
                "DATABASE_URL": self.safe_url,
                "TEST_DATABASE_URL": self.safe_url,
            }
        )

        self.assertEqual(result, 0)
        self.assertEqual(stdout, "CI database contract OK.\n")
        self.assertEqual(stderr, "")

    def test_each_required_database_url_is_enforced(self) -> None:
        for missing_name in ("DATABASE_URL", "TEST_DATABASE_URL"):
            with self.subTest(missing_name=missing_name):
                environment = {
                    "DATABASE_URL": self.safe_url,
                    "TEST_DATABASE_URL": self.safe_url,
                }
                del environment[missing_name]

                result, stdout, stderr = self.run_guard(environment)

                self.assertNotEqual(result, 0)
                self.assertEqual(stdout, "")
                self.assertIn(f"{missing_name} must be set", stderr)

    def test_malformed_database_url_is_rejected_without_raw_parser_error(self) -> None:
        malformed_url = "not a database URL [super-secret"

        result, stdout, stderr = self.run_guard(
            {
                "DATABASE_URL": malformed_url,
                "TEST_DATABASE_URL": self.safe_url,
            }
        )

        self.assertNotEqual(result, 0)
        self.assertEqual(stdout, "")
        self.assertIn("DATABASE_URL is not a valid PostgreSQL URL", stderr)
        self.assertNotIn(malformed_url, stderr)
        self.assertNotIn("Could not parse", stderr)

    def test_non_postgresql_and_non_test_databases_are_rejected(self) -> None:
        unsafe_urls = (
            "sqlite:///workflow_tracker_test",
            "postgresql+psycopg://ci-user:super-secret@database.example/"
            "workflow_tracker",
        )

        for unsafe_url in unsafe_urls:
            with self.subTest(unsafe_url=unsafe_url):
                result, stdout, stderr = self.run_guard(
                    {
                        "DATABASE_URL": self.safe_url,
                        "TEST_DATABASE_URL": unsafe_url,
                    }
                )

                self.assertNotEqual(result, 0)
                self.assertEqual(stdout, "")
                self.assertIn("TEST_DATABASE_URL", stderr)
                self.assertNotIn("ci-user", stderr)
                self.assertNotIn("super-secret", stderr)
                self.assertNotIn("database.example", stderr)

    def test_connection_options_are_rejected_without_disclosing_values(self) -> None:
        for name in ("DATABASE_URL", "TEST_DATABASE_URL"):
            for query in ("dbname=private_database", "sslmode=require"):
                with self.subTest(name=name, query=query):
                    environment = dict.fromkeys(
                        ("DATABASE_URL", "TEST_DATABASE_URL"), self.safe_url
                    )
                    environment[name] = f"{self.safe_url}?{query}"

                    result, stdout, stderr = self.run_guard(environment)

                    self.assertEqual(result, 1)
                    self.assertEqual(stdout, "")
                    self.assertEqual(stderr, f"{name} must not include query options\n")


class TrackedEnvironmentGuardTests(unittest.TestCase):
    def run_guard(
        self,
        tracked_output: str = "",
        *,
        git_error: Exception | None = None,
        arguments: list[str] | None = None,
    ) -> tuple[int, str, str, list[str]]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        completed = subprocess.CompletedProcess(
            ["git", "ls-files", "-z"], 0, tracked_output, ""
        )
        side_effect = git_error

        with (
            patch(
                "scripts.check_tracked_env.subprocess.run",
                return_value=completed,
                side_effect=side_effect,
            ) as run_git,
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            result = check_tracked_env.main(arguments or [])

        command = run_git.call_args.args[0]
        return result, stdout.getvalue(), stderr.getvalue(), command

    def test_environment_templates_are_allowed_at_any_depth(self) -> None:
        result, stdout, stderr, _ = self.run_guard(
            ".env.example\0frontend/.env.example\0nested/file.txt\0"
        )

        self.assertEqual(result, 0)
        self.assertEqual(stdout, "Tracked environment file check passed.\n")
        self.assertEqual(stderr, "")

    def test_environment_files_are_rejected_at_any_depth(self) -> None:
        tracked_files = ".env\0frontend/.env.production\0deep/path/.env.local\0"

        result, stdout, stderr, _ = self.run_guard(tracked_files)

        self.assertNotEqual(result, 0)
        self.assertEqual(stdout, "")
        self.assertIn(".env\n", stderr)
        self.assertIn("frontend/.env.production", stderr)
        self.assertIn("deep/path/.env.local", stderr)

    def test_git_inspection_failure_is_rejected_without_raw_error(self) -> None:
        raw_error = "fatal: unsafe repository secret-value"

        result, stdout, stderr, _ = self.run_guard(
            git_error=subprocess.CalledProcessError(
                128, ["git", "ls-files", "-z"], stderr=raw_error
            )
        )

        self.assertNotEqual(result, 0)
        self.assertEqual(stdout, "")
        self.assertIn("Unable to inspect tracked files", stderr)
        self.assertNotIn(raw_error, stderr)

    def test_repo_argument_is_used_for_git_inspection(self) -> None:
        repository = PROJECT_ROOT / "isolated-repository"

        result, _, _, command = self.run_guard(
            arguments=["--repo", str(repository)]
        )

        self.assertEqual(result, 0)
        self.assertEqual(
            command,
            ["git", "-C", str(repository), "ls-files", "-z"],
        )


if __name__ == "__main__":
    unittest.main()
