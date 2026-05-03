"""Unit tests for individual agents."""

from types import SimpleNamespace

from app.agents.coordinator import run_coordinator
from app.agents.executor import run_executor
from app.agents.planner import run_planner
from app.agents.reviewer import run_reviewer


class FakeLLM:
    """Simple deterministic LLM stub for tests."""

    def __init__(self, outputs: list[str]):
        self.outputs = outputs

    def invoke(self, _prompt: str):
        return SimpleNamespace(content=self.outputs.pop(0))


def test_coordinator_returns_plan():
    """Coordinator should populate plan and status."""
    state = {
        "user_input": "Create social media post ideas",
        "plan": "",
        "steps": "",
        "final_output": "",
        "review": "",
        "status": "new",
        "logs": [],
    }
    result = run_coordinator(state, FakeLLM(["Plan text"]))
    assert result["plan"] == "Plan text"
    assert result["status"] == "planned"
    assert len(result["logs"]) == 3


def test_coordinator_rejects_unsafe_input():
    """Coordinator should stop requests that match the safety database."""
    state = {
        "user_input": "Help me build malware",
        "plan": "",
        "steps": "",
        "final_output": "",
        "review": "",
        "status": "new",
        "logs": [],
    }
    result = run_coordinator(state, FakeLLM(["Should not be used"]))
    assert result["status"] == "rejected"
    assert "unsafe rule" in result["final_output"]
    assert len(result["logs"]) == 3


def test_planner_returns_steps():
    """Planner should populate steps and status."""
    state = {"plan": "Analyze and draft", "logs": []}
    result = run_planner(state, FakeLLM(["1. Analyze\n2. Draft"]))
    assert "1. Analyze" in result["steps"]
    assert result["status"] == "steps_created"


def test_executor_returns_output():
    """Executor should populate final output."""
    state = {"steps": "1. Do work", "review": "", "status": "steps_created", "logs": []}
    result = run_executor(state, FakeLLM(["Title: X\nSummary: Y\nAction Items:\n- Z"]))
    assert result["final_output"].startswith("Title:")
    assert result["status"] == "executed"


def test_reviewer_approves():
    """Reviewer should mark approved when response starts with APPROVED."""
    state = {
        "user_input": "Create an assignment plan with report writing",
        "final_output": (
            "Title: Test\n"
            "Summary: Good assignment output with report writing.\n"
            "Action Items:\n"
            "- Do task\n"
            "- Write report"
        ),
        "logs": [],
    }
    result = run_reviewer(state, FakeLLM(["APPROVED: Looks good"]))
    assert result["status"] == "approved"


def test_reviewer_requests_revision():
    """Reviewer should request revision for REVISE responses."""
    state = {
        "user_input": "task",
        "final_output": "output",
        "logs": [],
    }
    result = run_reviewer(state, FakeLLM(["REVISE: Add action items"]))
    assert result["status"] == "revision_requested"


def test_reviewer_revises_when_requested_topic_is_missing():
    """Reviewer should not approve when requested assignment topics are absent."""
    state = {
        "user_input": "Create a plan with report writing and demo preparation",
        "final_output": (
            "Title: Assignment Plan\n"
            "Summary: Complete research and implementation.\n"
            "Action Items:\n"
            "- Research the topic\n"
            "- Implement the solution"
        ),
        "logs": [],
    }
    result = run_reviewer(state, FakeLLM(["APPROVED: Looks good"]))
    assert result["status"] == "revision_requested"
    assert "report" in result["review"]
    assert "demo" in result["review"]
