# Lesson 10 local CI verification

The latest hosted result inspected, PR #4 run 45776766966 on November 26,
2026, passed all three jobs with 47 backend tests. The final local log records
a separate full verifier run that passed with 56 backend tests.

## Observed local results

`/tmp/workflow-tracker-10d.log` records a full `scripts/verify-local.sh` run
through the API image build and the concluding `Local CI parity checks passed`
message. The script mounts the local working tree in the backend container.
The log does not capture a checkout SHA, Git status at launch, or the outer
shell command used to capture the output, so the local result cannot be
attributed to an exact committed tree.

| Check | Command run by `scripts/verify-local.sh` | Result shown in the final log |
|---|---|---|
| Tracked environment files | `python3 scripts/check_tracked_env.py` | Passed |
| Workflow validation | `docker run --rm -v "$repo_root:/repo" --workdir /repo rhysd/actionlint:latest -color` | Completed with no reported errors |
| Python version | `python --version` in `python:3.13-slim` | Python 3.13.18 |
| pip upgrade | `python -m pip install --upgrade pip` | Installed pip 26.3 |
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

The log contains one unittest summary, `Ran 56 tests in 1.867s` followed by
`OK`. It contains no separate focused test invocation or `git diff --check`
result. The tracked-file check invokes Git on the host. The environment-file
unit tests in `tests/test_ci_guards.py` mock the Git subprocess.

## Successful hosted runs on November 26, 2026

| Run | GitHub event and source commit | Commit checked out by all three jobs | Backend tests | Result |
|---|---|---|---|---|
| [45658751536, attempt 2](https://github.com/mseiyai/workflow-tracker/actions/runs/45658751536/attempts/2) | Push to `main`, `5e3488ea1a95be721a647d06fa653808558c8c49` | `5e3488ea1a95be721a647d06fa653808558c8c49` | 47 passed in 0.767s | All three jobs passed |
| [45776766966, attempt 1](https://github.com/mseiyai/workflow-tracker/actions/runs/45776766966/attempts/1) | PR #4 from `fix/010d-verification-evidence`, `0a094e65ce04c2adf93faecb9a877b919b7cbc3b` | GitHub-generated PR merge commit `af056b6f004b210998fbdfe009180ddef6c3bb6b` | 47 passed in 0.511s | All three jobs passed |

Both runs recorded these commands and passing job results.

| Job | Commands | Result |
|---|---|---|
| Backend tests and migrations | `python scripts/check_tracked_env.py`, `python -m pip install --upgrade pip`, `python -m pip install --requirement requirements.txt`, `python scripts/check_ci_database.py`, `python -m alembic upgrade head`, `python -m unittest discover -s tests -p "test_*.py" -v`, `python -m alembic check` | Guards passed, both migrations applied to the test database, 47 tests passed per run, and no new upgrade operations were detected |
| Frontend production build | `npm ci`, `npm run lint`, `npm run build` from `frontend/` | Install, lint, and build passed |
| Container build | `docker compose config --quiet`, `docker build --tag workflow-tracker-api:ci .` | Compose validation and API image build passed |

## Why the test counts differ

The three logs show the same 47 named tests, including all nine in
`tests/test_ci_guards.py`. The single local discovery run also lists six
cases from `tests/test_ci_checks.py` and three from `tests/test_health.py`,
which account for all nine additional tests. Both files are untracked in the
working tree inspected for this review and absent from both hosted checkout
trees. The logs establish which cases ran. They do not establish the exact
state or contents of the local files when the verifier started.

## Earlier failed attempts

- GitHub reports `startup_failure` and zero jobs for source commit
  `c81c55d75a5f7bd2679ffb149bd84089886bd3d9`, the run recorded in the Lesson
  10C issue.
  [Run 43721148661](https://github.com/mseiyai/workflow-tracker/actions/runs/43721148661)
- The PR #2 run for source commit `3770be031c6d23675b4817c7a972a5994c7a71a0`
  failed with zero steps recorded in each of its three jobs. The previous
  review reported `log not found` when fetching the failed job logs. PR #2
  later merged into `main` as `5e3488ea1a95be721a647d06fa653808558c8c49`.
  [Run 45658142966](https://github.com/mseiyai/workflow-tracker/actions/runs/45658142966)
- The first hosted attempt on `main` commit
  `5e3488ea1a95be721a647d06fa653808558c8c49` also failed with zero steps
  recorded in each job. Attempt 2 on the same commit passed, as recorded above.
  [Run 45658751536, attempt 1](https://github.com/mseiyai/workflow-tracker/actions/runs/45658751536/attempts/1)
- The earlier version of this document reported a local verifier attempt
  that stopped at the API image build because Docker Buildx could not write
  its activity directory. The supplied final log contains the successful
  full run. The earlier failure log was unavailable for this review.
