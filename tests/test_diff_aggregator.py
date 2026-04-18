import pytest
from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_aggregator import aggregate_diff, AggregateGroup


def _row(change_type, fields):
    old = fields if change_type in ("removed", "modified") else None
    new = fields if change_type in ("added", "modified") else None
    return RowDiff(key=fields.get("id", "k"), change_type=change_type, old_fields=old, new_fields=new)


def _result(rows):
    return DiffResult(headers=["id", "region", "val"], rows=rows)


def test_aggregate_empty_result():
    agg = aggregate_diff(_result([]), "region")
    assert agg.column == "region"
    assert agg.groups == {}


def test_aggregate_counts_added():
    rows = [_row("added", {"id": "1", "region": "EU", "val": "x"})]
    agg = aggregate_diff(_result(rows), "region")
    assert agg.groups["EU"].added == 1
    assert agg.groups["EU"].removed == 0
    assert agg.groups["EU"].modified == 0


def test_aggregate_counts_removed():
    rows = [_row("removed", {"id": "1", "region": "US", "val": "y"})]
    agg = aggregate_diff(_result(rows), "region")
    assert agg.groups["US"].removed == 1


def test_aggregate_counts_modified():
    rows = [_row("modified", {"id": "1", "region": "APAC", "val": "z"})]
    agg = aggregate_diff(_result(rows), "region")
    assert agg.groups["APAC"].modified == 1


def test_aggregate_multiple_groups():
    rows = [
        _row("added", {"id": "1", "region": "EU", "val": "a"}),
        _row("added", {"id": "2", "region": "EU", "val": "b"}),
        _row("removed", {"id": "3", "region": "US", "val": "c"}),
    ]
    agg = aggregate_diff(_result(rows), "region")
    assert agg.groups["EU"].added == 2
    assert agg.groups["EU"].total == 2
    assert agg.groups["US"].removed == 1


def test_aggregate_missing_column_uses_empty_string():
    rows = [_row("added", {"id": "1", "val": "x"})]
    agg = aggregate_diff(_result(rows), "region")
    assert "" in agg.groups


def test_sorted_groups_by_total_descending():
    rows = [
        _row("added", {"id": "1", "region": "EU", "val": "a"}),
        _row("added", {"id": "2", "region": "EU", "val": "b"}),
        _row("removed", {"id": "3", "region": "US", "val": "c"}),
    ]
    agg = aggregate_diff(_result(rows), "region")
    groups = agg.sorted_groups()
    assert groups[0].key == "EU"


def test_as_dict_contains_expected_keys():
    g = AggregateGroup(key="EU", added=2, removed=1, modified=3)
    d = g.as_dict()
    assert set(d.keys()) == {"key", "added", "removed", "modified", "total"}
    assert d["total"] == 6
