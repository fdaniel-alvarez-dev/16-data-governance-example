import unittest
from pathlib import Path


class TestDemoContract(unittest.TestCase):
    def test_compose_file_contains_expected_services(self) -> None:
        text = Path("docker-compose.yml").read_text(encoding="utf-8")
        for needle in ["postgres-primary:", "postgres-replica:", "pgbouncer:"]:
            self.assertIn(needle, text)

    def test_migrations_exist(self) -> None:
        self.assertTrue(Path("migrations/001_init.sql").exists())

    def test_restore_is_isolated_verify_db(self) -> None:
        text = Path("scripts/restore.sh").read_text(encoding="utf-8")
        self.assertIn("appdb_verify", text)
        self.assertIn("drop database if exists", text)
        self.assertIn("create database", text)


if __name__ == "__main__":
    unittest.main()
