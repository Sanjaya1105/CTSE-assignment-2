"""Unit tests for utility tools."""

import re
from pathlib import Path

from app.tools.planner_file_tool import read_planning_guidelines
from app.tools.review_tools import find_missing_requested_topics, has_required_sections
from app.tools.file_tools import read_text, save_text
from app.tools.time_tools import get_timestamp


def test_save_and_read_text():
    """save_text and read_text should round-trip file contents."""
    target = Path("outputs") / "test_sample.txt"
    message = save_text("hello", str(target))
    assert "Saved text" in message
    assert read_text(str(target)) == "hello"


def test_get_timestamp_is_iso8601():
    """Timestamp tool should return a UTC ISO timestamp string."""
    ts = get_timestamp()
    assert re.match(r"^\d{4}-\d{2}-\d{2}T", ts)
    assert ts.endswith("+00:00")


def test_read_planning_guidelines_loads_local_rules():
    """Planner guideline tool should load the local guideline file."""
    guidelines = read_planning_guidelines()
    assert "Plans should be practical" in guidelines
    assert "Keep plans between 3 and 6 steps" in guidelines


def test_has_required_sections_validates_report_format():
    """Review tool should require all final output sections."""
    required = ["Title:", "Summary:", "Action Items:"]
    valid_output = "Title: Plan\nSummary: Ready\nAction Items:\n- Research"
    invalid_output = "Title: Plan\nSummary: Ready"

    assert has_required_sections(valid_output, required)
    assert not has_required_sections(invalid_output, required)



