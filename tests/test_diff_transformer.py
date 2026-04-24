"""Tests for csv_diff_reporter.diff_transformer."""
import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_transformer import (
    TransformOptions,
    transform_diff,
)


def _row(change_type: str, key: str, old=None, new=None) -> RowDiff:
    return RowDiff(
        change_type=change_type,
        key=key,
        old_fields=old or {},
        new_fields=new or {},
    )


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id", "name", "value"], rows=list(rows))


def test_transform_no_options_returns_same_object():
    result = _result(_row("added", "1", new={"id": "1", "name": "Alice"}))
    tr = transform_diff(result, None)
    assert tr.result is result
    assert tr.columns_affected == []


def test_transform_empty_options_returns_same_object():
    result = _result()
    tr = transform_diff(result, TransformOptions())
    assert tr.result is result


def test_transform_upper_on_added_row():
    row = _row("added", "1", new={"id": "1", "name": "alice"})
    result = _result(row)
    opts = TransformOptions(column_transforms={"name": str.upper})
    tr = transform_diff(result, opts)
    assert tr.result.rows[0].new_fields["name"] == "ALICE"
    assert tr.result.rows[0].new_fields["id"] == "1"  # untouched


def test_transform_lower_on_removed_row():
    row = _row("removed", "2", old={"id": "2", "name": "BOB"})
    result = _result(row)
    opts = TransformOptions(column_transforms={"name": str.lower})
    tr = transform_diff(result, opts)
    assert tr.result.rows[0].old_fields["name"] == "bob"


def test_transform_modified_row_both_fields():
    row = _row("modified", "3",
               old={"id": "3", "name": " carol "},
               new={"id": "3", "name": " dave "})
    result = _result(row)
    opts = TransformOptions(column_transforms={"name": str.strip})
    tr = transform_diff(result, opts)
    assert tr.result.rows[0].old_fields["name"] == "carol"
    assert tr.result.rows[0].new_fields["name"] == "dave"


def test_transform_default_applies_to_all_columns():
    row = _row("added", "4", new={"id": "4", "name": "eve", "value": "x"})
    result = _result(row)
    opts = TransformOptions(default_transform=str.upper)
    tr = transform_diff(result, opts)
    assert tr.result.rows[0].new_fields["name"] == "EVE"
    assert tr.result.rows[0].new_fields["value"] == "X"
    assert "*" in tr.columns_affected


def test_transform_column_overrides_default():
    row = _row("added", "5", new={"id": "5", "name": "frank"})
    result = _result(row)
    opts = TransformOptions(
        column_transforms={"name": str.upper},
        default_transform=str.strip,
    )
    tr = transform_diff(result, opts)
    assert tr.result.rows[0].new_fields["name"] == "FRANK"


def test_transform_columns_affected_lists_mapped_columns():
    result = _result()
    opts = TransformOptions(column_transforms={"name": str.upper, "value": str.lower})
    tr = transform_diff(result, opts)
    assert set(tr.columns_affected) == {"name", "value"}


def test_transform_preserves_headers():
    result = _result()
    opts = TransformOptions(column_transforms={"name": str.upper})
    tr = transform_diff(result, opts)
    assert tr.result.headers == result.headers


def test_transform_bad_fn_returns_original_value():
    def bad_fn(v: str) -> str:
        raise RuntimeError("oops")

    row = _row("added", "6", new={"id": "6", "name": "grace"})
    result = _result(row)
    opts = TransformOptions(column_transforms={"name": bad_fn})
    tr = transform_diff(result, opts)
    assert tr.result.rows[0].new_fields["name"] == "grace"
