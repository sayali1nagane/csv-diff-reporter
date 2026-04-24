"""Tests for csv_diff_reporter.diff_enricher."""
from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_enricher import (
    EnrichOptions,
    EnrichResult,
    enrich_diff,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

HEADERS = ["id", "name", "score"]


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=HEADERS, rows=list(rows))


def _modified(key: str, old: dict, new: dict) -> RowDiff:
    return RowDiff(key=key, change_type="modified", old_fields=old, new_fields=new)


def _added(key: str, fields: dict) -> RowDiff:
    return RowDiff(key=key, change_type="added", old_fields=None, new_fields=fields)


def _removed(key: str, fields: dict) -> RowDiff:
    return RowDiff(key=key, change_type="removed", old_fields=fields, new_fields=None)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_enrich_empty_result():
    result = enrich_diff(_result())
    assert isinstance(result, EnrichResult)
    assert len(result) == 0
    assert result.headers == HEADERS


def test_enrich_modified_row_change_count():
    row = _modified("1", {"name": "Alice", "score": "10"}, {"name": "Alice", "score": "20"})
    result = enrich_diff(_result(row))
    enriched = result.rows[0]
    assert enriched.change_count == 1
    assert enriched.changed_fields == ["score"]


def test_enrich_modified_row_change_ratio():
    row = _modified(
        "2",
        {"name": "Bob", "score": "5"},
        {"name": "Robert", "score": "50"},
    )
    result = enrich_diff(_result(row))
    enriched = result.rows[0]
    assert enriched.change_count == 2
    assert enriched.change_ratio == pytest.approx(1.0)


def test_enrich_added_row_all_fields_changed():
    row = _added("3", {"name": "Carol", "score": "99"})
    result = enrich_diff(_result(row))
    enriched = result.rows[0]
    assert enriched.change_count == 2
    assert enriched.change_ratio == pytest.approx(1.0)
    assert set(enriched.changed_fields) == {"name", "score"}


def test_enrich_removed_row_all_fields_changed():
    row = _removed("4", {"name": "Dan", "score": "0"})
    result = enrich_diff(_result(row))
    enriched = result.rows[0]
    assert enriched.change_count == 2
    assert set(enriched.changed_fields) == {"name", "score"}


def test_enrich_no_ratio_option():
    row = _modified("5", {"name": "Eve", "score": "1"}, {"name": "Eve", "score": "2"})
    opts = EnrichOptions(include_ratio=False)
    result = enrich_diff(_result(row), options=opts)
    enriched = result.rows[0]
    assert enriched.change_ratio == 0.0
    assert enriched.change_count == 1


def test_enrich_no_changed_fields_option():
    row = _modified("6", {"name": "Frank", "score": "3"}, {"name": "Francis", "score": "3"})
    opts = EnrichOptions(include_changed_fields=False)
    result = enrich_diff(_result(row), options=opts)
    enriched = result.rows[0]
    assert enriched.changed_fields == []
    assert enriched.change_count == 1


def test_enrich_as_dict_keys():
    row = _modified("7", {"name": "Gina", "score": "7"}, {"name": "Gina", "score": "77"})
    result = enrich_diff(_result(row))
    d = result.rows[0].as_dict()
    assert set(d.keys()) == {"key", "change_type", "change_count", "change_ratio", "changed_fields"}


def test_enrich_unchanged_modified_row_zero_changes():
    row = _modified("8", {"name": "Hank", "score": "8"}, {"name": "Hank", "score": "8"})
    result = enrich_diff(_result(row))
    enriched = result.rows[0]
    assert enriched.change_count == 0
    assert enriched.change_ratio == pytest.approx(0.0)
    assert enriched.changed_fields == []
