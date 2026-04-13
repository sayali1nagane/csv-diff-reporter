"""Tests for column_stats_formatter.format_enriched_report."""
from __future__ import annotations

import json
import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.column_stats_reporter import build_enriched_report
from csv_diff_reporter.column_stats_formatter import format_enriched_report


def _modified(key: str, old: dict, new: dict) -> RowDiff:
    return RowDiff(key=key, change_type="modified", old_row=old, new_row=new)


def _make_result(*rows: RowDiff) -> DiffResult:
    return DiffResult(rows=list(rows), headers=["id", "name", "score"])


def _report(*rows: RowDiff):
    return build_enriched_report(_make_result(*rows))


def test_format_text_empty_diff():
    output = format_enriched_report(_report(), fmt="text")
    # empty diff may produce empty or whitespace-only string — just ensure no exception
    assert isinstance(output, str)


def test_format_text_contains_stats_header_when_changes_present():
    row = _modified("1", {"id": "1", "name": "A", "score": "1"}, {"id": "1", "name": "B", "score": "9"})
    output = format_enriched_report(_report(row), fmt="text")
    assert "Column Statistics" in output


def test_format_text_contains_most_changed_column():
    r1 = _modified("1", {"id": "1", "name": "A", "score": "1"}, {"id": "1", "name": "A", "score": "9"})
    r2 = _modified("2", {"id": "2", "name": "C", "score": "3"}, {"id": "2", "name": "C", "score": "4"})
    output = format_enriched_report(_report(r1, r2), fmt="text")
    assert "Most changed column: score" in output


def test_format_json_returns_valid_json():
    row = _modified("1", {"id": "1", "name": "A", "score": "1"}, {"id": "1", "name": "B", "score": "9"})
    output = format_enriched_report(_report(row), fmt="json")
    parsed = json.loads(output)
    assert "stats" in parsed
    assert "most_changed_column" in parsed


def test_format_json_empty_diff():
    output = format_enriched_report(_report(), fmt="json")
    parsed = json.loads(output)
    assert parsed["most_changed_column"] is None


def test_format_json_filtered_columns_present():
    row = _modified("1", {"id": "1", "name": "A", "score": "1"}, {"id": "1", "name": "B", "score": "9"})
    report = build_enriched_report(_make_result(row), include_columns=["id", "name"])
    output = format_enriched_report(report, fmt="json")
    parsed = json.loads(output)
    assert parsed["filtered_columns"] == ["id", "name"]
