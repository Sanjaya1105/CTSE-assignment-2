# Student Assignment Planning Multi-Agent System

This project is a locally hosted Multi-Agent System that helps students convert an assignment or academic task into a structured action plan. The system uses four agents to understand the task, create step-by-step actions, generate a final assignment plan, review the result, and save the output locally.

The system runs fully on a local machine using Ollama with the `phi3` model and LangGraph for agent orchestration.

## Problem Domain

The problem domain is Education / Student Productivity.

Students often receive large assignment descriptions and struggle to convert them into clear tasks, deadlines, and action items. This system automates that process using a local multi-agent workflow.

The user enters an assignment task. The Coordinator checks whether the request is safe and creates a high-level plan. The Planner converts the plan into ordered steps. The Executor creates the final assignment action plan. The Reviewer checks the output and requests revision if required.

The assignment task can be typed directly in the terminal or loaded through the UI from a local `.txt` file.

## Workflow

`Coordinator -> Planner -> Executor -> Reviewer`

The reviewer can request revisions, and the executor will retry (up to 2 times).

```text
User assignment task
  |
  v
Coordinator Agent
  |
  v
Planner Agent
  |
  v
Executor Agent
  |
  v
Reviewer Agent
  |
  v
Final plan + JSONL logs
```

## Agent Roles

| Agent | Responsibility |
|---|---|
| Coordinator Agent | Checks the user request against the local safety database and creates a high-level assignment plan. |
| Planner Agent | Converts the high-level plan into ordered steps using local planning guidelines. |
| Executor Agent | Generates the final assignment action plan and saves it to a local output file. |
| Reviewer Agent | Checks the final output for required sections and asks for revisions when needed. |

## Custom Tools

| Tool | Purpose |
|---|---|
| `safety_db_tool.py` | Reads unsafe keywords from a local SQLite database and validates user input. |
| `planner_file_tool.py` | Reads local planning guidelines from `app/utils/data/planning_guidelines.txt`. |
| `output_file_tool.py` | Saves the final generated plan as a timestamped Markdown file. |
| `review_tools.py` | Checks whether the final output contains required sections. |
| `file_tools.py` | Reads local assignment text files and writes output files. |
| `time_tools.py` | Creates timestamps for observability logs. |

## State Management and Observability

The system uses `AssistantState` as the global state shared between agents. It stores the user input, generated plan, execution steps, final output, review result, status, revision count, and in-memory logs.

Each agent records its input, tool calls, and output. At the end of execution, logs are written to `outputs/logs.jsonl`.

## Assignment Requirement Mapping

| Assignment Requirement | Project Implementation |
|---|---|
| 3-4 agents | Four agents are implemented: Coordinator, Planner, Executor, and Reviewer. |
| Local LLM | The system uses Ollama with the local `phi3` model through `langchain-ollama`. |
| Orchestrator | LangGraph manages the agent workflow and routing. |
| Custom tools | The agents use custom Python tools for SQLite safety checking, reading planning guidelines, saving output files, validating required sections, and timestamp logging. |
| State management | `AssistantState` is used as the shared state passed between LangGraph nodes. |
| Observability | Agent inputs, tool calls, outputs, and timestamps are stored in JSONL logs. |
| Testing and evaluation | `pytest` tests validate individual agents, tools, and the full workflow including the revision loop. |

## Project Structure

```text
app/
  state.py
  graph.py
  agents/
    coordinator.py
    planner.py
    executor.py
    reviewer.py
  tools/
    file_tools.py
    time_tools.py
  utils/
    logger.py
main.py
tests/
  test_tools.py
  test_agents.py
  test_system.py
outputs/
README.md
```

## Requirements

- Python 3.10+
- Ollama installed and running locally
- `phi3` model available in Ollama

Install model if needed:

```bash
ollama pull phi3
```

## Setup

```bash
pip install -U langgraph langchain-ollama pytest typing-extensions
```

## Run

### Command Line

```bash
python main.py
```

The app will ask for an input method:

```text
Choose input method:
1. Type assignment task
2. Load assignment task from local text file
```

For file input, create a `.txt` file containing the assignment task and enter its path when prompted.

### Streamlit UI

```bash
streamlit run app/ui.py
```

The local UI supports typed assignment tasks and `.txt` file upload. It displays the final output, reviewer result, workflow status, and agent logs.

Windows note: if `ollama` is not recognized in terminal, run it directly:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" list
```

If needed, start the server:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" serve
```

Output files:

- `outputs/result.txt`
- `outputs/logs.jsonl`

## Test

```bash
python -m pytest -q
```
