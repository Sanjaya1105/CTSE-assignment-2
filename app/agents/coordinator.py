"""Coordinator agent implementation."""

from typing import Any, Dict

from app.tools.safety_db_tool import contains_unsafe_keyword
from app.utils.logger import append_log


def run_coordinator(state: Dict[str, Any], llm: Any) -> Dict[str, Any]:
    """Understand the user request and produce a high-level plan."""
    user_input = state["user_input"]
    append_log(state, "coordinator", "input", user_input)

    # Custom tool usage: check local SQLite safety database
    is_unsafe = contains_unsafe_keyword(user_input)
    append_log(state, "coordinator", "tool_call", f"contains_unsafe_keyword={is_unsafe}")

    # If the input contains any keyword from the SQLite safety database,
    # stop immediately.
    if is_unsafe:
        response = "Request rejected because it matches an unsafe rule from the local safety database."
        append_log(state, "coordinator", "output", response)

        return {
            "plan": response,
            "final_output": response,
            "status": "rejected",
            "logs": state["logs"],
        }

    prompt = (
        "You are the Coordinator Agent for a Student Assignment Planning System.\n"
        "Understand the student's academic task and create a concise high-level assignment plan.\n"
        "Focus on useful work stages such as research, implementation, testing, report writing, and demo preparation when relevant.\n"
        "Return 2-4 short sentences.\n\n"
        f"User request:\n{user_input}"
    )

    response = llm.invoke(prompt).content.strip()
    append_log(state, "coordinator", "output", response)

    return {
        "plan": response,
        "status": "planned",
        "logs": state["logs"],
    }
