"""Tests for csv_diff_reporter.diff_formatter_ndjson."""
from __future__ import annotations

import json

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_formatter_ndjson import format_diff_as_ndjson, _row_to_record


def _row(key: str, *, added=False, removed=False,
         old=None, new=None) -> RowDiff:
    old = old or {}
    new = new or {}
    return RowDiff(
        key=key,
        added=added,
        removed=removed,
        old_fields=old,
        new_fields=new,
    )


def _make_result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id", "name"], rows=list(rows))


def _parse_lines(text: str) -> list[dict]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# _row_to_record
# ---------------------------------------------------------------------------

def test_row_to_record_added():
    r = _row("1", added=True, new={"id": "1", "name": "Alice"})
    rec = _row_to_record(r)
    assert rec["change_type"] == "added"
    assert rec["key"] == "1"
    assert rec["fields"] == {"id": "1", "name": "Alice"}
    assert "old_fields" not in rec


def test_row_to_record_removed():
    r = _row("2", removed=True, old={"id": "2", "name": "Bob"})
    rec = _row_to_record(r)
    assert rec["change_type"] == "removed"
    assert rec["fields"] == {"id": "2", "name": "Bob"}
    assert "old_fields" not in rec


def test_row_to_record_modified_includes_old_fields():
    r = _row("3", old={"id": "3", "name": "Old"}, new={"id": "3", "name": "New"})
    rec = _row_to_record(r)
    assert rec["change_type"] == "modified"
    assert rec["fields"] == {"id": "3", "name": "New"}
    assert rec["old_fields"] == {"id": "3", "name": "Old"}


# ---------------------------------------------------------------------------
# format_diff_as_ndjson
# ---------------------------------------------------------------------------

def test_format_ndjson_empty_result_returns_empty_string():
    result = _make_result()
    assert format_diff_as_ndjson(result) == ""


def test_format_ndjson_single_added_row():
    result = _make_result(_row("1", added=True, new={"id": "1", "name": "Alice"}))
    text = format_diff_as_ndjson(result)
    records = _parse_lines(text)
    assert len(records) == 1
    assert records[0]["change_type"] == "added"


def test_format_ndjson_multiple_rows_one_line_each():
    rows = [
        _row("1", added=True, new={"id": "1"}),
        _row("2", removed=True, old={"id": "2"}),
        _row("3", old={"id": "3", "name": "X"}, new={"id": "3", "name": "Y"}),
    ]
    result = _make_result(*rows)
    text = format_diff_as_ndjson(result)
    lines = [l for l in text.splitlines() if l.strip()]
    assert len(lines) == 3


def test_format_ndjson_each_line_is_valid_json():
    rows = [
        _row("1", added=True, new={"id": "1", "name": "Alice"}),
        _row("2", removed=True, old={"id": "2", "name": "Bob"}),
    ]
    text = format_diff_as_ndjson(_make_result(*rows))
    for line in text.splitlines():
        obj = json.loads(line)  # must not raise
        assert "change_type" in obj
        assert "key" in obj


def test_format_ndjson_no_trailing_newline_for_single_row():
    result = _make_result(_row("1", added=True, new={"id": "1"}))
    text = format_diff_as_ndjson(result)
    assert not text.endswith("\n")
