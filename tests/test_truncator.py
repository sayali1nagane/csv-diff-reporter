"""Tests for csv_diff_reporter.truncator."""
from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.truncator import (
    TruncateResult,
    format_truncation_notice,
    truncate_diff,
)


def _row(key: str, change: str = "added") -> RowDiff:
    return RowDiff(
        key=key,
        change_type=change,
        old_row={},
        new_row={"id": key},
        changed_fields=[],
    )


def _result(*keys: str) -> DiffResult:
    return DiffResult(rows=[_row(k) for k in keys], headers=["id"])


# ---------------------------------------------------------------------------
# truncate_diff
# ---------------------------------------------------------------------------

def test_truncate_no_limit_returns_all():
    result = _result("a", "b", "c")
    tr = truncate_diff(result, limit=None)
    assert len(tr.diff.rows) == 3
    assert tr.truncated is False
    assert tr.dropped == 0


def test_truncate_limit_equal_to_count_no_truncation():
    result = _result("a", "b", "c")
    tr = truncate_diff(result, limit=3)
    assert len(tr.diff.rows) == 3
    assert tr.truncated is False


def test_truncate_limit_greater_than_count_no_truncation():
    result = _result("a", "b")
    tr = truncate_diff(result, limit=10)
    assert len(tr.diff.rows) == 2
    assert tr.truncated is False


def test_truncate_limit_less_than_count():
    result = _result("a", "b", "c", "d", "e")
    tr = truncate_diff(result, limit=3)
    assert len(tr.diff.rows) == 3
    assert tr.truncated is True
    assert tr.dropped == 2
    assert tr.original_count == 5


def test_truncate_preserves_order():
    result = _result("x", "y", "z")
    tr = truncate_diff(result, limit=2)
    assert [r.key for r in tr.diff.rows] == ["x", "y"]


def test_truncate_preserves_headers():
    result = DiffResult(rows=[_row("a")], headers=["id", "name"])
    tr = truncate_diff(result, limit=1)
    assert tr.diff.headers == ["id", "name"]


def test_truncate_empty_result():
    result = _result()
    tr = truncate_diff(result, limit=5)
    assert tr.truncated is False
    assert tr.dropped == 0


def test_truncate_limit_zero():
    result = _result("a", "b")
    tr = truncate_diff(result, limit=0)
    assert len(tr.diff.rows) == 0
    assert tr.truncated is True
    assert tr.dropped == 2


def test_truncate_negative_limit_raises():
    """A negative limit is invalid and should raise a ValueError."""
    result = _result("a", "b")
    with pytest.raises(ValueError, match="limit"):
        truncate_diff(result, limit=-1)


# ---------------------------------------------------------------------------
# format_truncation_notice
# ---------------------------------------------------------------------------

def test_format_notice_not_truncated_returns_empty():
    result = _result("a")
    tr = truncate_diff(result, limit=None)
    assert format_truncation_notice(tr) == ""


def test_format_notice_truncated_contains_counts():
    result = _result("a", "b", "c", "d")
    tr = truncate_diff(result, limit=2)
    notice = format_truncation_notice(tr)
    assert "2" in notice
    assert "4" in notice
    assert "2" in notice  # dropped count also 2
    assert "Truncated"
