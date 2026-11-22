#!/usr/bin/env bash
set -Eeuo pipefail

quick_mode=0

case "${1:-}" in
  "")
    ;;
  --quick)
    quick_mode=1
    ;;
  *)
    printf 'Usage: %s [--quick]\n' "$0" >&2
    exit 2
    ;;
esac

repo_root="$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
  pwd
)"

cd "$repo_root"

db_container="workflow-tracker-verify-$$"
db_port="${VERIFY_DB_PORT:-55432}"

cleanup() {
  docker rm --force "$db_container" >/dev/null 2>&1 || true
}

trap cleanup EXIT

section() {
  printf '\n==> %s\n' "$1"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Required command not found: %s\n' "$1" >&2
    exit 1
  fi
}

require_command docker
require_command npm

section "Validate GitHub Actions workflows"

docker run --rm \
  -v "$repo_root:/repo" \
  --workdir /repo \
  rhysd/actionlint:latest -color

section "Start isolated PostgreSQL test database"

docker run \
  --name "$db_container" \
  --rm \
  --detach \
  --env POSTGRES_USER=workflow \
  --env POSTGRES_PASSWORD=workflow \
  --env POSTGRES_DB=workflow_tracker_test \
  --publish "127.0.0.1:${db_port}:5432" \
  postgres:17

database_ready=0

for attempt in {1..30}; do
  if docker exec "$db_container" \
    pg_isready \
      --username workflow \
      --dbname workflow_tracker_test >/dev/null 2>&1; then
    database_ready=1
    break
  fi

  sleep 1
done

if [[ "$database_ready" -ne 1 ]]; then
  printf 'PostgreSQL did not become ready within 30 seconds.\n' >&2
  exit 1
fi

test_database_url="postgresql+psycopg://workflow:workflow@localhost:${db_port}/workflow_tracker_test"

section "Verify backend with Python 3.13"

docker run --rm \
  --network host \
  -v "$repo_root:/work" \
  --workdir /work \
  --env DATABASE_URL="$test_database_url" \
  --env TEST_DATABASE_URL="$test_database_url" \
  python:3.13-slim \
  sh -euc '
    python --version
    python -m pip install --upgrade pip
    python -m pip install --requirement requirements.txt
    python -m pip check
    python scripts/check_ci_database.py
    python -m alembic upgrade head
    python -m unittest discover -s tests -p "test_*.py" -v
    python -m alembic check
  '

section "Verify frontend"

npm --prefix frontend ci
npm --prefix frontend run lint
npm --prefix frontend run build

section "Validate Docker Compose"

POSTGRES_PASSWORD=local-ci-only \
  docker compose --file compose.yaml config --quiet

if [[ "$quick_mode" -eq 0 ]]; then
  section "Build application images"

  POSTGRES_PASSWORD=local-ci-only \
    docker compose --file compose.yaml build api
else
  section "Skip application image build in quick mode"
fi

section "Checking for tracked environment files..."

tracked_env_files="$(
  git ls-files | grep -E '(^|/)\.env($|\.)' |
    grep -Ev '(^|/)\.env\.example$' || true
)"

if [[ -n "$tracked_env_files" ]]; then
  echo "ERROR: Tracked environment files detected:"
  printf '%s\n' "$tracked_env_files"
  echo "Only .env.example files may be tracked."
  exit 1
fi

echo "Tracked environment file check passed."

section "Local CI parity checks passed"
