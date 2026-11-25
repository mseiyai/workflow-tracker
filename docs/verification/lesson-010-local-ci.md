# Lesson 10 local CI verification

Date: 2026-11-25
Working branch: lesson/011a-deployment-readiness
PR branch: lesson/010-github-ci
Pull request: #2

## Observed local results

| Check | Command | Result |
|---|---|---|
| Focused CI guard tests | `.venv/bin/python -m unittest tests.test_ci_checks -v` | Passed, 6 tests |
| Tracked environment files | `python3 scripts/check_tracked_environment_files.py` through `scripts/verify-local.sh` | Passed |
| Workflow validation | `rhysd/actionlint:latest` through `scripts/verify-local.sh` | Passed |
| Python version | `python --version` in `python:3.13-slim` | Python 3.13.18 |
| Clean dependency install | `python -m pip install --requirement requirements.txt` | Passed |
| Dependency consistency | `python -m pip check` | Passed, no broken requirements |
| Test database guard | `python scripts/check_ci_database.py` | Passed before migration |
| Alembic migration | `python -m alembic upgrade head` | Passed against `workflow_tracker_test` |
| Backend tests | `python -m unittest discover -s tests -p "test_*.py" -v` | Passed, 46 tests |
| Migration drift | `python -m alembic check` | Passed, no new upgrade operations |
| Frontend install | `npm --prefix frontend ci` | Passed, 0 vulnerabilities reported |
| Frontend lint | `npm --prefix frontend run lint` | Passed |
| Frontend build | `npm --prefix frontend run build` | Passed |
| Compose validation | `POSTGRES_PASSWORD=local-ci-only docker compose --file compose.yaml config --quiet` | Passed |
| API image build | `POSTGRES_PASSWORD=local-ci-only docker compose --file compose.yaml build api` | Passed |
| Whitespace validation | `git diff --check` | Passed |

The first complete-suite attempt exposed that `python:3.13-slim` did not
contain Git, which the temporary-repository policy tests require. After the
local verifier installed Git in its disposable backend container, all 46
tests passed.

The subsequent `scripts/verify-local.sh` run completed every check through
Compose validation. Its final image-build step could not update the sandbox's
read-only Docker Buildx activity directory. Running the same Compose API build
with that directory available then passed. Therefore, the individual local
checks have observed passing results, but this environment did not produce a
single uninterrupted full-script run.

## Hosted CI

The account billing blocker was reported resolved.
Hosted CI verification for the finishing changes is pending.
See PR #2 for the latest run and tested commit.

Local verification is not a substitute for a successful GitHub-hosted
run. PR #2 must remain unmerged until hosted CI is rerun or a deliberate
human decision records an exception.

## Remaining blocker

Make the workflow dispatchable from GitHub (or create a new run by updating
the PR branch), then record the hosted result. No push was made as part of
this verification.
