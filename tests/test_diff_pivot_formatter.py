"""Tests for diff_pivot_formatter."""
import json

import pytest

from csv_diff_reporter.diff_pivot import PivotResult, build_pivot
from csv_diff_reporter.diff_pivot_formatter import format_pivot
from csv_diff_reporter.differ import DiffResult, RowDiff


def _row(key: str, change: str, old: dict | None = None, new: dict | None = None) -> RowDiff:
    return RowDiff(key=key, change_type=change, old_row=old or {}, new_row=new or {})


def _make_result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id", "status", "amount"], rows=list(rows))


@pytest.fixture()
def pivot_with_data() -> PivotResult:
    result = _make_result(
        _row("1", "modified", {"status": "active", "amount": "10"}, {"status": "inactive", "amount": "20"}),
        _row("2", "modified", {"status": "active", "amount": "5"}, {"status": "active", "amount": "15"}),
        _row("3", "added", {}, {"status": "new", "amount": "0"}),
    )
    return build_pivot(result)


def test_format_text_empty_pivot():
    result = _make_result()
    pivot = build_pivot(result)
    out = format_pivot(pivot)
    assert "No pivot data" in out


def test_format_text_contains_header(pivot_with_data):
    out = format_pivot(pivot_with_data)
    assert "Column Change Pivot" in out


def test_format_text_contains_column_names(pivot_with_data):
    out = format_pivot(pivot_with_data)
    assert "status" in out
    assert "amount" in out


def test_format_text_contains_change_count(pivot_with_data):
    out = format_pivot(pivot_with_data)
    assert "Total changes" in out


def test_format_json_empty_pivot():
    result = _make_result()
    pivot = build_pivot(result)
    out = format_pivot(pivot, fmt="json")
    data = json.loads(out)
    assert data == {"columns": {}}


def test_format_json_has_columns_key(pivot_with_data):
    out = format_pivot(pivot_with_data, fmt="json")
    data = json.loads(out)
    assert "columns" in data


def test_format_json_column_has_value_counts(pivot_with_data):
    out = format_pivot(pivot_with_data, fmt="json")
    data = json.loads(out)
    for col_data in data["columns"].values():
        assert "value_counts" in col_data


def test_format_unknown_fmt_defaults_to_text(pivot_with_data):
    out = format_pivot(pivot_with_data, fmt="unknown")
    assert "Column Change Pivot" in out
