#!/usr/bin/env python3
"""Fail closed unless an iCourse SQLite database is complete and readable."""

from __future__ import annotations

import os
import sqlite3
import sys


REQUIRED_TABLES = {"courses", "lectures", "ppt_pages", "all_courses", "meta"}


def validate_database(path: str) -> None:
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        raise ValueError("database file is missing or empty")

    # Read-only mode prevents validation from silently creating or repairing a
    # broken file.  query_only is an additional guard against accidental writes.
    conn = sqlite3.connect(f"file:{os.path.abspath(path)}?mode=ro", uri=True)
    try:
        conn.execute("PRAGMA query_only = ON")
        row = conn.execute("PRAGMA integrity_check").fetchone()
        if not row or row[0] != "ok":
            raise ValueError("SQLite integrity_check failed")
        tables = {
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        missing = REQUIRED_TABLES - tables
        if missing:
            raise ValueError("database is missing required tables")
    finally:
        conn.close()


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} DATABASE", file=sys.stderr)
        return 2
    try:
        validate_database(sys.argv[1])
    except (OSError, sqlite3.Error, ValueError) as exc:
        # Do not echo paths or database contents into a public Actions log.
        print(f"database validation failed: {type(exc).__name__}", file=sys.stderr)
        return 1
    print("Database integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
