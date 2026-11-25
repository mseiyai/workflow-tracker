# CI: recover workflow startup and harden configuration

## Problem

PR #2 has an Actions run that concluded with `startup_failure`.
No useful application-test logs were produced.

Local migration commands also require an explicit `DATABASE_URL`, the
local virtual environment uses Python 3.10, and `requirements.txt`
appears to contain packages unrelated to the application.

## Acceptance criteria

- [ ] GitHub recognizes the CI workflow by name.
- [ ] Every run creates at least one job.
- [ ] Workflow files pass actionlint.
- [ ] CI uses Python 3.13.
- [ ] Backend CI receives explicit `DATABASE_URL` and
      `TEST_DATABASE_URL` values pointing to an isolated test database.
- [ ] Alembic migrations and backend tests pass.
- [ ] Frontend install, lint, and build pass.
- [ ] Docker Compose configuration and image builds pass.
- [ ] requirements.txt contains intentional application dependencies,
      not unrelated packages from a developer environment.
- [ ] No credentials or populated .env files are committed.
- [ ] PR #2 reports green required checks.

## Out of scope

- Production deployment
- Authentication and authorization
- Merging PR #2
- Production secrets
