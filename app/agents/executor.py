"""Executor agent implementation."""

from typing import Any, Dict

from app.utils.logger import append_log
from app.tools.output_file_tool import save_final_output


def run_executor(state: Dict[str, Any], llm: Any) -> Dict[str, Any]:
    """Generate final formatted output from steps."""
    review_feedback = state.get("review", "").strip()

    append_log(
        state,
        "executor",
        "input",
        f"steps={state['steps']} | review_feedback={review_feedback}",
    )

    feedback_block = ""
    if state.get("status") == "revision_requested" and review_feedback:
        feedback_block = f"\nIncorporate this reviewer feedback:\n{review_feedback}\n"

    prompt = (
        "You are the Executor Agent for a Student Assignment Planning System.\n"
        "Produce the final assignment action plan in this format:\n"
        "Title: <short title>\n"
        "Summary: <2-4 lines explaining the assignment plan>\n"
        "Action Items:\n"
        "- <item>\n"
        "- <item>\n\n"
        "Use the provided steps and keep the output clear, realistic, and student-friendly."
        f"{feedback_block}\n"
        f"Steps:\n{state['steps']}"
    )

    response = llm.invoke(prompt).content.strip()
    append_log(state, "executor", "output", response)

    # Custom tool usage: save final response to local file
    output_path = save_final_output(response)
    append_log(state, "executor", "tool_call", f"save_final_output={output_path}")

    return {
        "final_output": response,
        "output_path": output_path,
        "status": "executed",
        "logs": state["logs"],
    }
