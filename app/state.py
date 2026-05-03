"""Shared graph state types for the multi-agent workflow."""

from typing import List, TypedDict
from typing_extensions import NotRequired


class AssistantState(TypedDict):
    """State passed between LangGraph nodes."""

    user_input: str
    plan: str
    steps: str
    final_output: str
    review: str
    status: str
    logs: List[dict]
    revision_count: NotRequired[int]
