#!/usr/bin/env bash
set -euo pipefail

primary_id="$(docker compose ps -q postgres-primary)"
replica_id="$(docker compose ps -q postgres-replica)"

if [[ -z "${primary_id}" || -z "${replica_id}" ]]; then
  echo "Postgres containers are not running. Start them first:"
  echo "  make up"
  exit 1
fi

echo "Waiting for replica to connect to primary..."
deadline="$((SECONDS + 60))"
while true; do
  count="$(docker exec -i "${primary_id}" psql -U app -d appdb -At -c "select count(*) from pg_stat_replication;" | tr -d '[:space:]' || true)"
  if [[ "${count}" =~ ^[0-9]+$ ]] && [[ "${count}" -ge 1 ]]; then
    break
  fi
  if (( SECONDS >= deadline )); then
    echo "Replication not detected within 60s (pg_stat_replication count=${count:-unknown})."
    echo "Check container logs:"
    echo "  make logs"
    exit 1
  fi
  sleep 2
done

echo "Replication detected."
echo
echo "Replication status on primary:"
docker exec -i "${primary_id}" psql -U app -d appdb -c "select application_name, state, sync_state, write_lag, flush_lag, replay_lag from pg_stat_replication;"

echo
echo "Checking replica is in recovery mode..."
is_recovery="$(docker exec -i "${replica_id}" psql -U app -d appdb -At -c "select pg_is_in_recovery();" | tr -d '[:space:]' || true)"
if [[ "${is_recovery}" != "t" ]]; then
  echo "Expected replica to be in recovery mode (got: ${is_recovery:-empty})."
  exit 1
fi
echo "Replica is in recovery mode (OK)."
