"""Tests for csv_diff_reporter.diff_formatter_yaml."""
from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_formatter_yaml import format_diff_as_yaml, _escape_str


def _row(
    key: str = "1",
    change_type: str = "modified",
    old_fields: dict | None = None,
    new_fields: dict | None = None,
) -> RowDiff:
    return RowDiff(
        key=key,
        change_type=change_type,
        old_fields=old_fields or {},
        new_fields=new_fields or {},
    )


def _make_result(rows: list[RowDiff] | None = None) -> DiffResult:
    return DiffResult(headers=["id", "name", "value"], rows=rows or [])


# ---------------------------------------------------------------------------
# _escape_str
# ---------------------------------------------------------------------------

def test_escape_str_plain_value():
    assert _escape_str("hello") == "hello"


def test_escape_str_empty_string():
    assert _escape_str("") == '""'


def test_escape_str_contains_colon():
    result = _escape_str("key: value")
    assert result.startswith('"') and result.endswith('"')


def test_escape_str_boolean_like():
    assert _escape_str("true") == '"true"'
    assert _escape_str("yes") == '"yes"'


# ---------------------------------------------------------------------------
# format_diff_as_yaml
# ---------------------------------------------------------------------------

def test_format_yaml_empty_result_is_string():
    result = _make_result()
    output = format_diff_as_yaml(result)
    assert isinstance(output, str)


def test_format_yaml_empty_result_shows_zero_counts():
    output = format_diff_as_yaml(_make_result())
    assert "added: 0" in output
    assert "removed: 0" in output
    assert "modified: 0" in output


def test_format_yaml_empty_result_rows_empty():
    output = format_diff_as_yaml(_make_result())
    assert "[]" in output


def test_format_yaml_includes_headers():
    output = format_diff_as_yaml(_make_result())
    assert "id" in output
    assert "name" in output


def test_format_yaml_added_row_change_type():
    row = _row(key="10", change_type="added", new_fields={"id": "10", "name": "Alice"})
    output = format_diff_as_yaml(_make_result([row]))
    assert "change_type: added" in output
    assert "added: 1" in output


def test_format_yaml_removed_row_change_type():
    row = _row(key="5", change_type="removed", old_fields={"id": "5", "name": "Bob"})
    output = format_diff_as_yaml(_make_result([row]))
    assert "change_type: removed" in output
    assert "removed: 1" in output


def test_format_yaml_modified_row_has_old_and_new_fields():
    row = _row(
        key="3",
        change_type="modified",
        old_fields={"name": "Old"},
        new_fields={"name": "New"},
    )
    output = format_diff_as_yaml(_make_result([row]))
    assert "old_fields:" in output
    assert "new_fields:" in output
    assert "Old" in output
    assert "New" in output


def test_format_yaml_key_appears_in_output():
    row = _row(key="abc-123", change_type="added", new_fields={"id": "abc-123"})
    output = format_diff_as_yaml(_make_result([row]))
    assert "abc-123" in output


def test_format_yaml_ends_with_newline():
    output = format_diff_as_yaml(_make_result())
    assert output.endswith('\n')


def test_format_yaml_multiple_rows_counts():
    rows = [
        _row(key="1", change_type="added", new_fields={"id": "1"}),
        _row(key="2", change_type="removed", old_fields={"id": "2"}),
        _row(key="3", change_type="modified", old_fields={"id": "3"}, new_fields={"id": "3"}),
    ]
    output = format_diff_as_yaml(_make_result(rows))
    assert "added: 1" in output
    assert "removed: 1" in output
    assert "modified: 1" in output
