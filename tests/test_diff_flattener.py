"""Tests for csv_diff_reporter.diff_flattener."""
from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_flattener import (
    FlattenOptions,
    FlattenResult,
    flatten_diff,
)


def _row(key: str, old=None, new=None) -> RowDiff:
    return RowDiff(key=key, old=old, new=new)


def _result(*rows: RowDiff, headers=None) -> DiffResult:
    return DiffResult(
        rows=list(rows),
        headers=headers or ["name", "value"],
    )


def test_flatten_empty_result_returns_empty():
    res = flatten_diff(_result())
    assert res.rows == []
    assert res.total == 0


def test_flatten_added_row_has_added_label():
    r = _row("1", new={"name": "Alice", "value": "10"})
    res = flatten_diff(_result(r))
    assert len(res.rows) == 1
    assert res.rows[0]["_change"] == "added"


def test_flatten_removed_row_has_removed_label():
    r = _row("2", old={"name": "Bob", "value": "20"})
    res = flatten_diff(_result(r))
    assert res.rows[0]["_change"] == "removed"


def test_flatten_modified_row_has_modified_label():
    r = _row("3", old={"name": "Carol", "value": "30"}, new={"name": "Carol", "value": "99"})
    res = flatten_diff(_result(r))
    assert res.rows[0]["_change"] == "modified"


def test_flatten_unchanged_row_excluded_by_default():
    r = _row("4", old={"name": "Dave", "value": "5"}, new={"name": "Dave", "value": "5"})
    res = flatten_diff(_result(r))
    assert res.rows == []


def test_flatten_unchanged_row_included_when_opted_in():
    r = _row("4", old={"name": "Dave", "value": "5"}, new={"name": "Dave", "value": "5"})
    opts = FlattenOptions(include_unchanged=True)
    res = flatten_diff(_result(r), opts)
    assert len(res.rows) == 1


def test_flatten_key_column_present_by_default():
    r = _row("42", new={"name": "Eve", "value": "7"})
    res = flatten_diff(_result(r))
    assert "_key" in res.rows[0]
    assert res.rows[0]["_key"] == "42"


def test_flatten_key_column_omitted_when_none():
    r = _row("42", new={"name": "Eve", "value": "7"})
    opts = FlattenOptions(key_column=None)
    res = flatten_diff(_result(r), opts)
    assert "_key" not in res.rows[0]


def test_flatten_custom_change_key():
    r = _row("1", new={"name": "A", "value": "1"})
    opts = FlattenOptions(change_type_key="type")
    res = flatten_diff(_result(r), opts)
    assert "type" in res.rows[0]
    assert "_change" not in res.rows[0]


def test_flatten_headers_include_extra_columns():
    r = _row("1", new={"name": "A", "value": "1"})
    res = flatten_diff(_result(r))
    assert "_key" in res.headers
    assert "_change" in res.headers
    assert "name" in res.headers
    assert "value" in res.headers


def test_flatten_total_matches_row_count():
    rows = [
        _row("1", new={"name": "A", "value": "1"}),
        _row("2", old={"name": "B", "value": "2"}),
        _row("3", old={"name": "C", "value": "3"}, new={"name": "C", "value": "99"}),
    ]
    res = flatten_diff(_result(*rows))
    assert res.total == 3
    assert len(res.as_dicts()) == 3
