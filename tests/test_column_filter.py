"""Tests for csv_diff_reporter.column_filter."""

from __future__ import annotations

import pytest

from csv_diff_reporter.column_filter import ColumnFilterOptions, filter_columns
from csv_diff_reporter.differ import DiffResult, RowDiff


HEADERS = ["id", "name", "age", "city"]


def _make_result(*rows: RowDiff) -> DiffResult:
    return DiffResult(rows=list(rows), headers=HEADERS)


def _modified(key: str, old: dict, new: dict, changed: list) -> RowDiff:
    return RowDiff(key=key, change_type="modified", old_row=old, new_row=new, changed_fields=changed)


def _added(key: str, new: dict) -> RowDiff:
    return RowDiff(key=key, change_type="added", old_row=None, new_row=new, changed_fields=None)


def _removed(key: str, old: dict) -> RowDiff:
    return RowDiff(key=key, change_type="removed", old_row=old, new_row=None, changed_fields=None)


# ---------------------------------------------------------------------------
# No-op cases
# ---------------------------------------------------------------------------

def test_filter_columns_no_options_returns_same_object():
    row = _modified("1", {"id": "1", "name": "Alice"}, {"id": "1", "name": "Bob"}, ["name"])
    result = _make_result(row)
    out = filter_columns(result, ColumnFilterOptions())
    assert out is result


# ---------------------------------------------------------------------------
# include_columns
# ---------------------------------------------------------------------------

def test_filter_include_columns_modified():
    old = {"id": "1", "name": "Alice", "age": "30", "city": "NYC"}
    new = {"id": "1", "name": "Bob", "age": "30", "city": "LA"}
    row = _modified("1", old, new, ["name", "city"])
    opts = ColumnFilterOptions(include_columns=["id", "name"])
    out = filter_columns(_make_result(row), opts)
    assert list(out.rows[0].old_row.keys()) == ["id", "name"]
    assert list(out.rows[0].new_row.keys()) == ["id", "name"]
    assert out.rows[0].changed_fields == ["name"]


def test_filter_include_columns_added():
    new = {"id": "2", "name": "Carol", "age": "25", "city": "LA"}
    row = _added("2", new)
    opts = ColumnFilterOptions(include_columns=["id", "city"])
    out = filter_columns(_make_result(row), opts)
    assert out.rows[0].new_row == {"id": "2", "city": "LA"}
    assert out.rows[0].old_row is None


def test_filter_include_columns_removed():
    old = {"id": "3", "name": "Dave", "age": "40", "city": "SF"}
    row = _removed("3", old)
    opts = ColumnFilterOptions(include_columns=["name"])
    out = filter_columns(_make_result(row), opts)
    assert out.rows[0].old_row == {"name": "Dave"}


# ---------------------------------------------------------------------------
# exclude_columns
# ---------------------------------------------------------------------------

def test_filter_exclude_columns_removes_fields():
    old = {"id": "1", "name": "Alice", "age": "30", "city": "NYC"}
    new = {"id": "1", "name": "Alice", "age": "31", "city": "NYC"}
    row = _modified("1", old, new, ["age"])
    opts = ColumnFilterOptions(exclude_columns=["city", "name"])
    out = filter_columns(_make_result(row), opts)
    assert "city" not in out.rows[0].old_row
    assert "name" not in out.rows[0].new_row
    assert "id" in out.rows[0].old_row
    assert "age" in out.rows[0].old_row


def test_filter_exclude_removes_from_changed_fields():
    old = {"id": "1", "name": "Alice", "age": "30"}
    new = {"id": "1", "name": "Bob", "age": "31"}
    row = _modified("1", old, new, ["name", "age"])
    opts = ColumnFilterOptions(exclude_columns=["age"])
    out = filter_columns(_make_result(row), opts)
    assert out.rows[0].changed_fields == ["name"]


# ---------------------------------------------------------------------------
# Combined include + exclude
# ---------------------------------------------------------------------------

def test_filter_include_and_exclude_exclude_wins():
    old = {"id": "1", "name": "Alice", "age": "30"}
    new = {"id": "1", "name": "Bob", "age": "31"}
    row = _modified("1", old, new, ["name", "age"])
    # include asks for name + age, but exclude removes age
    opts = ColumnFilterOptions(include_columns=["name", "age"], exclude_columns=["age"])
    out = filter_columns(_make_result(row), opts)
    assert list(out.rows[0].old_row.keys()) == ["name"]
