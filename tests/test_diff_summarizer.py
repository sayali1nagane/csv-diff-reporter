import json
import pytest
from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_summarizer import (
    SummaryLine,
    build_summary_line,
    format_summary_line,
)


def _row(key: str, change_type: str) -> RowDiff:
    return RowDiff(
        key=key,
        change_type=change_type,
        old_fields={},
        new_fields={},
    )


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id"], rows=list(rows))


def test_build_summary_line_empty():
    s = build_summary_line(_result())
    assert s.added == 0
    assert s.removed == 0
    assert s.modified == 0
    assert s.unchanged == 0
    assert s.total_rows == 0


def test_build_summary_line_counts():
    result = _result(
        _row("1", "added"),
        _row("2", "removed"),
        _row("3", "modified"),
        _row("4", "unchanged"),
        _row("5", "unchanged"),
    )
    s = build_summary_line(result)
    assert s.added == 1
    assert s.removed == 1
    assert s.modified == 1
    assert s.unchanged == 2
    assert s.total_rows == 5


def test_as_dict_includes_changed_key():
    s = SummaryLine(added=2, removed=1, modified=3, unchanged=4, total_rows=10)
    d = s.as_dict()
    assert d["changed"] == 6
    assert d["total_rows"] == 10


def test_format_text_no_differences():
    s = build_summary_line(_result())
    assert format_summary_line(s) == "No differences found."


def test_format_text_only_added():
    result = _result(_row("1", "added"), _row("2", "added"))
    s = build_summary_line(result)
    text = format_summary_line(s)
    assert "2 added" in text
    assert "2 change(s)" in text


def test_format_text_mixed_changes():
    result = _result(
        _row("1", "added"),
        _row("2", "removed"),
        _row("3", "modified"),
        _row("4", "unchanged"),
    )
    s = build_summary_line(result)
    text = format_summary_line(s)
    assert "added" in text
    assert "removed" in text
    assert "modified" in text
    assert "75.0%" in text


def test_format_json_is_valid():
    result = _result(_row("1", "added"))
    s = build_summary_line(result)
    out = format_summary_line(s, fmt="json")
    data = json.loads(out)
    assert data["added"] == 1
    assert "changed" in data


def test_format_json_empty():
    s = build_summary_line(_result())
    out = format_summary_line(s, fmt="json")
    data = json.loads(out)
    assert data["changed"] == 0
