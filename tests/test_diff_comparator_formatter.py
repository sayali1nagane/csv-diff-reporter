import json
import pytest
from csv_diff_reporter.diff_comparator import ComparisonResult
from csv_diff_reporter.diff_comparator_formatter import format_comparison


def _result(**kwargs):
    return ComparisonResult(labels={"a": "old", "b": "new"}, **kwargs)


def test_format_text_contains_labels():
    out = format_comparison(_result(), fmt="text")
    assert "old" in out
    assert "new" in out


def test_format_text_contains_change_types():
    out = format_comparison(_result(), fmt="text")
    assert "Added" in out or "added" in out.lower()
    assert "Removed" in out or "removed" in out.lower()
    assert "Modified" in out or "modified" in out.lower()\n

def test_format_text_shows_counts():
    r = _result(common_added=3, added_only_in_a=1, added_only_in_b=2)
    out = format_comparison(r, fmt="text")
    assert "3" in out
    assert "1" in out
    assert "2" in out


def test_format_json_is_valid():
    r = _result(common_modified=5)
    out = format_comparison(r, fmt="json")
    data = json.loads(out)
    assert data["common_modified"] == 5


def test_format_json_includes_labels():
    r = _result()
    out = format_comparison(r, fmt="json")
    data = json.loads(out)
    assert data["labels"]["a"] == "old"
    assert data["labels"]["b"] == "new"


def test_format_default_is_text():
    r = _result()
    out = format_comparison(r)
    assert isinstance(out, str)
    assert "Diff Comparison" in out
