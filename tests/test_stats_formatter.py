"""Tests for csv_diff_reporter.stats_formatter."""
import json

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.stats import compute_stats
from csv_diff_reporter.stats_formatter import format_stats


def _modified(key: str, old: dict, new: dict) -> RowDiff:
    changed = [k for k in old if old.get(k) != new.get(k)]
    return RowDiff(key=key, change_type="modified", old_row=old, new_row=new, changed_fields=changed)


def _make_result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


def test_format_stats_text_empty():
    stats = compute_stats(_make_result())
    output = format_stats(stats, output_format="text")
    assert "Rows compared" in output
    assert "No column-level changes" in output


def test_format_stats_json_empty():
    stats = compute_stats(_make_result())
    output = format_stats(stats, output_format="json")
    data = json.loads(output)
    assert data["total_rows_compared"] == 0
    assert data["columns"] == {}


def test_format_stats_json_with_data():
    row = _modified("1", {"val": "a"}, {"val": "b"})
    stats = compute_stats(_make_result(modified=[row]))
    output = format_stats(stats, output_format="json")
    data = json.loads(output)
    assert data["columns"]["val"]["changes"] == 1


def test_format_stats_markdown_contains_table_header():
    stats = compute_stats(_make_result())
    output = format_stats(stats, output_format="markdown")
    assert "| Column |" in output
    assert "| --- |" in output


def test_format_stats_markdown_with_column():
    row = _modified("1", {"price": "10"}, {"price": "20"})
    stats = compute_stats(_make_result(modified=[row]))
    output = format_stats(stats, output_format="markdown")
    assert "price" in output
    assert "| 1 |" in output


def test_format_stats_default_is_text():
    stats = compute_stats(_make_result())
    assert format_stats(stats) == format_stats(stats, output_format="text")


def test_format_stats_markdown_empty_columns():
    stats = compute_stats(_make_result())
    output = format_stats(stats, output_format="markdown")
    assert "—" in output
