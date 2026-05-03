"""Simple JSONL logger for agent events."""

import json
from pathlib import Path
from typing import Any, Dict

from app.tools.time_tools import get_timestamp


def make_log_entry(agent: str, phase: str, payload: str) -> Dict[str, Any]:
    """Create a log entry dictionary."""
    return {
        "timestamp": get_timestamp(),
        "agent": agent,
        "phase": phase,
        "payload": payload,
    }


def append_log(state: Dict[str, Any], agent: str, phase: str, payload: str) -> None:
    """Append a log entry to in-memory state."""
    state.setdefault("logs", []).append(make_log_entry(agent, phase, payload))


def write_jsonl(logs: list[dict], path: str) -> str:
    """Persist logs to a JSONL file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as file:
        for entry in logs:
            file.write(json.dumps(entry, ensure_ascii=True) + "\n")
    return f"Wrote {len(logs)} logs to {target}"
