import pytest
from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_comparator import compare_diffs, ComparisonResult


def _row(key, change_type, before=None, after=None):
    return RowDiff(
        key=key,
        change_type=change_type,
        before=before or {},
        after=after or {},
    )


def _result(*rows):
    headers = ["id", "name"]
    return DiffResult(headers=headers, rows=list(rows))


def test_compare_empty_diffs():
    r = compare_diffs(_result(), _result())
    assert r.common_added == 0
    assert r.common_removed == 0
    assert r.common_modified == 0


def test_compare_common_added():
    a = _result(_row("1", "added"))
    b = _result(_row("1", "added"))
    r = compare_diffs(a, b)
    assert r.common_added == 1
    assert r.added_only_in_a == 0
    assert r.added_only_in_b == 0


def test_compare_added_only_in_a():
    a = _result(_row("1", "added"))
    b = _result()
    r = compare_diffs(a, b)
    assert r.added_only_in_a == 1
    assert r.added_only_in_b == 0
    assert r.common_added == 0


def test_compare_added_only_in_b():
    a = _result()
    b = _result(_row("2", "added"))
    r = compare_diffs(a, b)
    assert r.added_only_in_b == 1
    assert r.added_only_in_a == 0


def test_compare_mixed_types():
    a = _result(_row("1", "added"), _row("2", "removed"), _row("3", "modified"))
    b = _result(_row("1", "added"), _row("2", "added"), _row("3", "modified"))
    r = compare_diffs(a, b)
    assert r.common_added == 1
    assert r.removed_only_in_a == 1
    assert r.added_only_in_b == 1
    assert r.common_modified == 1


def test_compare_labels_stored():
    r = compare_diffs(_result(), _result(), label_a="old", label_b="new")
    assert r.labels["a"] == "old"
    assert r.labels["b"] == "new"


def test_as_dict_keys():
    r = ComparisonResult(common_added=2, added_only_in_a=1)
    d = r.as_dict()
    assert "common_added" in d
    assert d["common_added"] == 2
    assert d["added_only_in_a"] == 1
