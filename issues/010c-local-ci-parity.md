# CI: establish local parity while hosted runners are blocked

## Problem

GitHub Actions run 43721148661 did not create any jobs.

GitHub subsequently reported that the job was not started because recent
account payments failed or the account spending limit must be increased.
Therefore, the observed failure is an external billing/runner blocker, not
evidence that application tests failed.

## Goal

Create a repeatable local verification command that exercises the same
categories of checks intended for GitHub Actions.

## Acceptance criteria

- [ ] A repository script runs from the project root in WSL2.
- [ ] Workflow YAML passes actionlint.
- [ ] Backend dependencies install in a clean Python 3.13 container.
- [ ] Alembic migrations run against an isolated PostgreSQL test database.
- [ ] Backend tests pass.
- [ ] Frontend dependencies install with npm ci.
- [ ] Frontend lint and production build pass.
- [ ] Docker Compose configuration validates.
- [ ] Application container images build.
- [ ] No credentials or populated .env files are committed.
- [ ] PR #2 distinguishes local verification from blocked hosted CI.
- [ ] GitHub-hosted checks are rerun after the billing block is cleared.

## Out of scope

- Claiming GitHub Actions passed
- Merging PR #2
- Production deployment
- Production credentials
- Replacing the current CI workflow without evidence of a workflow defect

## External blocker

GitHub Actions is blocked by the account's payment or Actions budget state.