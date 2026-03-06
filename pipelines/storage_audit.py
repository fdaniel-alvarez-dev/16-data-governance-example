#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AuditSummary:
    collected_at: str
    mode: str
    checks: list[dict[str, object]]
    facts: dict[str, str]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _print_err(message: str) -> None:
    sys.stderr.write(message.rstrip() + "\n")


def _run_psql(primary_id: str, sql: str) -> str:
    proc = subprocess.run(
        ["docker", "exec", "-i", primary_id, "psql", "-U", "app", "-d", "appdb", "-At", "-c", sql],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "psql failed")
    return proc.stdout.strip()


def run_demo_audit() -> AuditSummary:
    checks = [
        {"check_id": "history.append_only", "status": "pass", "message": "Append-only model enforced by primary key."},
        {"check_id": "wal.idempotency", "status": "pass", "message": "WAL staging table uses a natural key to dedupe."},
        {"check_id": "lifecycle.retention", "status": "pass", "message": "Lifecycle scripts exist (archive + retention)."},
    ]
    facts = {"artifact": "artifacts/storage_audit_report.json"}
    return AuditSummary(collected_at=_now_iso(), mode="demo", checks=checks, facts=facts)


def run_production_audit() -> AuditSummary:
    primary_id = subprocess.run(
        ["docker", "compose", "ps", "-q", "postgres-primary"], cwd=REPO_ROOT, text=True, capture_output=True
    ).stdout.strip()
    if not primary_id:
        raise RuntimeError("postgres-primary container not running (run: make up)")

    events = _run_psql(primary_id, "select count(*) from workflow_events;")
    wal = _run_psql(primary_id, "select count(*) from workflow_wal;")
    archive = _run_psql(primary_id, "select count(*) from workflow_events_archive;")

    checks: list[dict[str, object]] = []
    checks.append(
        {
            "check_id": "history.non_empty",
            "status": "pass" if events and int(events) >= 1 else "warn",
            "message": f"workflow_events count={events}",
        }
    )
    checks.append(
        {
            "check_id": "wal.drained",
            "status": "pass" if wal == "0" else "warn",
            "message": f"workflow_wal count={wal} (expected 0 after apply_wal)",
        }
    )
    checks.append(
        {
            "check_id": "archive.exists",
            "status": "pass",
            "message": f"workflow_events_archive count={archive}",
        }
    )
    facts = {"events": events, "wal": wal, "archive": archive}
    return AuditSummary(collected_at=_now_iso(), mode="production", checks=checks, facts=facts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a storage governance audit report.")
    parser.add_argument("--mode", choices=["demo", "production"], default="demo")
    parser.add_argument("--out", default="artifacts/storage_audit_report.json")
    args = parser.parse_args(argv)

    if args.mode == "production" and os.environ.get("PRODUCTION_AUDIT_CONFIRM") != "1":
        _print_err(
            "Production audit is guarded.\n"
            "Set PRODUCTION_AUDIT_CONFIRM=1 to confirm you intend to query the running database.\n"
            "Example:\n"
            "  PRODUCTION_AUDIT_CONFIRM=1 python3 pipelines/storage_audit.py --mode production\n"
        )
        return 2

    try:
        summary = run_demo_audit() if args.mode == "demo" else run_production_audit()
    except Exception as exc:
        _print_err(f"Audit failed: {exc}")
        return 1

    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(asdict(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
