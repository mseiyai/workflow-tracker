# Add API liveness and database readiness

Status: Not started

## Business example

The stationery shop needs monitoring that distinguishes an API outage
from a PostgreSQL outage.

## Acceptance criteria

- [ ] Existing GET /health still returns 200 and {"status":"ok"}.
- [ ] GET /health/live returns the same response without accessing PostgreSQL.
- [ ] GET /health/ready executes SELECT 1 through the existing session factory.
- [ ] Readiness returns 200 when the query succeeds.
- [ ] Readiness returns 503 with a generic message on database failure.
- [ ] No response exposes credentials, database URLs, or raw exceptions.
- [ ] Sessions are closed after successful and failed readiness checks.
- [ ] Injected session factories remain supported by create_app.
- [ ] Focused tests cover success, failure, and liveness independence.
- [ ] Compose API health checks use /health/ready.
- [ ] A real database stop/restart demonstrates failure and recovery.

## Non-goals

- Authentication
- Hosting-provider setup
- Database schema changes
- Replacing the existing database/session architecture