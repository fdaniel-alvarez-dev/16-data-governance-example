-- Schema for a durable, queryable append-only history with a WAL-like staging table.
-- This is intentionally small, but the invariants mirror production patterns:
-- - idempotent writes via a natural key
-- - append-only history
-- - lifecycle controls (archive + retention)

create table if not exists workflow_wal (
  tenant_id text not null,
  workflow_id text not null,
  event_id bigint not null,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  primary key (tenant_id, workflow_id, event_id)
);

create table if not exists workflow_events (
  tenant_id text not null,
  workflow_id text not null,
  event_id bigint not null,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  primary key (tenant_id, workflow_id, event_id)
);

create table if not exists workflow_events_archive (
  like workflow_events including all
);

create index if not exists idx_workflow_events_created_at on workflow_events (created_at);
create index if not exists idx_workflow_events_archive_created_at on workflow_events_archive (created_at);

create or replace function apply_wal(batch_size int default 500)
returns int
language plpgsql
as $$
declare
  moved int := 0;
begin
  with batch as (
    select tenant_id, workflow_id, event_id, event_type, payload, created_at
    from workflow_wal
    order by created_at asc
    limit batch_size
    for update skip locked
  ), ins as (
    insert into workflow_events (tenant_id, workflow_id, event_id, event_type, payload, created_at)
    select tenant_id, workflow_id, event_id, event_type, payload, created_at
    from batch
    on conflict do nothing
    returning 1
  ), del as (
    delete from workflow_wal w
    using batch b
    where w.tenant_id=b.tenant_id and w.workflow_id=b.workflow_id and w.event_id=b.event_id
    returning 1
  )
  select coalesce(sum(1),0) into moved from del;

  return moved;
end;
$$;

create or replace function append_event(p_tenant_id text, p_workflow_id text, p_event_id bigint, p_event_type text, p_payload jsonb default '{}'::jsonb)
returns void
language plpgsql
as $$
begin
  insert into workflow_wal (tenant_id, workflow_id, event_id, event_type, payload)
  values (p_tenant_id, p_workflow_id, p_event_id, p_event_type, p_payload)
  on conflict do nothing;
end;
$$;
