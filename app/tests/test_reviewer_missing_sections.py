"""Tests for Reviewer Agent missing-section revision path."""

from app.agents.reviewer import run_reviewer


class FakeLLM:
    """Fake LLM. It should not be called when required sections are missing."""

    def invoke(self, prompt: str):
        raise AssertionError("LLM should not be called when required sections are missing.")


def test_reviewer_requests_revision_when_summary_is_missing() -> None:
    """Reviewer should request revision if final output misses Summary section."""
    state = {
        "user_input": "Create an assignment plan with research, coding, testing, report, demo, and submission.",
        "final_output": (
            "Title: Assignment Plan\n"
            "Action Items:\n"
            "- Complete research\n"
            "- Do coding\n"
            "- Add testing\n"
            "- Prepare report\n"
            "- Do demo\n"
            "- Submit work"
        ),
        "review": "",
        "status": "executed",
        "logs": [],
    }

    result = run_reviewer(state, FakeLLM())

    assert result["status"] == "revision_requested"
    assert result["review"].startswith("REVISE:")
    assert "missing required sections" in result["review"].lower()