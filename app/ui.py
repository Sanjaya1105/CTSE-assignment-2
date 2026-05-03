"""Streamlit UI for the Student Assignment Planning MAS."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import streamlit as st

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import run


def format_logs(logs: list[dict[str, Any]]) -> str:
    """Convert agent logs into readable JSON text for the UI."""
    return "\n".join(json.dumps(entry, ensure_ascii=True) for entry in logs)


st.set_page_config(
    page_title="Student Assignment Planning MAS",
    layout="wide",
)

st.title("Student Assignment Planning MAS")
st.caption("Local multi-agent assignment planner powered by Ollama and LangGraph.")

with st.sidebar:
    st.header("Input")
    input_method = st.radio(
        "Choose input method",
        ["Type assignment task", "Upload text file"],
    )
    st.info("Make sure Ollama is running and the phi3 model is installed.")

user_input = ""

if input_method == "Type assignment task":
    user_input = st.text_area(
        "Assignment task",
        height=180,
        placeholder=(
            "Create a study and submission plan for my machine learning assignment. "
            "Include research, coding, testing, report writing, and demo preparation."
        ),
    )
else:
    uploaded_file = st.file_uploader("Upload assignment text file", type=["txt"])
    if uploaded_file is not None:
        user_input = uploaded_file.read().decode("utf-8")
        st.text_area("Loaded assignment task", user_input, height=180, disabled=True)

run_button = st.button("Generate Plan", type="primary")

if run_button:
    if not user_input.strip():
        st.error("Please enter or upload an assignment task.")
    else:
        with st.spinner("Running Coordinator, Planner, Executor, and Reviewer agents..."):
            try:
                result = run(user_input.strip())
            except Exception as exc:  # pragma: no cover - UI runtime guard
                st.error(f"Execution failed: {exc}")
                st.stop()

        final_output = result.get("final_output", "")
        review = result.get("review", "")
        status = result.get("status", "unknown")
        logs = result.get("logs", [])

        st.subheader("Final Output")
        st.text_area("Generated assignment plan", final_output, height=320)

        left, right = st.columns(2)
        with left:
            st.subheader("Review")
            st.write(review)
        with right:
            st.subheader("Status")
            if status == "approved":
                st.success(status)
            elif status == "rejected":
                st.error(status)
            else:
                st.warning(status)

        with st.expander("Agent Logs"):
            st.code(format_logs(logs), language="json")

        st.info("Saved output to outputs/result.txt and logs to outputs/logs.jsonl.")
