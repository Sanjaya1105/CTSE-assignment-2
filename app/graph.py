"""LangGraph orchestration for the multi-agent system."""

import os
from typing import Any

from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

from app.agents.coordinator import run_coordinator
from app.agents.executor import run_executor
from app.agents.planner import run_planner
from app.agents.reviewer import run_reviewer
from app.state import AssistantState

MAX_REVISIONS = 2


def build_graph(llm: Any | None = None):
    """Build and compile the multi-agent LangGraph workflow."""
    model = llm or ChatOllama(
        model="phi3",
        temperature=0,
        num_predict=256,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )
    graph = StateGraph(AssistantState)

    def coordinator_node(state: AssistantState) -> AssistantState:
        return run_coordinator(state, model)

    def planner_node(state: AssistantState) -> AssistantState:
        return run_planner(state, model)

    def executor_node(state: AssistantState) -> AssistantState:
        return run_executor(state, model)

    def reviewer_node(state: AssistantState) -> AssistantState:
        return run_reviewer(state, model)

    def reviewer_next(state: AssistantState) -> str:
        revisions = state.get("revision_count", 0)
        if state["status"] == "approved":
            return END
        if revisions >= MAX_REVISIONS:
            return END
        return "executor"

    def count_revision(state: AssistantState) -> AssistantState:
        state["revision_count"] = state.get("revision_count", 0) + 1
        return state

    def coordinator_next(state: AssistantState) -> str:
        if state["status"] == "rejected":
            return END
        return "planner"

    def executor_next(state: AssistantState) -> str:
        if state["status"] == "rejected":
            return END
        return "reviewer"

    graph.add_node("coordinator", coordinator_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("count_revision", count_revision)

    graph.add_edge(START, "coordinator")
    graph.add_conditional_edges(
        "coordinator",
        coordinator_next,
        {END: END, "planner": "planner"},
    )
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges(
        "executor",
        executor_next,
        {END: END, "reviewer": "reviewer"},
    )
    graph.add_conditional_edges(
        "reviewer",
        reviewer_next,
        {END: END, "executor": "count_revision"},
    )
    graph.add_edge("count_revision", "executor")
    return graph.compile()
