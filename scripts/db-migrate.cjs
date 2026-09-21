const { spawnSync } = require("child_process");

const migrationCommand = [
  "set -eu",
  'for migration in /docker-entrypoint-initdb.d/schema/migrations/*.sql; do',
  '  [ -f "$migration" ] || continue',
  '  echo "[db-migrate] Applying $(basename "$migration")"',
  '  psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$migration"',
  "done",
].join("\n");

const result = spawnSync(
  "docker",
  [
    "compose",
    "--env-file",
    "backend/.env",
    "exec",
    "-T",
    "postgres",
    "sh",
    "-lc",
    migrationCommand,
  ],
  { cwd: require("path").resolve(__dirname, ".."), stdio: "inherit" }
);

if (result.error) {
  console.error(`[db-migrate] Could not start Docker: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
