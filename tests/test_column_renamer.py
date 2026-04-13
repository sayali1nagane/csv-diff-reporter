"""Tests for csv_diff_reporter.column_renamer and csv_diff_reporter.cli_rename."""

import argparse
import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.column_renamer import RenameOptions, rename_columns
from csv_diff_reporter.cli_rename import (
    add_rename_args,
    apply_rename,
    _parse_renames,
)


def _make_result() -> DiffResult:
    rows = [
        RowDiff(key="1", change_type="added", old_fields=None, new_fields={"id": "1", "name": "Alice"}),
        RowDiff(key="2", change_type="removed", old_fields={"id": "2", "name": "Bob"}, new_fields=None),
        RowDiff(
            key="3",
            change_type="modified",
            old_fields={"id": "3", "name": "Carol"},
            new_fields={"id": "3", "name": "Caroline"},
        ),
    ]
    return DiffResult(rows=rows, headers=["id", "name"])


def test_rename_columns_no_options_returns_same_object():
    result = _make_result()
    assert rename_columns(result, None) is result


def test_rename_columns_empty_mapping_returns_same_object():
    result = _make_result()
    assert rename_columns(result, RenameOptions(mapping={})) is result


def test_rename_columns_renames_headers():
    result = _make_result()
    renamed = rename_columns(result, RenameOptions(mapping={"name": "full_name"}))
    assert renamed.headers == ["id", "full_name"]


def test_rename_columns_renames_added_row_fields():
    result = _make_result()
    renamed = rename_columns(result, RenameOptions(mapping={"name": "full_name"}))
    added = renamed.rows[0]
    assert "full_name" in added.new_fields
    assert "name" not in added.new_fields


def test_rename_columns_renames_removed_row_fields():
    result = _make_result()
    renamed = rename_columns(result, RenameOptions(mapping={"name": "full_name"}))
    removed = renamed.rows[1]
    assert "full_name" in removed.old_fields
    assert "name" not in removed.old_fields


def test_rename_columns_renames_modified_row_both_sides():
    result = _make_result()
    renamed = rename_columns(result, RenameOptions(mapping={"name": "full_name"}))
    modified = renamed.rows[2]
    assert "full_name" in modified.old_fields
    assert "full_name" in modified.new_fields


def test_rename_columns_unknown_column_left_unchanged():
    result = _make_result()
    renamed = rename_columns(result, RenameOptions(mapping={"nonexistent": "x"}))
    assert renamed.headers == ["id", "name"]


def test_parse_renames_none_on_empty():
    assert _parse_renames([]) is None


def test_parse_renames_builds_mapping():
    opts = _parse_renames(["name:full_name", "id:identifier"])
    assert opts.mapping == {"name": "full_name", "id": "identifier"}


def test_parse_renames_raises_on_missing_colon():
    with pytest.raises(ValueError, match="OLD:NEW"):
        _parse_renames(["badvalue"])


def test_parse_renames_raises_on_empty_part():
    with pytest.raises(ValueError, match="non-empty"):
        _parse_renames([":new"])


def test_add_rename_args_registers_flag():
    parser = argparse.ArgumentParser()
    add_rename_args(parser)
    args = parser.parse_args(["--rename", "a:b", "--rename", "c:d"])
    assert args.renames == ["a:b", "c:d"]


def test_apply_rename_delegates_correctly():
    parser = argparse.ArgumentParser()
    add_rename_args(parser)
    args = parser.parse_args(["--rename", "name:full_name"])
    result = _make_result()
    renamed = apply_rename(args, result)
    assert renamed.headers == ["id", "full_name"]
