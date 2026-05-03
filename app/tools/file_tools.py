"""File I/O tools used by agents and main runtime."""

from pathlib import Path


def save_text(content: str, path: str) -> str:
    """Save text to a file path and return a status message."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Saved text to {target}"


def read_text(path: str) -> str:
    """Read text from a file path."""
    return Path(path).read_text(encoding="utf-8")
