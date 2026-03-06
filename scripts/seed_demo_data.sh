#!/usr/bin/env bash
set -euo pipefail

primary_id="$(docker compose ps -q postgres-primary)"
if [[ -z "${primary_id}" ]]; then
  echo "Postgres primary is not running. Start it first:"
  echo "  make up"
  exit 1
fi

echo "Waiting for Postgres primary to accept connections..."
deadline="$((SECONDS + 60))"
while true; do
  if docker exec -i "${primary_id}" psql -U app -d appdb -At -c "select 1" >/dev/null 2>&1; then
    break
  fi
  if (( SECONDS >= deadline )); then
    echo "Postgres primary did not become ready within 60s."
    echo "Check logs:"
    echo "  make logs"
    exit 1
  fi
  sleep 2
done

echo "Seeding demo events via append_event + apply_wal..."
docker exec -i "${primary_id}" psql -U app -d appdb -v ON_ERROR_STOP=1 <<'SQL'
-- multi-tenant, multi-workflow sample history
select append_event('tenant-a','wf-001',1,'started', '{"source":"demo"}');
select append_event('tenant-a','wf-001',2,'step',    '{"n":1}');
select append_event('tenant-a','wf-001',3,'step',    '{"n":2}');
select append_event('tenant-a','wf-001',4,'completed','{"ok":true}');

select append_event('tenant-b','wf-002',1,'started', '{"source":"demo"}');
select append_event('tenant-b','wf-002',2,'failed',  '{"reason":"example"}');

-- idempotency: should be a no-op
select append_event('tenant-b','wf-002',2,'failed',  '{"reason":"duplicate"}');

-- apply WAL to history table
select apply_wal(1000);
SQL

echo "Seed complete."
