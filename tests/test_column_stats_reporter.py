"""Tests for column_stats_reporter.build_enriched_report."""
from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.column_stats_reporter import build_enriched_report, EnrichedReport


def _modified(key: str, old: dict, new: dict) -> RowDiff:
    return RowDiff(key=key, change_type="modified", old_row=old, new_row=new)


def _added(key: str, row: dict) -> RowDiff:
    return RowDiff(key=key, change_type="added", old_row={}, new_row=row)


def _removed(key: str, row: dict) -> RowDiff:
    return RowDiff(key=key, change_type="removed", old_row=row, new_row={})


def _make_result(*rows: RowDiff) -> DiffResult:
    return DiffResult(rows=list(rows), headers=["id", "name", "score"])


def test_build_enriched_report_empty():
    result = _make_result()
    report = build_enriched_report(result)
    assert isinstance(report, EnrichedReport)
    assert report.stats.total_changes == 0
    assert report.highlighted_rows == []
    assert report.most_changed_column is None


def test_build_enriched_report_stats_populated():
    row = _modified("1", {"id": "1", "name": "Alice", "score": "10"}, {"id": "1", "name": "Bob", "score": "10"})
    report = build_enriched_report(_make_result(row))
    assert report.stats.total_changes == 1
    assert "name" in report.stats.by_column


def test_build_enriched_report_highlighted_rows_match_diff_rows():
    row = _added("2", {"id": "2", "name": "Carol", "score": "99"})
    result = _make_result(row)
    report = build_enriched_report(result)
    assert len(report.highlighted_rows) == len(result.rows)


def test_most_changed_column_returns_highest():
    r1 = _modified("1", {"id": "1", "name": "A", "score": "1"}, {"id": "1", "name": "B", "score": "2"})
    r2 = _modified("2", {"id": "2", "name": "C", "score": "3"}, {"id": "2", "name": "C", "score": "4"})
    report = build_enriched_report(_make_result(r1, r2))
    # name changed once, score changed twice
    assert report.most_changed_column == "score"


def test_column_stats_returns_none_for_unknown_column():
    result = _make_result()
    report = build_enriched_report(result)
    assert report.column_stats("nonexistent") is None


def test_build_enriched_report_with_include_columns():
    row = _modified("1", {"id": "1", "name": "A", "score": "1"}, {"id": "1", "name": "B", "score": "9"})
    report = build_enriched_report(_make_result(row), include_columns=["id", "name"])
    assert report.filtered_columns == ["id", "name"]


def test_build_enriched_report_with_exclude_columns():
    row = _modified("1", {"id": "1", "name": "A", "score": "1"}, {"id": "1", "name": "B", "score": "9"})
    report = build_enriched_report(_make_result(row), exclude_columns=["score"])
    assert report.filtered_columns == ["score"]
