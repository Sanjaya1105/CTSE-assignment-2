from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1] / "utils" / "data"


def read_planning_guidelines() -> str:
    """Read local planning guidelines from a text file."""
    file_path = BASE_DIR / "planning_guidelines.txt"

    if not file_path.exists():
        return "No planning guidelines found."

    return file_path.read_text(encoding="utf-8")
