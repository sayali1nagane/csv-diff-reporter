"""Tests for csv_diff_reporter.diff_classifier."""
import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_classifier import (
    ClassifyOptions,
    classify_diff,
)


def _row(
    key: str,
    old: dict | None = None,
    new: dict | None = None,
) -> RowDiff:
    return RowDiff(key=key, old_fields=old, new_fields=new)


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id", "name", "price"], rows=list(rows))


# ---------------------------------------------------------------------------
# classify_diff — no options
# ---------------------------------------------------------------------------

def test_classify_no_options_returns_all_as_other():
    row = _row("1", old={"name": "a"}, new={"name": "b"})
    res = classify_diff(_result(row))
    assert len(res.rows) == 1
    assert res.rows[0].category == "other"


def test_classify_empty_result_returns_empty_rows():
    res = classify_diff(_result())
    assert res.rows == []
    assert res.headers == ["id", "name", "price"]


# ---------------------------------------------------------------------------
# category detection
# ---------------------------------------------------------------------------

def test_classify_modified_row_matches_category():
    opts = ClassifyOptions(categories={"price_change": ["price"]})
    row = _row("1", old={"price": "10"}, new={"price": "20"})
    res = classify_diff(_result(row), opts)
    assert res.rows[0].category == "price_change"


def test_classify_modified_row_falls_back_to_default():
    opts = ClassifyOptions(categories={"price_change": ["price"]})
    row = _row("1", old={"name": "a"}, new={"name": "b"})
    res = classify_diff(_result(row), opts)
    assert res.rows[0].category == "other"


def test_classify_added_row_matches_category_by_field():
    opts = ClassifyOptions(categories={"new_entry": ["name"]})
    row = _row("2", old=None, new={"name": "Alice", "price": "5"})
    res = classify_diff(_result(row), opts)
    assert res.rows[0].category == "new_entry"


def test_classify_removed_row_matches_category_by_field():
    opts = ClassifyOptions(categories={"deletion": ["price"]})
    row = _row("3", old={"price": "99"}, new=None)
    res = classify_diff(_result(row), opts)
    assert res.rows[0].category == "deletion"


def test_classify_first_matching_category_wins():
    opts = ClassifyOptions(
        categories={"price_change": ["price"], "any_change": ["price", "name"]}
    )
    row = _row("1", old={"price": "1"}, new={"price": "2"})
    res = classify_diff(_result(row), opts)
    assert res.rows[0].category == "price_change"


# ---------------------------------------------------------------------------
# category_counts / for_category helpers
# ---------------------------------------------------------------------------

def test_category_counts_aggregates_correctly():
    opts = ClassifyOptions(categories={"price_change": ["price"]})
    rows = [
        _row("1", old={"price": "1"}, new={"price": "2"}),
        _row("2", old={"price": "3"}, new={"price": "4"}),
        _row("3", old={"name": "a"}, new={"name": "b"}),
    ]
    res = classify_diff(_result(*rows), opts)
    counts = res.category_counts()
    assert counts["price_change"] == 2
    assert counts["other"] == 1


def test_for_category_filters_correctly():
    opts = ClassifyOptions(categories={"price_change": ["price"]})
    rows = [
        _row("1", old={"price": "1"}, new={"price": "2"}),
        _row("2", old={"name": "a"}, new={"name": "b"}),
    ]
    res = classify_diff(_result(*rows), opts)
    assert len(res.for_category("price_change")) == 1
    assert len(res.for_category("other")) == 1


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_classified_row_as_dict_has_expected_keys():
    opts = ClassifyOptions(categories={"price_change": ["price"]})
    row = _row("42", old={"price": "5"}, new={"price": "10"})
    res = classify_diff(_result(row), opts)
    d = res.rows[0].as_dict()
    assert d["key"] == "42"
    assert d["change_type"] == "modified"
    assert d["category"] == "price_change"
