"""Tests for csv_diff_reporter.diff_grouper."""
from __future__ import annotations

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_grouper import GroupOptions, GroupedDiff, group_diff


def _row(
    key: str,
    change_type: str,
    new_fields=None,
    old_fields=None,
) -> RowDiff:
    return RowDiff(
        key=key,
        change_type=change_type,
        old_fields=old_fields,
        new_fields=new_fields,
    )


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(rows=list(rows), headers=[])


def test_group_diff_empty_result():
    result = _result()
    grouped = group_diff(result, GroupOptions(column="region"))
    assert grouped.groups == {}
    assert grouped.total_rows() == 0


def test_group_diff_single_group():
    r1 = _row("1", "added", new_fields={"region": "EU", "val": "10"})
    r2 = _row("2", "added", new_fields={"region": "EU", "val": "20"})
    grouped = group_diff(_result(r1, r2), GroupOptions(column="region"))
    assert grouped.group_keys() == ["EU"]
    assert len(grouped.rows_for("EU")) == 2


def test_group_diff_multiple_groups():
    r1 = _row("1", "added", new_fields={"region": "EU"})
    r2 = _row("2", "modified", new_fields={"region": "US"}, old_fields={"region": "US"})
    r3 = _row("3", "removed", old_fields={"region": "EU"})
    grouped = group_diff(_result(r1, r2, r3), GroupOptions(column="region"))
    assert set(grouped.group_keys()) == {"EU", "US"}
    assert len(grouped.rows_for("EU")) == 2
    assert len(grouped.rows_for("US")) == 1


def test_group_diff_missing_column_uses_fallback():
    r = _row("1", "added", new_fields={"other": "x"})
    grouped = group_diff(_result(r), GroupOptions(column="region", ungrouped_label="???"))
    assert "???" in grouped.groups


def test_group_diff_drop_ungrouped():
    r1 = _row("1", "added", new_fields={"region": "EU"})
    r2 = _row("2", "added", new_fields={"other": "x"})
    grouped = group_diff(
        _result(r1, r2),
        GroupOptions(column="region", include_ungrouped=False),
    )
    assert grouped.group_keys() == ["EU"]
    assert grouped.total_rows() == 1


def test_group_diff_uses_old_fields_for_removed_row():
    r = _row("1", "removed", old_fields={"region": "APAC"})
    grouped = group_diff(_result(r), GroupOptions(column="region"))
    assert "APAC" in grouped.groups


def test_group_keys_are_sorted():
    rows = [
        _row(str(i), "added", new_fields={"region": region})
        for i, region in enumerate(["US", "EU", "APAC"])
    ]
    grouped = group_diff(_result(*rows), GroupOptions(column="region"))
    assert grouped.group_keys() == ["APAC", "EU", "US"]


def test_rows_for_unknown_key_returns_empty():
    grouped = GroupedDiff(column="region", groups={"EU": []})
    assert grouped.rows_for("UNKNOWN") == []


def test_total_rows_counts_across_all_groups():
    r1 = _row("1", "added", new_fields={"region": "EU"})
    r2 = _row("2", "added", new_fields={"region": "EU"})
    r3 = _row("3", "added", new_fields={"region": "US"})
    grouped = group_diff(_result(r1, r2, r3), GroupOptions(column="region"))
    assert grouped.total_rows() == 3
