"""Tests for csv_diff_reporter.sorter."""

from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.sorter import sort_diff

_HEADERS = ["id", "val"]


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(rows=list(rows), headers=_HEADERS)


_R_C = RowDiff(key="c", old=None, new={"id": "c", "val": "1"})          # added
_R_A = RowDiff(key="a", old={"id": "a", "val": "2"}, new=None)           # removed
_R_B = RowDiff(                                                            # modified
    key="b",
    old={"id": "b", "val": "3"},
    new={"id": "b", "val": "9"},
)


def test_sort_by_key_asc():
    result = sort_diff(_result(_R_C, _R_B, _R_A), by="key", order="asc")
    assert [r.key for r in result.rows] == ["a", "b", "c"]


def test_sort_by_key_desc():
    result = sort_diff(_result(_R_A, _R_B, _R_C), by="key", order="desc")
    assert [r.key for r in result.rows] == ["c", "b", "a"]


def test_sort_by_type_asc():
    # added=0, removed=1, modified=2
    result = sort_diff(_result(_R_B, _R_A, _R_C), by="type", order="asc")
    types = []
    for r in result.rows:
        if r.old is None:
            types.append("added")
        elif r.new is None:
            types.append("removed")
        else:
            types.append("modified")
    assert types == ["added", "removed", "modified"]


def test_sort_by_type_desc():
    result = sort_diff(_result(_R_B, _R_A, _R_C), by="type", order="desc")
    first = result.rows[0]
    assert first.old is not None and first.new is not None  # modified first


def test_sort_preserves_headers():
    result = sort_diff(_result(_R_A, _R_C), by="key")
    assert result.headers == _HEADERS


def test_sort_empty():
    result = sort_diff(_result(), by="key")
    assert result.rows == []


def test_sort_unknown_key_raises():
    with pytest.raises(ValueError, match="Unknown sort key"):
        sort_diff(_result(_R_A), by="invalid")  # type: ignore[arg-type]


def test_sort_stable_for_equal_keys():
    r1 = RowDiff(key="x", old=None, new={"id": "x", "val": "1"})
    r2 = RowDiff(key="x", old=None, new={"id": "x", "val": "2"})
    result = sort_diff(_result(r1, r2), by="key", order="asc")
    assert result.rows[0] is r1  # stable sort preserves original order
