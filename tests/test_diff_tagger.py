"""Tests for csv_diff_reporter.diff_tagger."""
from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_tagger import (
    TagOptions,
    TagRule,
    TaggedResult,
    tag_diff,
)


def _row(key: str, change_type: str) -> RowDiff:
    return RowDiff(
        key=key,
        change_type=change_type,
        old_fields={"name": "Alice"} if change_type != "added" else {},
        new_fields={"name": "Bob"} if change_type != "removed" else {},
    )


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id", "name"], rows=list(rows))


def test_tag_diff_no_options_returns_untagged_rows():
    result = _result(_row("1", "added"), _row("2", "removed"))
    tagged = tag_diff(result)
    assert len(tagged.rows) == 2
    assert all(r.tags == [] for r in tagged.rows)


def test_tag_diff_preserves_headers():
    result = _result(_row("1", "added"))
    tagged = tag_diff(result)
    assert tagged.headers == ["id", "name"]


def test_tag_diff_applies_single_rule():
    options = TagOptions(rules=[
        TagRule(tag="new", predicate=lambda r: r.change_type == "added"),
    ])
    result = _result(_row("1", "added"), _row("2", "removed"))
    tagged = tag_diff(result, options)
    assert tagged.rows[0].tags == ["new"]
    assert tagged.rows[1].tags == []


def test_tag_diff_multiple_rules_can_match_same_row():
    options = TagOptions(rules=[
        TagRule(tag="changed", predicate=lambda r: r.change_type in ("added", "modified")),
        TagRule(tag="new", predicate=lambda r: r.change_type == "added"),
    ])
    result = _result(_row("1", "added"))
    tagged = tag_diff(result, options)
    assert set(tagged.rows[0].tags) == {"changed", "new"}


def test_tagged_result_with_tag_filters_correctly():
    options = TagOptions(rules=[
        TagRule(tag="gone", predicate=lambda r: r.change_type == "removed"),
    ])
    result = _result(_row("1", "added"), _row("2", "removed"), _row("3", "modified"))
    tagged = tag_diff(result, options)
    gone = tagged.with_tag("gone")
    assert len(gone) == 1
    assert gone[0].row.key == "2"


def test_tagged_result_all_tags_sorted():
    options = TagOptions(rules=[
        TagRule(tag="zebra", predicate=lambda r: r.change_type == "added"),
        TagRule(tag="alpha", predicate=lambda r: r.change_type == "removed"),
    ])
    result = _result(_row("1", "added"), _row("2", "removed"))
    tagged = tag_diff(result, options)
    assert tagged.all_tags() == ["alpha", "zebra"]


def test_tagged_row_has_tag():
    options = TagOptions(rules=[
        TagRule(tag="x", predicate=lambda r: True),
    ])
    result = _result(_row("1", "modified"))
    tagged = tag_diff(result, options)
    assert tagged.rows[0].has_tag("x")
    assert not tagged.rows[0].has_tag("y")


def test_tag_diff_empty_result():
    result = _result()
    tagged = tag_diff(result)
    assert tagged.rows == []
    assert tagged.all_tags() == []
