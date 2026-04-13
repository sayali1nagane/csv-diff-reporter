"""Tests for csv_diff_reporter.filter."""

from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.filter import FilterOptions, filter_diff


_HEADERS = ["id", "name", "score"]


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(rows=list(rows), headers=_HEADERS)


_ADDED = RowDiff(key="1", old=None, new={"id": "1", "name": "Alice", "score": "10"})
_REMOVED = RowDiff(key="2", old={"id": "2", "name": "Bob", "score": "20"}, new=None)
_MODIFIED = RowDiff(
    key="3",
    old={"id": "3", "name": "Carol", "score": "30"},
    new={"id": "3", "name": "Carol", "score": "99"},
)


def test_filter_default_keeps_all():
    result = _result(_ADDED, _REMOVED, _MODIFIED)
    filtered = filter_diff(result)
    assert len(filtered.rows) == 3


def test_filter_exclude_added():
    opts = FilterOptions(include_added=False)
    filtered = filter_diff(_result(_ADDED, _REMOVED, _MODIFIED), opts)
    assert _ADDED not in filtered.rows
    assert len(filtered.rows) == 2


def test_filter_exclude_removed():
    opts = FilterOptions(include_removed=False)
    filtered = filter_diff(_result(_ADDED, _REMOVED, _MODIFIED), opts)
    assert _REMOVED not in filtered.rows
    assert len(filtered.rows) == 2


def test_filter_exclude_modified():
    opts = FilterOptions(include_modified=False)
    filtered = filter_diff(_result(_ADDED, _REMOVED, _MODIFIED), opts)
    assert _MODIFIED not in filtered.rows
    assert len(filtered.rows) == 2


def test_filter_by_column_match():
    opts = FilterOptions(columns={"score"})
    filtered = filter_diff(_result(_ADDED, _REMOVED, _MODIFIED), opts)
    # _ADDED and _REMOVED touch all columns; _MODIFIED changes 'score'
    assert len(filtered.rows) == 3


def test_filter_by_column_no_match():
    opts = FilterOptions(columns={"nonexistent"})
    filtered = filter_diff(_result(_MODIFIED), opts)
    assert len(filtered.rows) == 0


def test_filter_preserves_headers():
    result = _result(_ADDED)
    filtered = filter_diff(result, FilterOptions())
    assert filtered.headers == _HEADERS


def test_filter_empty_result():
    filtered = filter_diff(_result(), FilterOptions())
    assert filtered.rows == []


def test_filter_none_opts_defaults():
    result = _result(_ADDED, _REMOVED)
    filtered = filter_diff(result, None)
    assert len(filtered.rows) == 2
