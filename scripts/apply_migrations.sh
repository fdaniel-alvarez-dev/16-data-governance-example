#!/usr/bin/env bash
set -euo pipefail

primary_id="$(docker compose ps -q postgres-primary)"
if [[ -z "${primary_id}" ]]; then
  echo "Postgres primary is not running. Start it first:"
  echo "  make up"
  exit 1
fi

echo "Applying migrations..."
for f in migrations/*.sql; do
  echo " - ${f}"
  docker exec -i "${primary_id}" psql -U app -d appdb -v ON_ERROR_STOP=1 < "${f}"
done
echo "Migrations applied."
