"""Tests for csv_diff_reporter.stats."""
import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.stats import (
    ColumnStats,
    DiffStats,
    compute_stats,
    format_stats_text,
)


def _modified(key: str, old: dict, new: dict) -> RowDiff:
    changed = [k for k in old if old.get(k) != new.get(k)]
    return RowDiff(key=key, change_type="modified", old_row=old, new_row=new, changed_fields=changed)


def _added(key: str, row: dict) -> RowDiff:
    return RowDiff(key=key, change_type="added", old_row=None, new_row=row, changed_fields=[])


def _removed(key: str, row: dict) -> RowDiff:
    return RowDiff(key=key, change_type="removed", old_row=row, new_row=None, changed_fields=[])


def _make_result(**kwargs) -> DiffResult:
    defaults = dict(added=[], removed=[], modified=[], unchanged=[])
    defaults.update(kwargs)
    return DiffResult(**defaults)


def test_compute_stats_empty():
    stats = compute_stats(_make_result())
    assert stats.total_rows_compared == 0
    assert stats.columns == {}


def test_compute_stats_counts_modified_columns():
    row = _modified("1", {"a": "x", "b": "y"}, {"a": "z", "b": "y"})
    stats = compute_stats(_make_result(modified=[row]))
    assert stats.columns["a"].changes == 1
    assert "b" not in stats.columns


def test_compute_stats_multiple_modifications_same_column():
    r1 = _modified("1", {"price": "10"}, {"price": "20"})
    r2 = _modified("2", {"price": "30"}, {"price": "40"})
    stats = compute_stats(_make_result(modified=[r1, r2]))
    assert stats.columns["price"].changes == 2


def test_compute_stats_added_rows():
    row = _added("3", {"name": "Alice", "age": "30"})
    stats = compute_stats(_make_result(added=[row]))
    assert stats.columns["name"].added_occurrences == 1
    assert stats.columns["age"].added_occurrences == 1


def test_compute_stats_removed_rows():
    row = _removed("4", {"name": "Bob"})
    stats = compute_stats(_make_result(removed=[row]))
    assert stats.columns["name"].removed_occurrences == 1


def test_compute_stats_total_rows_compared():
    a = _added("1", {"x": "1"})
    r = _removed("2", {"x": "2"})
    m = _modified("3", {"x": "3"}, {"x": "4"})
    stats = compute_stats(_make_result(added=[a], removed=[r], modified=[m]))
    assert stats.total_rows_compared == 3


def test_column_stats_as_dict():
    cs = ColumnStats(name="col", changes=2, added_occurrences=1, removed_occurrences=0)
    d = cs.as_dict()
    assert d == {"name": "col", "changes": 2, "added_occurrences": 1, "removed_occurrences": 0}


def test_diff_stats_as_dict():
    ds = DiffStats(total_rows_compared=5, columns={"a": ColumnStats(name="a", changes=3)})
    d = ds.as_dict()
    assert d["total_rows_compared"] == 5
    assert "a" in d["columns"]


def test_format_stats_text_no_changes():
    stats = compute_stats(_make_result())
    text = format_stats_text(stats)
    assert "No column-level changes" in text


def test_format_stats_text_with_changes():
    row = _modified("1", {"score": "1"}, {"score": "2"})
    stats = compute_stats(_make_result(modified=[row]))
    text = format_stats_text(stats)
    assert "score" in text
    assert "1 change" in text
