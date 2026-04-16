"""Tests for csv_diff_reporter.diff_deduplicator."""
import pytest
from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_deduplicator import (
    DeduplicateOptions,
    deduplicate_diff,
    format_deduplicate_notice,
)


def _row(key: str, change_type: str = "modified") -> RowDiff:
    return RowDiff(key=key, change_type=change_type, fields={})


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id", "name"], rows=list(rows))


def test_deduplicate_empty_result():
    result = _result()
    out = deduplicate_diff(result)
    assert out.rows == []


def test_deduplicate_no_duplicates_returns_all():
    rows = [_row("a"), _row("b"), _row("c")]
    result = _result(*rows)
    out = deduplicate_diff(result)
    assert len(out.rows) == 3


def test_deduplicate_removes_exact_duplicates():
    rows = [_row("a"), _row("a"), _row("b")]
    result = _result(*rows)
    out = deduplicate_diff(result)
    assert len(out.rows) == 2
    assert out.rows[0].key == "a"
    assert out.rows[1].key == "b"


def test_deduplicate_keep_first_is_default():
    r1 = RowDiff(key="a", change_type="modified", fields={"x": ("1", "2")})
    r2 = RowDiff(key="a", change_type="modified", fields={"x": ("3", "4")})
    result = _result(r1, r2)
    out = deduplicate_diff(result)
    assert out.rows[0].fields == {"x": ("1", "2")}


def test_deduplicate_keep_last():
    r1 = RowDiff(key="a", change_type="modified", fields={"x": ("1", "2")})
    r2 = RowDiff(key="a", change_type="modified", fields={"x": ("3", "4")})
    result = _result(r1, r2)
    opts = DeduplicateOptions(keep="last")
    out = deduplicate_diff(result, opts)
    assert out.rows[0].fields == {"x": ("3", "4")}


def test_deduplicate_different_change_types_kept_separately():
    rows = [_row("a", "added"), _row("a", "removed")]
    result = _result(*rows)
    out = deduplicate_diff(result)
    assert len(out.rows) == 2


def test_deduplicate_ignore_change_type_collapses_all():
    rows = [_row("a", "added"), _row("a", "removed")]
    result = _result(*rows)
    opts = DeduplicateOptions(ignore_change_type=True)
    out = deduplicate_diff(result, opts)
    assert len(out.rows) == 1


def test_deduplicate_preserves_headers():
    result = _result(_row("a"))
    out = deduplicate_diff(result)
    assert out.headers == ["id", "name"]


def test_format_notice_no_duplicates():
    msg = format_deduplicate_notice(5, 5)
    assert "No duplicate" in msg


def test_format_notice_with_duplicates():
    msg = format_deduplicate_notice(7, 5)
    assert "2" in msg
    assert "5" in msg
