from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATABASE = ROOT / "database"


def test_baseline_records_version_zero_and_includes_every_table_file():
    install = (DATABASE / "install.sql").read_text(encoding="utf-8")
    for table in sorted((DATABASE / "tables").glob("*.sql")):
        assert f"\\ir tables/{table.name}" in install
    assert "INSERT INTO schema_migrations (version) VALUES ('000')" in install


def test_migrations_are_ordered_unique_and_transaction_safe_runner_exists():
    migrations = sorted((DATABASE / "migrations").glob("*.sql"))
    versions = [path.name.split("_", 1)[0] for path in migrations]
    assert versions == sorted(versions)
    assert len(versions) == len(set(versions))
    assert versions[-1] == "001"
    runner = (ROOT / "scripts" / "migrate.sh").read_text(encoding="utf-8")
    assert "ON_ERROR_STOP=1" in runner
    assert "--single-transaction" in runner
    assert "schema_migrations" in runner


def test_unversioned_database_is_verified_before_baseline_stamp():
    runner = (ROOT / "scripts" / "migrate.sh").read_text(encoding="utf-8")
    verification = "tests/01_baseline_compatibility.sql"
    assert verification in runner
    assert runner.index(verification) < runner.index("INSERT INTO schema_migrations(version) VALUES ('000')")
    compatibility = (DATABASE / verification).read_text(encoding="utf-8")
    for required in ("users", "focus_runs", "reward_events", "idempotency_key", "pgcrypto"):
        assert required in compatibility
