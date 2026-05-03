# app/tools/output_file_tool.py

from pathlib import Path
from datetime import datetime


OUTPUT_DIR = Path("outputs").resolve()


def save_final_output(content: str) -> str:
    """Save the final agent output to a timestamped local file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = OUTPUT_DIR / f"final_output_{timestamp}.md"

    file_path.write_text(content, encoding="utf-8")

    return str(file_path)