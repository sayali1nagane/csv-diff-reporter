"""Tests for csv_diff_reporter.diff_formatter_csv."""
from __future__ import annotations

import csv
import io

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_formatter_csv import (
    _CHANGE_TYPE_HEADER,
    _KEY_HEADER,
    format_diff_as_csv,
)


def _row(
    key: str,
    change_type: str,
    old_fields: dict | None = None,
    new_fields: dict | None = None,
) -> RowDiff:
    return RowDiff(
        key=key,
        change_type=change_type,
        old_fields=old_fields,
        new_fields=new_fields,
    )


def _make_result(*rows: RowDiff) -> DiffResult:
    headers = ["name", "age"]
    return DiffResult(headers=headers, rows=list(rows))


def _parse(csv_text: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(csv_text)))


def test_format_csv_empty_result_has_header_only():
    result = _make_result()
    text = format_diff_as_csv(result)
    lines = text.strip().splitlines()
    assert len(lines) == 1
    assert _CHANGE_TYPE_HEADER in lines[0]
    assert _KEY_HEADER in lines[0]


def test_format_csv_added_row():
    result = _make_result(_row("1", "added", new_fields={"name": "Alice", "age": "30"}))
    rows = _parse(format_diff_as_csv(result))
    assert len(rows) == 1
    assert rows[0][_CHANGE_TYPE_HEADER] == "added"
    assert rows[0]["name"] == "Alice"


def test_format_csv_removed_row():
    result = _make_result(_row("2", "removed", old_fields={"name": "Bob", "age": "25"}))
    rows = _parse(format_diff_as_csv(result))
    assert len(rows) == 1
    assert rows[0][_CHANGE_TYPE_HEADER] == "removed"
    assert rows[0]["name"] == "Bob"


def test_format_csv_modified_row():
    result = _make_result(
        _row(
            "3",
            "modified",
            old_fields={"name": "Carol", "age": "20"},
            new_fields={"name": "Carol", "age": "21"},
        )
    )
    rows = _parse(format_diff_as_csv(result))
    assert rows[0][_CHANGE_TYPE_HEADER] == "modified"
    assert rows[0]["age"] == "21"


def test_format_csv_unchanged_excluded_by_default():
    result = _make_result(
        _row("1", "added", new_fields={"name": "Alice", "age": "30"}),
        _row("2", "unchanged", new_fields={"name": "Dave", "age": "40"}),
    )
    rows = _parse(format_diff_as_csv(result))
    assert len(rows) == 1
    assert rows[0][_CHANGE_TYPE_HEADER] == "added"


def test_format_csv_unchanged_included_when_flag_set():
    result = _make_result(
        _row("1", "added", new_fields={"name": "Alice", "age": "30"}),
        _row("2", "unchanged", new_fields={"name": "Dave", "age": "40"}),
    )
    rows = _parse(format_diff_as_csv(result, include_unchanged=True))
    assert len(rows) == 2


def test_format_csv_key_column_present():
    result = _make_result(_row("42", "added", new_fields={"name": "Eve", "age": "28"}))
    rows = _parse(format_diff_as_csv(result))
    assert rows[0][_KEY_HEADER] == "42"


def test_format_csv_missing_fields_are_empty_string():
    result = _make_result(_row("1", "added", new_fields={"name": "Frank"}))
    rows = _parse(format_diff_as_csv(result))
    assert rows[0].get("age", "") == ""
