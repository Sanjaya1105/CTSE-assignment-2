"""Entry point for the Multi-Agent Task Automation Assistant."""

import os
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.graph import build_graph
from app.tools.file_tools import read_text, save_text
from app.utils.logger import write_jsonl


def get_ollama_base_url() -> str:
    """Return the Ollama base URL used by the workflow."""
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def ensure_ollama_available(timeout: float = 2.0) -> str:
    """Fail fast when the local Ollama server is not reachable."""
    base_url = get_ollama_base_url().rstrip("/")
    health_url = f"{base_url}/api/tags"

    try:
        with urlopen(health_url, timeout=timeout):
            pass
    except (URLError, OSError) as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {base_url}. Start Ollama and ensure the phi3 model is installed."
        ) from exc

    return base_url


def run(user_input: str) -> dict:
    """Run the full workflow for user input and persist outputs."""
    ensure_ollama_available()
    workflow = build_graph()
    initial_state = {
        "user_input": user_input,
        "plan": "",
        "steps": "",
        "final_output": "",
        "review": "",
        "status": "new",
        "logs": [],
        "revision_count": 0,
    }
    result = workflow.invoke(initial_state)
    save_text(result["final_output"], "outputs/result.txt")
    write_jsonl(result["logs"], "outputs/logs.jsonl")
    return result


def get_user_task() -> str:
    """Read an assignment task from typed input or a local text file."""
    print("Choose input method:")
    print("1. Type assignment task")
    print("2. Load assignment task from local text file")
    choice = input("Enter choice (1/2): ").strip()

    if choice == "2":
        file_path = input("Enter text file path: ").strip().strip('"')
        if not file_path:
            return ""
        return read_text(file_path).strip()

    return input("Enter your task: ").strip()


def main() -> None:
    """Run from terminal until the user chooses to exit."""
    is_first_run = True

    while True:
        try:
            user_input = get_user_task()
        except OSError as exc:
            print(f"Could not read input file: {exc}")
            continue

        if not user_input:
            print("Please provide a non-empty task.")
        else:
            print("Running workflow with Ollama model 'phi3'...")
            if is_first_run:
                print("This can take 30-120 seconds on CPU for the first run.\n")
            else:
                print("This can still take some time because all agents use the local model.\n")

            try:
                result = run(user_input)
            except RuntimeError as exc:
                print(f"Execution failed: {exc}")
                print(
                    "If you just restarted the laptop, start Ollama again, then retry the plan."
                )
            except Exception as exc:  # pragma: no cover - runtime guard
                print(f"Execution failed: {exc}")
                print(
                    "Check that Ollama is running and reachable at "
                    "http://localhost:11434 (or set OLLAMA_BASE_URL)."
                )
            else:
                print("\n=== FINAL OUTPUT ===\n")
                print(result["final_output"])
                print("\n=== REVIEW ===\n")
                print(result["review"])
                print(f"\nStatus: {result['status']}")
                print("Saved output to outputs/result.txt")
                print("Saved logs to outputs/logs.jsonl")
            finally:
                is_first_run = False

        again = input("\nCreate another plan? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print("Goodbye.")
            return


if __name__ == "__main__":
    main()
