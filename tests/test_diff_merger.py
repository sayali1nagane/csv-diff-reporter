"""Tests for csv_diff_reporter.diff_merger and cli_merge helpers."""
from __future__ import annotations

import argparse

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_merger import MergeOptions, merge_diffs
from csv_diff_reporter.cli_merge import (
    add_merge_args,
    apply_merge,
    build_merge_options,
    render_merge_notice,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row(key: str, change_type: str = "added") -> RowDiff:
    new = {"id": key, "val": "x"}
    old = {"id": key, "val": "y"} if change_type == "modified" else None
    if change_type == "removed":
        new, old = None, {"id": key, "val": "y"}
    return RowDiff(key=key, change_type=change_type, old_row=old, new_row=new)


def _result(*rows: RowDiff, headers=None) -> DiffResult:
    return DiffResult(rows=list(rows), headers=headers or ["id", "val"])


# ---------------------------------------------------------------------------
# merge_diffs
# ---------------------------------------------------------------------------

def test_merge_empty_diffs_produces_empty_result():
    r = merge_diffs(_result(), _result())
    assert r.result.rows == []
    assert r.duplicate_keys == []


def test_merge_combines_rows_from_both_diffs():
    a = _result(_row("1"), _row("2"))
    b = _result(_row("3"))
    r = merge_diffs(a, b)
    keys = [row.key for row in r.result.rows]
    assert keys == ["1", "2", "3"]


def test_merge_deduplicates_by_default():
    a = _result(_row("1"), _row("2"))
    b = _result(_row("2"), _row("3"))  # key "2" appears in both
    r = merge_diffs(a, b)
    keys = [row.key for row in r.result.rows]
    assert keys == ["1", "2", "3"]
    assert r.duplicate_keys == ["2"]


def test_merge_no_dedup_keeps_duplicates():
    a = _result(_row("1"))
    b = _result(_row("1"), _row("2"))
    opts = MergeOptions(deduplicate=False)
    r = merge_diffs(a, b, opts)
    keys = [row.key for row in r.result.rows]
    assert keys == ["1", "1", "2"]
    assert r.duplicate_keys == []


def test_merge_tag_source_adds_field():
    a = _result(_row("1"))
    b = _result(_row("2"))
    opts = MergeOptions(tag_source=True, source_a_label="primary", source_b_label="secondary")
    r = merge_diffs(a, b, opts)
    rows = r.result.rows
    assert rows[0].new_row["__source__"] == "primary"
    assert rows[1].new_row["__source__"] == "secondary"


def test_merge_headers_are_union_of_both():
    a = _result(_row("1"), headers=["id", "name"])
    b = _result(_row("2"), headers=["id", "score"])
    r = merge_diffs(a, b)
    assert "id" in r.result.headers
    assert "name" in r.result.headers
    assert "score" in r.result.headers


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "merge_no_dedup": False,
        "merge_tag_source": False,
        "merge_source_a_label": "a",
        "merge_source_b_label": "b",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_add_merge_args_registers_flags():
    parser = argparse.ArgumentParser()
    add_merge_args(parser)
    args = parser.parse_args([])
    assert hasattr(args, "merge_diff_file")
    assert hasattr(args, "merge_no_dedup")
    assert hasattr(args, "merge_tag_source")


def test_build_merge_options_defaults():
    opts = build_merge_options(_make_args())
    assert opts.deduplicate is True
    assert opts.tag_source is False


def test_build_merge_options_no_dedup_flag():
    opts = build_merge_options(_make_args(merge_no_dedup=True))
    assert opts.deduplicate is False


def test_apply_merge_returns_merged_diff_and_keys():
    primary = _result(_row("1"))
    secondary = _result(_row("1"), _row("2"))
    merged, dupes = apply_merge(primary, secondary, _make_args())
    assert len(merged.rows) == 2
    assert "1" in dupes


def test_render_merge_notice_empty():
    assert render_merge_notice([]) == ""


def test_render_merge_notice_with_keys():
    notice = render_merge_notice(["k1", "k2"])
    assert "2" in notice
    assert "k1" in notice
