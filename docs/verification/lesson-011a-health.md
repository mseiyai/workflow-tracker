# Lesson 11A verification

Date: 2026-11-26
Branch: lesson/011a-deployment-readiness
Source commit before verification: 009a00f
Working-tree changes included in verification: resolved but uncommitted merge of
origin/main at 47f80c3, including the Lesson 10D CI guards and local verifier
updates; no stash content was applied

## Observed results

- Focused health-test command and test count: `.venv/bin/python -m unittest
  tests.test_health -v`; 6 tests passed.
- Full verifier command, test count, and exit status:
  `scripts/verify-local.sh`; 53 tests passed; exit status 0. The verifier also
  passed dependency, migration, migration-drift, frontend install/lint/build,
  Compose validation, and API image-build checks.
- /health compatibility: returned HTTP 200 and `{"status":"ok"}` against the
  isolated Compose stack.
- /health/live with PostgreSQL running: returned HTTP 200 and
  `{"status":"ok"}`.
- /health/ready with PostgreSQL running: returned HTTP 200 and
  `{"status":"ok"}`.
- Liveness during PostgreSQL outage: after `docker compose stop db`, returned
  HTTP 200 and `{"status":"ok"}`.
- Readiness during PostgreSQL outage: returned HTTP 503 and the generic
  `{"detail":"Service unavailable"}` response.
- Readiness after recovery: after `docker compose start db` and database health
  recovery, returned HTTP 200 and `{"status":"ok"}`.
- Compose health status: API and PostgreSQL were both reported healthy before
  the outage and after recovery. Verification used the isolated Compose project
  `workflow-tracker-011a-verify` and ended with `docker compose down` without
  deleting its named volume.
- Review findings and resolutions: all seven named stashed files were identical
  to their `origin/main` counterparts and were not applied. The three add/add
  conflicts retained the validated `origin/main` CI workflow, local verifier,
  and Lesson 10D evidence. `HealthRepository` and its `SELECT 1` implementation
  are present on the Lesson 11A branch, and the focused tests confirm the prior
  import failure is resolved.

## Hosted CI

Pending publication of the reviewed changes. No hosted run was performed for
this uncommitted merge result.

## Limitations

- The merge remains uncommitted because this verification was explicitly run
  without committing; `origin/main` is therefore not yet part of branch
  history.
- A first Compose startup using the pre-existing default project volume failed
  during migration because that volume was initialized with different database
  credentials. The volume was preserved. The outage and recovery evidence above
  comes from a fresh isolated Compose project.
- The direct `.venv/bin/python -m unittest discover -s tests -v` invocation
  without database environment variables ran 31 tests and reported three
  integration setup errors, each correctly refusing to run without
  `TEST_DATABASE_URL`. The complete 53-test suite passed in the verifier against
  its isolated `_test` database.
