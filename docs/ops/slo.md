# SLOs and error budgets (practical template)

This document turns reliability goals into measurable targets.

## Service context
- What are we protecting? A customer-visible API / data pipeline / database.
- Top pains this repo targets:
  1) Keeping production stable while the system scales—reducing incident frequency, improving MTTR, and building predictable operations (SLOs/runbooks/on-call hygiene).
  2) Making databases boring again—high availability, predictable performance, safe backups, and zero/low-downtime migrations with solid tooling and runbooks.
  3) Building a data platform people trust—reliable pipelines, clear ownership, data quality checks, and governance that scales without slowing delivery.

## Suggested SLIs (examples)
- Availability: successful requests / total requests
- Latency: p95 / p99 per endpoint or per pipeline step
- Correctness: data validation pass rate (data roles)
- Recovery: time-to-restore from backup (database roles)

## Suggested SLOs (start conservative, iterate)
- Availability: 99.9% monthly
- Latency: p95 < 250ms for critical endpoints
- Recovery: restore drill succeeds in < 30 minutes

## Error budget policy
- If error budget burn is high, freeze risky changes, focus on stability.
- If stable, ship improvements with stronger automation.
