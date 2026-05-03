# """Reviewer agent implementation."""
#
# from typing import Any, Dict
#
# from app.tools.review_tools import find_missing_requested_topics, has_required_sections
# from app.utils.logger import append_log
# from app.utils.setup_safety_db import get_assignment_topics
#
#
# def run_reviewer(state: Dict[str, Any], llm: Any) -> Dict[str, Any]:
#     """Review final output and either approve or request revision."""
#     append_log(state, "reviewer", "input", state["final_output"])
#
#     required_sections = ["Title:", "Summary:", "Action Items:"]
#     has_sections = has_required_sections(state["final_output"], required_sections)
#
#     append_log(state, "reviewer", "tool_call", f"has_required_sections={has_sections}")
#
#     required_assignment_topics = get_assignment_topics()
#
#     missing_topics = find_missing_requested_topics(
#         state["user_input"],
#         state["final_output"],
#         required_assignment_topics,
#     )
#
#     append_log(state, "reviewer", "tool_call", f"missing_requested_topics={missing_topics}")
#
#     if missing_topics:
#         topics = ", ".join(missing_topics)
#         response = f"REVISE: Final output is missing requested assignment topics: {topics}."
#         append_log(state, "reviewer", "output", response)
#
#         return {
#             "review": response,
#             "status": "revision_requested",
#             "logs": state["logs"],
#         }
#
#     prompt = (
#         "You are the Reviewer Agent for a Student Assignment Planning System.\n"
#         "Evaluate the final output for clarity, academic usefulness, completeness, and formatting.\n"
#         "Check that the plan would help a student complete the assignment in practical steps.\n"
#         "Do not approve the output while also saying important requested details are missing.\n"
#         "If it is good, respond exactly with:\n"
#         "APPROVED: <short reason>\n"
#         "If it needs changes, respond exactly with:\n"
#         "REVISE: <specific feedback>\n\n"
#         f"User input:\n{state['user_input']}\n\n"
#         f"Final output:\n{state['final_output']}"
#     )
#
#     response = llm.invoke(prompt).content.strip()
#     append_log(state, "reviewer", "output", response)
#
#     normalized = response.upper()
#     status = "approved" if normalized.startswith("APPROVED:") else "revision_requested"
#
#     return {
#         "review": response,
#         "status": status,
#         "logs": state["logs"],
#     }


"""Reviewer agent implementation."""

from typing import Any, Dict

from app.tools.review_tools import find_missing_requested_topics, has_required_sections
from app.utils.logger import append_log
from app.utils.setup_safety_db import get_assignment_topics


def run_reviewer(state: Dict[str, Any], llm: Any) -> Dict[str, Any]:
    """Review final output and either approve or request revision."""
    append_log(state, "reviewer", "input", state["final_output"])

    required_sections = ["Title:", "Summary:", "Action Items:"]
    has_sections = has_required_sections(state["final_output"], required_sections)

    append_log(state, "reviewer", "tool_call", f"has_required_sections={has_sections}")

    if not has_sections:
        response = (
            "REVISE: Final output is missing required sections. "
            "Regenerate the output using exactly this format: "
            "Title:, Summary:, Action Items:."
        )

        append_log(state, "reviewer", "output", response)

        return {
            "review": response,
            "status": "revision_requested",
            "logs": state["logs"],
        }

    required_assignment_topics = get_assignment_topics()

    missing_topics = find_missing_requested_topics(
        state["user_input"],
        state["final_output"],
        required_assignment_topics,
    )

    append_log(state, "reviewer", "tool_call", f"missing_requested_topics={missing_topics}")

    if missing_topics:
        topics = ", ".join(missing_topics)
        response = (
            f"REVISE: Final output is missing requested assignment topics: {topics}. "
            f"Regenerate the output and include these topics clearly."
        )

        append_log(state, "reviewer", "output", response)

        return {
            "review": response,
            "status": "revision_requested",
            "logs": state["logs"],
        }

    prompt = (
        "You are the Reviewer Agent for a Student Assignment Planning System.\n"
        "Evaluate the final output for clarity, academic usefulness, completeness, and formatting.\n"
        "Check that the plan would help a student complete the assignment in practical steps.\n"
        "Do not approve the output while also saying important requested details are missing.\n"
        "If it is good, respond exactly with:\n"
        "APPROVED: <short reason>\n"
        "If it needs changes, respond exactly with:\n"
        "REVISE: <specific feedback>\n\n"
        f"User input:\n{state['user_input']}\n\n"
        f"Final output:\n{state['final_output']}"
    )

    # response = llm.invoke(prompt).content.strip()
    # append_log(state, "reviewer", "output", response)
    #
    # first_line = response.splitlines()[0].strip()
    # normalized = first_line.upper()
    #
    # # if normalized.startswith("APPROVED:"):
    # #     status = "approved"
    # #     review = first_line
    # # else:
    # #     status = "revision_requested"
    # #     review = first_line if first_line.startswith("REVISE:") else "REVISE: Reviewer requested improvement."
    #
    # if normalized.startswith("APPROVED:") and "REVISE:" not in response.upper():
    #     status = "approved"
    #     review = first_line
    # else:
    #     status = "revision_requested"
    #     review = first_line if first_line.startswith("REVISE:") else "REVISE: Reviewer requested improvement."
    #
    # return {
    #     "review": review,
    #     "status": status,
    #     "logs": state["logs"],
    # }
    response = llm.invoke(prompt).content.strip()
    append_log(state, "reviewer", "output", response)

    normalized = response.upper()

    if normalized.startswith("APPROVED:") and "REVISE:" not in normalized:
        status = "approved"
        review = response
    elif normalized.startswith("REVISE:"):
        status = "revision_requested"
        review = response
    else:
        status = "revision_requested"
        review = "REVISE: Reviewer response was unclear. Please improve the final output."

    return {
        "review": review,
        "status": status,
        "logs": state["logs"],
    }