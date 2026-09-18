# Research Findings

## 1. Test Database Strategy

- **Decision**: Use `testcontainers-postgres` to spin up an ephemeral container per test session, with a fallback to `TEST_DATABASE_URL`.
- **Rationale**: The project already relies on Docker (via `docker-compose.yml`). Testcontainers provides a 100% isolated Postgres instance, guaranteeing the development database is never touched. For environments where Docker-in-Docker is difficult, a `TEST_DATABASE_URL` fallback allows testing against a manually provisioned DB.
- **Alternatives considered**: SQLite (rejected by spec due to Postgres-specific constraints and partial unique indexes).

## 2. Database Safety Guard

- **Decision**: A custom pytest fixture/startup hook will parse the database URL before engine creation. It will aggressively assert that `host` is dynamic (from testcontainers) OR that the database name ends with `_test` AND strictly does not equal `settings.POSTGRES_DB` or `settings.database_url`.
- **Rationale**: Prevents accidental data destruction of the main database.
- **Alternatives considered**: Relying on developers to not run destructive commands (unsafe, prone to human error).

## 3. Schema Initialization

- **Decision**: Since Alembic migrations are not to be used, the test session startup fixture will connect to the test database and read the SQL files in `database/migrations/` sequentially (`00_extensions.sql` through `10_indexes.sql`), executing them via async SQLAlchemy text execution.
- **Rationale**: Matches the project's authoritative schema definition without introducing unnecessary tools.
- **Alternatives considered**: Creating a new Alembic migration (explicitly forbidden by spec).

## 4. Test Isolation (Transactions vs Truncation)

- **Decision**: Fast truncation (`TRUNCATE TABLE ... CASCADE`) before each test.
- **Rationale**: If the application services (like `garden_service` or `planning_service`) explicitly call `await session.commit()`, wrapping tests in a single transaction that rolls back at the end will fail because the app commits the transaction. Truncation is safe, handles explicit commits, and is fast enough for integration tests on an ephemeral DB.
- **Alternatives considered**: Nested transactions (SAVEPOINT) - but these can be fragile if the application code uses its own savepoints or commits the root transaction.
