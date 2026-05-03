"""Planner agent implementation."""

from typing import Any, Dict

from app.utils.logger import append_log
from app.tools.planner_file_tool import read_planning_guidelines


def run_planner(state: Dict[str, Any], llm: Any) -> Dict[str, Any]:
    """Break the plan into concrete executable steps."""
    append_log(state, "planner", "input", state["plan"])

    # Custom tool usage: read planning rules from a local file
    guidelines = read_planning_guidelines()
    append_log(state, "planner", "tool_call", "read_planning_guidelines")

    prompt = (
        "You are the Planner Agent for a Student Assignment Planning System.\n"
        "Convert the given assignment plan into a numbered list of clear, practical student tasks.\n"
        "Include academic workflow steps such as research, development, testing, documentation, and submission when relevant.\n"
        "Use the local planning guidelines provided below.\n\n"
        f"Planning guidelines:\n{guidelines}\n\n"
        f"Plan:\n{state['plan']}"
    )

    response = llm.invoke(prompt).content.strip()
    append_log(state, "planner", "output", response)

    return {
        "steps": response,
        "status": "steps_created",
        "logs": state["logs"],
    }
