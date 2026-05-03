"""SQLite safety database tool for agent input validation."""

import sqlite3
from pathlib import Path
from typing import List


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "app" / "utils" / "data" / "safety_rules.db"


def get_unsafe_keywords() -> List[str]:
    """
    Read unsafe keywords from the local SQLite safety database.

    Returns:
        A list of unsafe keyword strings stored in the database.

    Raises:
        FileNotFoundError: If the safety database does not exist.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Safety database not found: {DB_PATH}. "
            "Run app/utils/setup_safety_database.py first."
        )

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT keyword FROM unsafe_keywords")
        rows = cursor.fetchall()

    return [row[0] for row in rows]


def contains_unsafe_keyword(user_input: str) -> bool:
    """
    Check whether user input contains any unsafe keyword from the SQLite database.

    Args:
        user_input: The original user request.

    Returns:
        True if an unsafe keyword is found, otherwise False.
    """
    if not user_input or not user_input.strip():
        return False

    unsafe_keywords = get_unsafe_keywords()
    normalized_input = user_input.lower()

    return any(keyword.lower() in normalized_input for keyword in unsafe_keywords)