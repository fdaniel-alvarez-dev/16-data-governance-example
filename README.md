# 16-aws-reliability-governance-postgres

A production-minded storage governance lab: durable append-only history, lifecycle (retention/tiering), and auditable reliability drills on Postgres.

Focus: postgres


## Why this repo exists
This is a portfolio-grade, runnable reference that demonstrates how to design and operate a persistence layer that can be trusted for years:
durability, correctness, lifecycle management, and measurable reliability.

## The top pains this repo addresses
1) Durable, queryable history—an append-only model with idempotency and a write-ahead staging table (a practical “WAL-like” pattern).
2) Lifecycle and cost control—retention and “tiering” (moving cold data to an archive table) with explicit evidence artifacts.
3) Reliability you can measure—replication checks, backup/restore verification, and a production-mode audit report (guarded).

## Quick demo (local)
Prereqs: Docker + Docker Compose.

```bash
make demo
```

What you get:
- a Postgres primary + replica setup
- PgBouncer for connection pooling
- scripts to apply schema, ingest demo events, enforce lifecycle, and run verified backup/restore drills

## Design decisions (high level)
- Prefer drills and runbooks over “tribal knowledge”.
- Keep the lab small but realistic (replication + pooling + backup).
- Make failure modes explicit and testable.

## What I would do next in production
- Add PITR with WAL archiving + periodic restore tests.
- Add SLOs (p95 query latency, replication lag) and alert thresholds.
- Add automated migration checks (preflight, locks, backout plan).

## Tests (two modes)
This repository supports exactly two test modes via `TEST_MODE`:

- `demo`: fast, offline checks against fixtures only (no Docker calls).
- `production`: real integration checks against Dockerized Postgres when properly configured.

Demo:
```bash
TEST_MODE=demo python3 tests/run_tests.py
```

Production (guarded):
```bash
TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py
```

## Sponsorship and authorship
Sponsored by:
CloudForgeLabs  
https://cloudforgelabs.ainextstudios.com/  
support@ainextstudios.com

Built by:
Freddy D. Alvarez  
https://www.linkedin.com/in/freddy-daniel-alvarez/

For job opportunities, contact:
it.freddy.alvarez@gmail.com

## License
Personal/non-commercial use is free. Commercial use requires permission (paid license).
See `LICENSE` and `COMMERCIAL_LICENSE.md` for details. For commercial licensing, contact: `it.freddy.alvarez@gmail.com`.
Note: this is a non-commercial license and is not OSI-approved; GitHub may not classify it as a standard open-source license.
