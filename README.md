# 16-temporal-staff-software-engineer-cloud-data-storage

A production-minded Database Reliability Engineering toolkit: HA lab, backup/PITR drills, and zero-downtime migration playbooks.

## Why this repo exists
This is a portfolio-grade, runnable toolkit that demonstrates how I approach database reliability work:
safe changes, predictable operations, and recovery you can actually trust.

## The top pains this repo addresses
1) Keeping production stable while the system scales—reducing incident frequency, improving MTTR, and building predictable operations (SLOs/runbooks/on-call hygiene).
2) Making databases boring again—high availability, predictable performance, safe backups, and zero/low-downtime migrations with solid tooling and runbooks.
3) Building a data platform people trust—reliable pipelines, clear ownership, data quality checks, and governance that scales without slowing delivery.

## Quick demo (local)
Prereqs: Docker + Docker Compose.

```bash
make demo
```

What you get:
- a Postgres primary + replica setup
- PgBouncer for connection pooling
- scripts to verify replication and run backup/restore drills

## Design decisions (high level)
- Prefer drills and runbooks over “tribal knowledge”.
- Keep the lab small but realistic (replication + pooling + backup).
- Make failure modes explicit and testable.

## What I would do next in production
- Add PITR with WAL archiving + periodic restore tests.
- Add SLOs (p95 query latency, replication lag) and alert thresholds.
- Add automated migration checks (preflight, locks, backout plan).
