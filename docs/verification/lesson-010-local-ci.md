# Lesson 10 local CI verification

Working branch: `fix/010d-verification-evidence`
Main-derived commit: `5e3488ea1a95be721a647d06fa653808558c8c49`
Final verification log: `/tmp/workflow-tracker-10d.log`

## Observed local results

The final log records one uninterrupted `scripts/verify-local.sh` run. It
reached the concluding `Local CI parity checks passed` message.

| Check | Command run by `scripts/verify-local.sh` | Result shown in the final log |
|---|---|---|
| Tracked environment files | `python3 scripts/check_tracked_env.py` | Passed |
| Workflow validation | `docker run --rm -v "$repo_root:/repo" --workdir /repo rhysd/actionlint:latest -color` | Completed with no reported errors |
| Python version | `python --version` in `python:3.13-slim` | Python 3.13.18 |
| Clean dependency install | `python -m pip install --requirement requirements.txt` | Passed |
| Dependency consistency | `python -m pip check` | Passed; no broken requirements found |
| Test database guard | `python scripts/check_ci_database.py` | Passed before migration |
| Alembic migration | `python -m alembic upgrade head` | Applied both recorded migrations |
| Backend tests | `python -m unittest discover -s tests -p "test_*.py" -v` | Passed, 56 tests |
| Migration drift | `python -m alembic check` | Passed; no new upgrade operations detected |
| Frontend install | `npm --prefix frontend ci` | Passed; 0 vulnerabilities reported |
| Frontend lint | `npm --prefix frontend run lint` | Passed; 0 warnings and 0 errors |
| Frontend build | `npm --prefix frontend run build` | Passed |
| Compose validation | `POSTGRES_PASSWORD=local-ci-only docker compose --file compose.yaml config --quiet` | Completed with no reported errors |
| API image build | `POSTGRES_PASSWORD=local-ci-only docker compose --file compose.yaml build api` | Passed; `workflow-tracker-api` built |

The 56-test suite included the nine tests in `tests/test_ci_guards.py`. The
log does not show a separate focused guard-test command or a `git diff
--check` run, so neither is recorded as part of this local verification.

The full script finished successfully. No Git installation was needed for
the mocked guard tests: the backend container ran the suite using the
dependencies installed from `requirements.txt`.

## Hosted CI

PR #2 used branch `lesson/010-github-ci` at source commit
[`3770be031c6d23675b4817c7a972a5994c7a71a0`](https://github.com/mseiyai/workflow-tracker/commit/3770be031c6d23675b4817c7a972a5994c7a71a0).
The inspected [pull-request CI run
45658142966](https://github.com/mseiyai/workflow-tracker/actions/runs/45658142966)
completed with failure on that commit. Its backend, frontend, and container
jobs each reported failure before recording any steps. GitHub returned `log
not found` when the failed-run log was inspected.

PR #2 was subsequently merged into `main` as commit
`5e3488ea1a95be721a647d06fa653808558c8c49`. The inspected hosted run is not
a successful GitHub-hosted verification.
