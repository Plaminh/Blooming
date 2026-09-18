# Backend Test Suite Quickstart

This guide outlines how to execute and validate the new test coverage. 
*Note: Test implementation is pending. These commands validate the infrastructure.*

## Prerequisites

- Python 3.11+
- Docker running (for `testcontainers`)
- Project dependencies installed with test extras

## 1. Install Test Dependencies

```bash
pip install -r backend/requirements.txt
pip install pytest pytest-asyncio httpx testcontainers[postgres] pytest-env
```

## 2. Execute Full Test Suite

The simplest and safest way to run all tests. The infrastructure will automatically spin up an ephemeral PostgreSQL instance, run migrations, and tear it down.

```bash
cd backend
pytest tests/
```

## 3. Run Specific Test Modules

```bash
# Pure unit tests (fastest, no DB required)
pytest tests/unit/test_scheduler.py

# Service-level integration tests (spins up DB)
pytest tests/services/test_planning_service.py
pytest tests/services/test_reminders_service.py

# API route testing
pytest tests/api/test_focus_routes.py
```

## 4. Testing with a Manual Local Database (Fallback)

If Docker is unavailable, you can use an explicit test database URL.
**Safety Check**: The database name MUST end with `_test`.

```bash
# Unix/macOS
export TEST_DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/blooming_test"
pytest tests/

# PowerShell
$env:TEST_DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/blooming_test"
pytest tests/
```

## Expected Outcomes

- **Safety**: Running these tests will NEVER modify your main development database.
- **Speed**: Thanks to `TEMPLATE` database cloning, integration tests run quickly.
- **Determinism**: No tests should fail due to wall-clock time or local timezone settings.
