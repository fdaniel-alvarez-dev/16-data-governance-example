#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _print_err(message: str) -> None:
    sys.stderr.write(message.rstrip() + "\n")


def _run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> int:
    proc = subprocess.run(cmd, cwd=cwd, text=True, env=env)
    return proc.returncode


def _mode_from_env_or_arg(mode: str | None) -> str:
    if mode:
        return mode
    return os.environ.get("TEST_MODE", "demo")


def _validate_mode(mode: str) -> None:
    if mode not in {"demo", "production"}:
        raise SystemExit("Invalid mode. Use --mode demo|production or set TEST_MODE=demo|production.")


def run_demo() -> int:
    code = 0
    code |= _run([sys.executable, "-m", "compileall", "-q", "."], cwd=REPO_ROOT)
    for path in [
        "scripts/backup.sh",
        "scripts/restore.sh",
        "scripts/check_replication.sh",
        "scripts/apply_migrations.sh",
        "scripts/seed_demo_data.sh",
        "scripts/lifecycle_retention.sh",
    ]:
        code |= _run(["bash", "-n", path], cwd=REPO_ROOT)
    code |= _run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-q"], cwd=REPO_ROOT)
    code |= _run([sys.executable, "pipelines/storage_audit.py", "--mode", "demo"], cwd=REPO_ROOT)
    return code


def _docker_available() -> bool:
    return subprocess.run(["docker", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def _docker_compose_available() -> bool:
    return subprocess.run(["docker", "compose", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def run_production() -> int:
    if os.environ.get("PRODUCTION_TESTS_CONFIRM") != "1":
        _print_err(
            "Production-mode tests are guarded.\n"
            "Set PRODUCTION_TESTS_CONFIRM=1 to confirm you intend to run real Docker-based integration checks.\n"
            "Example:\n"
            "  TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py\n"
        )
        return 2

    if not _docker_available():
        _print_err(
            "Docker is not available (or the daemon is not running).\n"
            "Start Docker Desktop / docker daemon, then rerun:\n"
            "  TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py\n"
        )
        return 2

    if not _docker_compose_available():
        _print_err(
            "Docker Compose is not available (missing `docker compose`).\n"
            "Install Docker Compose v2, then rerun:\n"
            "  TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py\n"
        )
        return 2

    env = dict(os.environ)
    env.setdefault("COMPOSE_PROJECT_NAME", "repo16_prodtests")

    try:
        code = 0
        code |= _run(["docker", "compose", "up", "-d", "--build"], cwd=REPO_ROOT, env=env)
        if code != 0:
            return code

        code |= _run(["bash", "scripts/apply_migrations.sh"], cwd=REPO_ROOT, env=env)
        code |= _run(["bash", "scripts/seed_demo_data.sh"], cwd=REPO_ROOT, env=env)
        code |= _run(["bash", "scripts/check_replication.sh"], cwd=REPO_ROOT, env=env)
        code |= _run(["bash", "scripts/lifecycle_retention.sh"], cwd=REPO_ROOT, env=env)
        code |= _run(["python3", "pipelines/storage_audit.py", "--mode", "production"], cwd=REPO_ROOT, env={**env, "PRODUCTION_AUDIT_CONFIRM": "1"})
        code |= _run(["bash", "scripts/backup.sh"], cwd=REPO_ROOT, env=env)
        code |= _run(["bash", "scripts/restore.sh"], cwd=REPO_ROOT, env=env)
        return code
    finally:
        _run(["docker", "compose", "down", "-v"], cwd=REPO_ROOT, env=env)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run repository tests in demo or production mode.")
    parser.add_argument("--mode", choices=["demo", "production"], help="Execution mode.")
    args = parser.parse_args(argv)

    mode = _mode_from_env_or_arg(args.mode)
    _validate_mode(mode)

    if mode == "demo":
        return run_demo()
    return run_production()


if __name__ == "__main__":
    raise SystemExit(main())
