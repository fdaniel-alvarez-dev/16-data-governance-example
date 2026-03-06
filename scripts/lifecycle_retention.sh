#!/usr/bin/env bash
set -euo pipefail

primary_id="$(docker compose ps -q postgres-primary)"
if [[ -z "${primary_id}" ]]; then
  echo "Postgres primary is not running. Start it first:"
  echo "  make up"
  exit 1
fi

archive_older_than_hours="${ARCHIVE_OLDER_THAN_HOURS:-0}"
retention_hours="${RETENTION_HOURS:-24}"

echo "Applying lifecycle policy:"
echo "- archive rows older than: ${archive_older_than_hours}h"
echo "- delete archive rows older than: ${retention_hours}h"

docker exec -i "${primary_id}" psql -U app -d appdb -v ON_ERROR_STOP=1 <<SQL
with moved as (
  insert into workflow_events_archive
  select *
  from workflow_events
  where created_at < now() - interval '${archive_older_than_hours} hours'
  on conflict do nothing
  returning 1
)
delete from workflow_events
where created_at < now() - interval '${archive_older_than_hours} hours';

delete from workflow_events_archive
where created_at < now() - interval '${retention_hours} hours';
SQL

echo "Lifecycle policy applied."
