"""Tests for csv_diff_reporter.diff_normalizer."""
import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_normalizer import NormalizeOptions, normalize_diff


HEADERS = ["id", "name", "status"]


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=HEADERS, rows=list(rows))


def _modified(key: str, old: dict, new: dict) -> RowDiff:
    return RowDiff(key=key, change_type="modified", old_fields=old, new_fields=new)


def _added(key: str, new: dict) -> RowDiff:
    return RowDiff(key=key, change_type="added", old_fields=None, new_fields=new)


def _removed(key: str, old: dict) -> RowDiff:
    return RowDiff(key=key, change_type="removed", old_fields=old, new_fields=None)


def test_normalize_strips_whitespace_by_default():
    row = _modified("1", {"name": "  Alice  "}, {"name": "Bob  "})
    result = normalize_diff(_result(row))
    assert result.rows[0].old_fields["name"] == "Alice"
    assert result.rows[0].new_fields["name"] == "Bob"


def test_normalize_lowercase():
    row = _added("2", {"name": "Alice", "status": "ACTIVE"})
    opts = NormalizeOptions(lowercase=True)
    result = normalize_diff(_result(row), opts)
    assert result.rows[0].new_fields["name"] == "alice"
    assert result.rows[0].new_fields["status"] == "active"


def test_normalize_value_map():
    row = _modified("3", {"status": "Y"}, {"status": "N"})
    opts = NormalizeOptions(value_map={"Y": "yes", "N": "no"})
    result = normalize_diff(_result(row), opts)
    assert result.rows[0].old_fields["status"] == "yes"
    assert result.rows[0].new_fields["status"] == "no"


def test_normalize_removed_row_old_fields_normalized():
    row = _removed("4", {"name": "  Carol  "})
    result = normalize_diff(_result(row))
    assert result.rows[0].old_fields["name"] == "Carol"
    assert result.rows[0].new_fields is None


def test_normalize_added_row_new_fields_normalized():
    row = _added("5", {"name": "  Dave"})
    result = normalize_diff(_result(row))
    assert result.rows[0].new_fields["name"] == "Dave"
    assert result.rows[0].old_fields is None


def test_normalize_preserves_headers():
    result = normalize_diff(_result())
    assert result.headers == HEADERS


def test_normalize_no_options_uses_defaults():
    row = _added("6", {"name": " Eve "})
    result = normalize_diff(_result(row))
    assert result.rows[0].new_fields["name"] == "Eve"


def test_normalize_strip_whitespace_false_preserves_spaces():
    row = _added("7", {"name": " Eve "})
    opts = NormalizeOptions(strip_whitespace=False)
    result = normalize_diff(_result(row), opts)
    assert result.rows[0].new_fields["name"] == " Eve "


def test_normalize_empty_result_returns_empty():
    result = normalize_diff(_result())
    assert result.rows == []


def test_normalize_does_not_mutate_original():
    row = _added("8", {"name": "  Frank  "})
    original = _result(row)
    normalize_diff(original)
    assert original.rows[0].new_fields["name"] == "  Frank  "
