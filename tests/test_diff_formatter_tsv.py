"""Tests for csv_diff_reporter.diff_formatter_tsv."""
from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_formatter_tsv import format_diff_as_tsv


def _row(
    key: str,
    change_type: str,
    old_fields: dict | None = None,
    new_fields: dict | None = None,
) -> RowDiff:
    return RowDiff(
        key=key,
        change_type=change_type,
        old_fields=old_fields,
        new_fields=new_fields,
    )


def _make_result(
    added=None, removed=None, modified=None, headers=("name", "score")
) -> DiffResult:
    return DiffResult(
        headers=list(headers),
        added=added or [],
        removed=removed or [],
        modified=modified or [],
    )


def _parse(tsv: str) -> list[list[str]]:
    lines = tsv.rstrip("\n").splitlines()
    return [line.split("\t") for line in lines]


# ---------------------------------------------------------------------------
# Empty result
# ---------------------------------------------------------------------------

def test_format_tsv_empty_result_has_header_only():
    result = _make_result()
    tsv = format_diff_as_tsv(result)
    rows = _parse(tsv)
    assert len(rows) == 1


def test_format_tsv_header_columns():
    result = _make_result()
    rows = _parse(format_diff_as_tsv(result))
    assert rows[0] == ["_key", "_change_type", "name", "score"]


# ---------------------------------------------------------------------------
# Added row
# ---------------------------------------------------------------------------

def test_format_tsv_added_row_change_type():
    r = _row("r1", "added", new_fields={"name": "Alice", "score": "10"})
    result = _make_result(added=[r])
    rows = _parse(format_diff_as_tsv(result))
    assert rows[1][1] == "added"


def test_format_tsv_added_row_key():
    r = _row("r1", "added", new_fields={"name": "Alice", "score": "10"})
    result = _make_result(added=[r])
    rows = _parse(format_diff_as_tsv(result))
    assert rows[1][0] == "r1"


def test_format_tsv_added_row_field_values():
    r = _row("r1", "added", new_fields={"name": "Alice", "score": "10"})
    result = _make_result(added=[r])
    rows = _parse(format_diff_as_tsv(result))
    assert rows[1][2] == "Alice"
    assert rows[1][3] == "10"


# ---------------------------------------------------------------------------
# Removed row
# ---------------------------------------------------------------------------

def test_format_tsv_removed_row_change_type():
    r = _row("r2", "removed", old_fields={"name": "Bob", "score": "5"})
    result = _make_result(removed=[r])
    rows = _parse(format_diff_as_tsv(result))
    assert rows[1][1] == "removed"


def test_format_tsv_removed_row_uses_old_fields():
    r = _row("r2", "removed", old_fields={"name": "Bob", "score": "5"})
    result = _make_result(removed=[r])
    rows = _parse(format_diff_as_tsv(result))
    assert rows[1][2] == "Bob"


# ---------------------------------------------------------------------------
# Modified row
# ---------------------------------------------------------------------------

def test_format_tsv_modified_row_change_type():
    r = _row(
        "r3",
        "modified",
        old_fields={"name": "Carol", "score": "7"},
        new_fields={"name": "Carol", "score": "9"},
    )
    result = _make_result(modified=[r])
    rows = _parse(format_diff_as_tsv(result))
    assert rows[1][1] == "modified"


def test_format_tsv_modified_row_uses_new_fields():
    r = _row(
        "r3",
        "modified",
        old_fields={"name": "Carol", "score": "7"},
        new_fields={"name": "Carol", "score": "9"},
    )
    result = _make_result(modified=[r])
    rows = _parse(format_diff_as_tsv(result))
    assert rows[1][3] == "9"


# ---------------------------------------------------------------------------
# Escaping
# ---------------------------------------------------------------------------

def test_format_tsv_escapes_tab_in_value():
    r = _row("r4", "added", new_fields={"name": "Al\tice", "score": "1"})
    result = _make_result(added=[r])
    tsv = format_diff_as_tsv(result)
    assert "\\t" in tsv
    assert "\t\t" not in tsv  # no raw unescaped double-tab from the value


def test_format_tsv_missing_field_defaults_to_empty_string():
    r = _row("r5", "added", new_fields={"name": "Dave"})  # 'score' missing
    result = _make_result(added=[r])
    rows = _parse(format_diff_as_tsv(result))
    assert rows[1][3] == ""
