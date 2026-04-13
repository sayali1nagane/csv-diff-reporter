"""Tests for csv_diff_reporter.formatter."""

from __future__ import annotations

import json

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.formatter import (
    format_as_json,
    format_as_markdown,
    format_output,
)


def _make_result(
    added: int = 0,
    removed: int = 0,
    modified: int = 0,
    row_diffs: list[RowDiff] | None = None,
) -> DiffResult:
    return DiffResult(
        added=added,
        removed=removed,
        modified=modified,
        row_diffs=row_diffs or [],
    )


def _added_row() -> RowDiff:
    return RowDiff(key="1", status="added", old_row=None, new_row={"id": "1", "name": "Alice"}, changed_fields=[])


def _removed_row() -> RowDiff:
    return RowDiff(key="2", status="removed", old_row={"id": "2", "name": "Bob"}, new_row=None, changed_fields=[])


def _modified_row() -> RowDiff:
    return RowDiff(
        key="3",
        status="modified",
        old_row={"id": "3", "name": "Carol"},
        new_row={"id": "3", "name": "Caroline"},
        changed_fields=["name"],
    )


# --- JSON formatter ---

def test_format_json_empty():
    result = _make_result()
    data = json.loads(format_as_json(result))
    assert data["summary"]["total_changes"] == 0
    assert data["changes"] == []


def test_format_json_summary_counts():
    result = _make_result(added=1, removed=1, modified=1, row_diffs=[_added_row(), _removed_row(), _modified_row()])
    data = json.loads(format_as_json(result))
    assert data["summary"]["added"] == 1
    assert data["summary"]["removed"] == 1
    assert data["summary"]["modified"] == 1
    assert data["summary"]["total_changes"] == 3


def test_format_json_change_fields():
    result = _make_result(modified=1, row_diffs=[_modified_row()])
    data = json.loads(format_as_json(result))
    change = data["changes"][0]
    assert change["key"] == "3"
    assert change["status"] == "modified"
    assert "name" in change["changed_fields"]


# --- Markdown formatter ---

def test_format_markdown_contains_header():
    result = _make_result()
    md = format_as_markdown(result)
    assert "# CSV Diff Report" in md


def test_format_markdown_no_diff_message():
    result = _make_result()
    md = format_as_markdown(result)
    assert "No differences" in md


def test_format_markdown_added_row():
    result = _make_result(added=1, row_diffs=[_added_row()])
    md = format_as_markdown(result)
    assert "added" in md
    assert "Alice" in md


def test_format_markdown_modified_table():
    result = _make_result(modified=1, row_diffs=[_modified_row()])
    md = format_as_markdown(result)
    assert "Carol" in md
    assert "Caroline" in md
    assert "| Field |" in md


# --- dispatch ---

def test_format_output_json():
    result = _make_result()
    out = format_output(result, "json")
    json.loads(out)  # must be valid JSON


def test_format_output_markdown():
    result = _make_result()
    out = format_output(result, "markdown")
    assert "#" in out


def test_format_output_text_fallback():
    result = _make_result()
    out = format_output(result, "text")
    assert isinstance(out, str)
