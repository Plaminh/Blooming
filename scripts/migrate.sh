#!/bin/sh
set -eu

DATABASE_URL="${DATABASE_URL:-}"
if [ -z "$DATABASE_URL" ] && [ -z "${PGDATABASE:-}" ]; then
  echo "DATABASE_URL or PGDATABASE is required" >&2
  exit 2
fi
ROOT_DIR="${MIGRATION_ROOT:-/app/database}"

run_psql() {
  if [ -n "$DATABASE_URL" ]; then
    psql "$DATABASE_URL" "$@"
  else
    psql "$@"
  fi
}

# Empty DB: install baseline 000. Existing unversioned DB: verify before
# stamping 000. Versioned DBs skip both branches and apply pending files only.
has_baseline="$(run_psql -Atqc "SELECT to_regclass('public.users') IS NOT NULL")"
has_version_table="$(run_psql -Atqc "SELECT to_regclass('public.schema_migrations') IS NOT NULL")"
if [ "$has_version_table" = "t" ]; then
  : # Versioned database: apply pending migrations below.
elif [ "$has_baseline" != "t" ]; then
  run_psql -v ON_ERROR_STOP=1 -f "$ROOT_DIR/install.sql"
else
  run_psql -v ON_ERROR_STOP=1 \
    -f "$ROOT_DIR/tests/01_baseline_compatibility.sql"
  run_psql -v ON_ERROR_STOP=1 <<'SQL'
CREATE TABLE IF NOT EXISTS schema_migrations (
  version VARCHAR(64) PRIMARY KEY,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO schema_migrations(version) VALUES ('000') ON CONFLICT DO NOTHING;
SQL
fi

for migration in "$ROOT_DIR"/migrations/*.sql; do
  [ -e "$migration" ] || continue
  filename="$(basename "$migration")"
  version="${filename%%_*}"
  applied="$(run_psql -Atqc "SELECT EXISTS(SELECT 1 FROM schema_migrations WHERE version = '$version')")"
  if [ "$applied" = "t" ]; then
    continue
  fi
  run_psql -v ON_ERROR_STOP=1 --single-transaction \
    -f "$migration" \
    -c "INSERT INTO schema_migrations(version) VALUES ('$version')"
done
