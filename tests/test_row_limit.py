"""Tests for csv_diff_reporter.row_limit."""
import pytest

from csv_diff_reporter.row_limit import (
    RowLimitOptions,
    RowLimitResult,
    apply_row_limit,
    format_row_limit_warning,
)


def _data(n: int):
    """Return a simple keyed data dict with *n* entries."""
    return {str(i): [{"id": str(i), "value": "x"}] for i in range(n)}


# ---------------------------------------------------------------------------
# apply_row_limit
# ---------------------------------------------------------------------------

def test_no_limit_returns_all_rows():
    data = _data(5)
    result = apply_row_limit(data, RowLimitOptions(max_rows=None))
    assert not result.was_limited
    assert result.limited_count == 5
    assert result.original_count == 5
    assert result.dropped == 0
    assert result.data is data


def test_limit_equal_to_count_no_truncation():
    data = _data(4)
    result = apply_row_limit(data, RowLimitOptions(max_rows=4))
    assert not result.was_limited
    assert result.limited_count == 4


def test_limit_greater_than_count_no_truncation():
    data = _data(3)
    result = apply_row_limit(data, RowLimitOptions(max_rows=10))
    assert not result.was_limited
    assert result.limited_count == 3


def test_limit_truncates_rows():
    data = _data(10)
    result = apply_row_limit(data, RowLimitOptions(max_rows=4))
    assert result.was_limited
    assert result.limited_count == 4
    assert result.original_count == 10
    assert result.dropped == 6
    assert len(result.data) == 4


def test_limit_preserves_insertion_order():
    data = {str(i): [{"id": str(i)}] for i in range(6)}
    result = apply_row_limit(data, RowLimitOptions(max_rows=3))
    assert list(result.data.keys()) == ["0", "1", "2"]


def test_limit_zero_returns_empty():
    data = _data(5)
    result = apply_row_limit(data, RowLimitOptions(max_rows=0))
    assert result.was_limited
    assert result.limited_count == 0
    assert result.data == {}


# ---------------------------------------------------------------------------
# format_row_limit_warning
# ---------------------------------------------------------------------------

def test_warning_empty_when_not_limited():
    data = _data(3)
    result = apply_row_limit(data, RowLimitOptions(max_rows=None))
    assert format_row_limit_warning(result) == ""


def test_warning_contains_counts_when_limited():
    data = _data(10)
    result = apply_row_limit(data, RowLimitOptions(max_rows=3))
    warning = format_row_limit_warning(result)
    assert "3" in warning
    assert "7" in warning
    assert "Warning" in warning
