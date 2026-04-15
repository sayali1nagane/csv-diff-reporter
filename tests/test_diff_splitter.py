"""Tests for csv_diff_reporter.diff_splitter."""
from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_splitter import (
    SplitOptions,
    split_diff,
)


HEADERS = ["id", "name", "value"]


def _row(key: str, change_type: str) -> RowDiff:
    old = {"id": key, "name": "old", "value": "1"} if change_type != "added" else {}
    new = {"id": key, "name": "new", "value": "2"} if change_type != "removed" else {}
    return RowDiff(key=key, change_type=change_type, old_row=old, new_row=new)


def _result(rows: list[RowDiff]) -> DiffResult:
    return DiffResult(headers=HEADERS, rows=rows)


# ---------------------------------------------------------------------------
# No options
# ---------------------------------------------------------------------------

def test_split_no_options_returns_single_chunk():
    rows = [_row("1", "added"), _row("2", "removed")]
    result = split_diff(_result(rows))
    assert result.count == 1
    assert result.labels == ["all"]
    assert result.chunks[0].rows == rows


def test_split_empty_result_single_chunk():
    result = split_diff(_result([]))
    assert result.count == 1


# ---------------------------------------------------------------------------
# chunk_size only
# ---------------------------------------------------------------------------

def test_split_by_size_exact_multiple():
    rows = [_row(str(i), "modified") for i in range(6)]
    result = split_diff(_result(rows), SplitOptions(chunk_size=2))
    assert result.count == 3
    for chunk in result.chunks:
        assert len(chunk.rows) == 2


def test_split_by_size_remainder():
    rows = [_row(str(i), "added") for i in range(5)]
    result = split_diff(_result(rows), SplitOptions(chunk_size=2))
    assert result.count == 3
    assert len(result.chunks[-1].rows) == 1


def test_split_by_size_preserves_headers():
    rows = [_row("1", "added")]
    result = split_diff(_result(rows), SplitOptions(chunk_size=1))
    assert result.chunks[0].headers == HEADERS


def test_split_by_size_invalid_raises():
    with pytest.raises(ValueError):
        split_diff(_result([_row("1", "added")]), SplitOptions(chunk_size=0))


# ---------------------------------------------------------------------------
# by_type only
# ---------------------------------------------------------------------------

def test_split_by_type_produces_three_buckets():
    rows = [_row("a", "added"), _row("b", "removed"), _row("c", "modified")]
    result = split_diff(_result(rows), SplitOptions(by_type=True))
    assert result.count == 3
    assert set(result.labels) == {"added", "removed", "modified"}


def test_split_by_type_empty_buckets_included():
    rows = [_row("1", "added")]
    result = split_diff(_result(rows), SplitOptions(by_type=True))
    assert result.count == 3  # removed and modified buckets are empty


# ---------------------------------------------------------------------------
# by_type + chunk_size
# ---------------------------------------------------------------------------

def test_split_by_type_and_size():
    rows = [_row(str(i), "added") for i in range(4)]
    result = split_diff(_result(rows), SplitOptions(chunk_size=2, by_type=True))
    added_chunks = [c for l, c in zip(result.labels, result.chunks) if "added" in l]
    assert len(added_chunks) == 2
    for chunk in added_chunks:
        assert len(chunk.rows) == 2
