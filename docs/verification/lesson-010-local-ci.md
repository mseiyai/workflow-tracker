# Lesson 10 local CI verification

Date: 2026-11-22
Branch: lesson/010-github-ci
Pull request: #2

## Observed local results

| Check | Command | Result |
|---|---|---|
| Workflow validation | actionlint through verify-local.sh | Pass/Fail |
| Python version | python:3.13-slim | Observed version |
| Dependency consistency | python -m pip check | Pass/Fail |
| Alembic migration | python -m alembic upgrade head | Pass/Fail |
| Backend tests | Repository test command | Pass/Fail |
| Frontend install | npm ci | Pass/Fail |
| Frontend lint | npm run lint | Pass/Fail |
| Frontend build | npm run build | Pass/Fail |
| Compose validation | docker compose config --quiet | Pass/Fail |
| Image build | docker compose build | Pass/Fail |

## Hosted CI status

Blocked. GitHub reported that jobs could not start because of the
account's payment or Actions spending-limit state.

Local verification is not a substitute for a successful GitHub-hosted
run. PR #2 must remain unmerged until hosted CI is rerun or a deliberate
human decision records an exception.

## Remaining blocker

Resolve the GitHub billing or Actions budget condition, then rerun the
workflow and record the hosted result.