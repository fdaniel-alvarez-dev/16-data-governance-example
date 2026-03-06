.PHONY: demo up down logs seed migrate lifecycle audit backup restore check test clean

.DEFAULT_GOAL := demo

demo: up migrate seed check lifecycle audit backup restore
	@echo "Demo complete. Try: make logs"

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

check:
	bash scripts/check_replication.sh

seed:
	bash scripts/seed_demo_data.sh

migrate:
	bash scripts/apply_migrations.sh

lifecycle:
	bash scripts/lifecycle_retention.sh

audit:
	python3 pipelines/storage_audit.py --mode demo

backup:
	bash scripts/backup.sh

restore:
	bash scripts/restore.sh

test:
	TEST_MODE=demo python3 tests/run_tests.py

clean:
	rm -rf artifacts
