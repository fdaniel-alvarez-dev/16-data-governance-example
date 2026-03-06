#!/usr/bin/env bash
set -euo pipefail

latest="$(ls -1 artifacts/backups/*.sql 2>/dev/null | tail -n 1 || true)"
if [[ -z "${latest}" ]]; then
  echo "No backups found under artifacts/backups/. Run: make backup"
  exit 1
fi

primary_id="$(docker compose ps -q postgres-primary)"
if [[ -z "${primary_id}" ]]; then
  echo "Postgres primary is not running. Start it first:"
  echo "  make up"
  exit 1
fi

verify_db="${RESTORE_VERIFY_DB:-appdb_verify}"

echo "Restoring latest backup into isolated verify database: ${verify_db}"
echo "Backup: ${latest}"

docker exec -i "${primary_id}" psql -U app -d postgres -v ON_ERROR_STOP=1 -c "drop database if exists ${verify_db} with (force);"
docker exec -i "${primary_id}" psql -U app -d postgres -v ON_ERROR_STOP=1 -c "create database ${verify_db};"

docker exec -i "${primary_id}" psql -U app -d "${verify_db}" -v ON_ERROR_STOP=1 < "${latest}"

echo
echo "Verifying restore outcome..."
docker exec -i "${primary_id}" psql -U app -d "${verify_db}" -v ON_ERROR_STOP=1 -c "select now() as verified_at, count(*) as events_count from workflow_events;" >/dev/null
echo "Restore verification passed (OK)."
