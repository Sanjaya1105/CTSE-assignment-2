import sqlite3
from pathlib import Path
from typing import Iterable

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "app" / "utils" / "data" / "safety_rules.db"

DEFAULT_UNSAFE_KEYWORDS = [
    "hack",
    "create malware",
    "build malware",
    "write malware",
    "malware payload",
    "steal password",
    "phishing",
    "keylogger",
]


def setup_safety_database(keywords: Iterable[str] = DEFAULT_UNSAFE_KEYWORDS) -> None:
    """Create the safety rules database and insert default unsafe keywords."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS unsafe_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL UNIQUE
            )
            """
        )

        cursor.executemany(
            """
            INSERT OR IGNORE INTO unsafe_keywords (keyword)
            VALUES (?)
            """,
            [(keyword.strip().lower(),) for keyword in keywords if keyword.strip()],
        )

        connection.commit()


if __name__ == "__main__":
    setup_safety_database()
    print(f"Safety database created successfully at: {DB_PATH}")