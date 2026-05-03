# app/utils/view_safety_db.py

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "app" / "utils" / "data" / "safety_rules.db"


def check_database() -> None:
    """Check whether the SQLite database exists and print table data."""
    if not DB_PATH.exists():
        print(f"Database not found at: {DB_PATH}")
        return

    print(f"Database found at: {DB_PATH.resolve()}")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table';
        """
    )

    tables = cursor.fetchall()
    print("Tables:", tables)

    cursor.execute("SELECT * FROM unsafe_keywords;")
    rows = cursor.fetchall()

    print("\nUnsafe keywords:")
    for row in rows:
        print(row)

    connection.close()


if __name__ == "__main__":
    check_database()