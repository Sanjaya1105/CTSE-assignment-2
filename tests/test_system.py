"""System-level tests for the LangGraph workflow."""

from io import BytesIO
from types import SimpleNamespace

from app.graph import build_graph
from app.main import ensure_ollama_available, get_user_task


class SequenceLLM:
    """Fake LLM that returns predefined outputs in order."""

    def __init__(self, outputs: list[str]):
        self.outputs = outputs

    def invoke(self, _prompt: str):
        return SimpleNamespace(content=self.outputs.pop(0))


def test_workflow_happy_path():
    """Graph should run coordinator->planner->executor->reviewer and stop when approved."""
    llm = SequenceLLM(
        [
            "High-level plan",
            "1. Step one\n2. Step two",
            "Title: Done\nSummary: Complete\nAction Items:\n- Item",
            "APPROVED: Clear and complete",
        ]
    )
    app = build_graph(llm=llm)
    state = {
        "user_input": "Prepare a launch checklist",
        "plan": "",
        "steps": "",
        "final_output": "",
        "review": "",
        "status": "new",
        "logs": [],
        "revision_count": 0,
    }
    result = app.invoke(state)
    assert result["status"] == "approved"
    assert result["plan"] == "High-level plan"
    assert result["steps"].startswith("1.")
    assert result["review"].startswith("APPROVED:")
    assert len(result["logs"]) >= 8


def test_workflow_revision_loop():
    """Graph should rerun executor after revision request."""
    llm = SequenceLLM(
        [
            "Plan",
            "1. Draft",
            "Title: First\nSummary: Short\nAction Items:\n- TBD",
            "REVISE: Make summary clearer",
            "Title: Second\nSummary: Better\nAction Items:\n- Done",
            "APPROVED: Improved",
        ]
    )
    app = build_graph(llm=llm)
    state = {
        "user_input": "Write quick notes",
        "plan": "",
        "steps": "",
        "final_output": "",
        "review": "",
        "status": "new",
        "logs": [],
        "revision_count": 0,
    }
    result = app.invoke(state)
    assert result["status"] == "approved"
    assert result["final_output"].startswith("Title: Second")
    assert result["revision_count"] == 1


def test_get_user_task_from_typed_input(monkeypatch):
    """CLI input helper should return manually typed assignment tasks."""
    answers = iter(["1", "Create assignment plan"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    assert get_user_task() == "Create assignment plan"


def test_get_user_task_from_local_file(monkeypatch):
    """CLI input helper should load assignment tasks from a local text file."""
    file_path = "outputs/test_assignment_input.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("Create report and demo plan")

    answers = iter(["2", file_path])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    assert get_user_task() == "Create report and demo plan"


def test_ensure_ollama_available_uses_health_endpoint(monkeypatch):
    """Ollama readiness check should probe the local health endpoint."""
    captured = {}

    def fake_urlopen(url, timeout):
        captured["url"] = url
        captured["timeout"] = timeout
        return BytesIO(b"{}")

    monkeypatch.setattr("app.main.urlopen", fake_urlopen)

    assert ensure_ollama_available(timeout=1.5) == "http://localhost:11434"
    assert captured["url"] == "http://localhost:11434/api/tags"
    assert captured["timeout"] == 1.5


def test_ensure_ollama_available_raises_clear_error(monkeypatch):
    """Ollama readiness check should fail with a helpful message when offline."""

    def fake_urlopen(_url, timeout=None):
        raise OSError("connection refused")

    monkeypatch.setattr("app.main.urlopen", fake_urlopen)

    try:
        ensure_ollama_available(timeout=0.1)
    except RuntimeError as exc:
        assert "Could not reach Ollama" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError when Ollama is unreachable")
