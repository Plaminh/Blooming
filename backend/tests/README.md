# Backend Tests

This directory contains the automated tests for the Blooming backend.

## Safety First

**NEVER use your development or production database for testing.**
The test suite is designed to be completely isolated and will reject any attempt to run against the main development database. 
By default, tests use an ephemeral PostgreSQL container via `testcontainers-postgres`.

## Commands

Run these commands from the `backend/` directory:

- **Unit tests (fast, no DB)**: `pytest tests/unit/`
- **Integration tests (DB required)**: `pytest tests/services/`
- **Full suite**: `pytest tests/`

## Troubleshooting

If Docker is unavailable, you can provide an explicit test database URL. The database name MUST end with `_test`.
The provided user MUST have the `CREATEDB` privilege, because the testing strategy relies on creating temporary template and per-test databases.

**macOS/Linux** (from the `backend/` directory):
```bash
export TEST_DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/blooming_test"
pytest tests/
```

**PowerShell** (from the `backend/` directory):
```powershell
$env:TEST_DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/blooming_test"
pytest tests/
```

## CI Usage

In CI, ensure a PostgreSQL service is available and set `TEST_DATABASE_URL` with a user that has `CREATEDB` permissions.
The test framework cleans up its own ephemeral databases automatically. If a crash occurs, drop any databases matching `test_db_%` manually.