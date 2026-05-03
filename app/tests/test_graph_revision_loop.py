"""Test full LangGraph revision loop when executor output is wrong."""

from app.graph import build_graph


class FakeResponse:
    """Fake LLM response object."""

    def __init__(self, content: str) -> None:
        self.content = content


class FakeLLM:
    """Fake LLM that makes Executor fail first, then succeed after feedback."""

    def invoke(self, prompt: str) -> FakeResponse:
        if "Coordinator Agent" in prompt:
            return FakeResponse("Create a high-level plan for completing the assignment.")

        if "Planner Agent" in prompt:
            return FakeResponse(
                "1. Research the assignment topic.\n"
                "2. Implement the required solution.\n"
                "3. Test the solution.\n"
                "4. Prepare report and demo.\n"
                "5. Submit the final work."
            )

        # First executor attempt: WRONG output, missing Title/Summary/Action Items
        if "Executor Agent" in prompt and "Incorporate this reviewer feedback" not in prompt:
            return FakeResponse("This is a bad incomplete answer.")

        # Second executor attempt: CORRECT output after reviewer feedback
        if "Executor Agent" in prompt and "Incorporate this reviewer feedback" in prompt:
            return FakeResponse(
                "Title: Assignment Completion Plan\n"
                "Summary: This plan helps the student complete the assignment step by step. "
                "It includes research, coding, testing, report preparation, demo, and submission.\n"
                "Action Items:\n"
                "- Complete research and literature review.\n"
                "- Develop the coding implementation.\n"
                "- Perform testing and validation.\n"
                "- Prepare the report and demo presentation.\n"
                "- Submit the final assignment."
            )

        if "Reviewer Agent" in prompt:
            return FakeResponse("APPROVED: Output is complete and properly formatted.")

        return FakeResponse("Default response")


def test_executor_reruns_after_reviewer_rejects_bad_output() -> None:
    """Full workflow should rerun executor when reviewer requests revision."""
    app = build_graph(llm=FakeLLM())

    initial_state = {
        "user_input": "Create an assignment plan with research, coding, testing, report, demo, and submission.",
        "plan": "",
        "steps": "",
        "final_output": "",
        "review": "",
        "status": "started",
        "revision_count": 0,
        "logs": [],
        "output_path": "",
    }

    result = app.invoke(initial_state)

    assert result["revision_count"] == 1
    assert result["status"] == "approved"
    assert "Title:" in result["final_output"]
    assert "Summary:" in result["final_output"]
    assert "Action Items:" in result["final_output"]