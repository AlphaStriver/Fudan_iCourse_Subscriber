import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.validate_db import validate_database
from src.data.schema import SCHEMA_SQL


class DatabaseSafetyTests(unittest.TestCase):
    def test_accepts_complete_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "icourse.db"
            conn = sqlite3.connect(path)
            conn.executescript(SCHEMA_SQL)
            conn.close()
            validate_database(str(path))

    def test_rejects_empty_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "icourse.db"
            path.touch()
            with self.assertRaises(ValueError):
                validate_database(str(path))

    def test_rejects_non_sqlite_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "icourse.db"
            path.write_bytes(b"not a sqlite database")
            with self.assertRaises(sqlite3.Error):
                validate_database(str(path))

    def test_rejects_sqlite_with_incomplete_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "icourse.db"
            conn = sqlite3.connect(path)
            conn.execute("CREATE TABLE unrelated (id INTEGER)")
            conn.close()
            with self.assertRaises(ValueError):
                validate_database(str(path))
