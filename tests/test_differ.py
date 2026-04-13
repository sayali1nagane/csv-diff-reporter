"""Tests for csv_diff_reporter.differ module."""

import pytest
from csv_diff_reporter.differ import DiffResult, RowDiff, diff_csv


OLD = {
    "1": {"id": "1", "name": "Alice", "score": "90"},
    "2": {"id": "2", "name": "Bob", "score": "80"},
    "3": {"id": "3", "name": "Carol", "score": "70"},
}

NEW = {
    "1": {"id": "1", "name": "Alice", "score": "95"},  # modified
    "3": {"id": "3", "name": "Carol", "score": "70"},  # unchanged
    "4": {"id": "4", "name": "Dave", "score": "85"},   # added
    # key "2" removed
}


def test_diff_detects_added_row():
    result = diff_csv(OLD, NEW)
    assert len(result.added) == 1
    assert result.added[0].key == "4"
    assert result.added[0].change_type == "added"
    assert result.added[0].new_row == NEW["4"]
    assert result.added[0].old_row is None


def test_diff_detects_removed_row():
    result = diff_csv(OLD, NEW)
    assert len(result.removed) == 1
    assert result.removed[0].key == "2"
    assert result.removed[0].change_type == "removed"
    assert result.removed[0].old_row == OLD["2"]
    assert result.removed[0].new_row is None


def test_diff_detects_modified_row():
    result = diff_csv(OLD, NEW)
    assert len(result.modified) == 1
    mod = result.modified[0]
    assert mod.key == "1"
    assert mod.change_type == "modified"
    assert mod.changed_fields == {"score": ("90", "95")}


def test_diff_unchanged_row_not_reported():
    result = diff_csv(OLD, NEW)
    modified_keys = {r.key for r in result.modified}
    assert "3" not in modified_keys


def test_diff_total_changes():
    result = diff_csv(OLD, NEW)
    assert result.total_changes == 3


def test_diff_empty_datasets():
    result = diff_csv({}, {})
    assert result.is_empty
    assert result.total_changes == 0


def test_diff_identical_datasets():
    result = diff_csv(OLD, OLD)
    assert result.is_empty


def test_diff_all_added():
    result = diff_csv({}, NEW)
    assert len(result.added) == len(NEW)
    assert result.removed == []
    assert result.modified == []


def test_diff_all_removed():
    result = diff_csv(OLD, {})
    assert len(result.removed) == len(OLD)
    assert result.added == []
    assert result.modified == []


def test_diff_multiple_changed_fields():
    old = {"x": {"id": "x", "a": "1", "b": "2"}}
    new = {"x": {"id": "x", "a": "9", "b": "8"}}
    result = diff_csv(old, new)
    assert len(result.modified) == 1
    assert result.modified[0].changed_fields == {"a": ("1", "9"), "b": ("2", "8")}


def test_diff_modified_row_contains_old_and_new_row():
    """Modified rows should carry both old_row and new_row for context."""
    result = diff_csv(OLD, NEW)
    mod = result.modified[0]
    assert mod.old_row == OLD["1"]
    assert mod.new_row == NEW["1"]
