"""Tests for csv_diff_reporter.diff_tagger_formatter."""
from __future__ import annotations

import json

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_tagger import TagOptions, TagRule, tag_diff
from csv_diff_reporter.diff_tagger_formatter import format_tagged


def _row(key: str, change_type: str) -> RowDiff:
    return RowDiff(
        key=key,
        change_type=change_type,
        old_fields={"col": "old"} if change_type != "added" else {},
        new_fields={"col": "new"} if change_type != "removed" else {},
    )


def _make_result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id", "col"], rows=list(rows))


def test_format_text_empty_result():
    result = _make_result()
    tagged = tag_diff(result)
    output = format_tagged(tagged, fmt="text")
    assert output == "No tagged rows."


def test_format_text_shows_change_type_and_key():
    result = _make_result(_row("42", "added"))
    tagged = tag_diff(result)
    output = format_tagged(tagged, fmt="text")
    assert "ADDED" in output
    assert "42" in output


def test_format_text_shows_tags():
    options = TagOptions(rules=[
        TagRule(tag="fresh", predicate=lambda r: r.change_type == "added"),
    ])
    result = _make_result(_row("1", "added"))
    tagged = tag_diff(result, options)
    output = format_tagged(tagged, fmt="text")
    assert "fresh" in output


def test_format_text_no_tags_shows_none_label():
    result = _make_result(_row("1", "modified"))
    tagged = tag_diff(result)
    output = format_tagged(tagged, fmt="text")
    assert "(none)" in output


def test_format_json_empty_result():
    result = _make_result()
    tagged = tag_diff(result)
    output = format_tagged(tagged, fmt="json")
    data = json.loads(output)
    assert data["rows"] == []
    assert data["headers"] == ["id", "col"]
    assert data["all_tags"] == []


def test_format_json_contains_row_data():
    options = TagOptions(rules=[
        TagRule(tag="gone", predicate=lambda r: r.change_type == "removed"),
    ])
    result = _make_result(_row("7", "removed"))
    tagged = tag_diff(result, options)
    output = format_tagged(tagged, fmt="json")
    data = json.loads(output)
    assert len(data["rows"]) == 1
    row = data["rows"][0]
    assert row["key"] == "7"
    assert row["change_type"] == "removed"
    assert "gone" in row["tags"]


def test_format_json_all_tags_populated():
    options = TagOptions(rules=[
        TagRule(tag="a", predicate=lambda r: r.change_type == "added"),
        TagRule(tag="b", predicate=lambda r: r.change_type == "removed"),
    ])
    result = _make_result(_row("1", "added"), _row("2", "removed"))
    tagged = tag_diff(result, options)
    data = json.loads(format_tagged(tagged, fmt="json"))
    assert data["all_tags"] == ["a", "b"]


def test_format_defaults_to_text():
    result = _make_result(_row("1", "modified"))
    tagged = tag_diff(result)
    output = format_tagged(tagged)
    assert "MODIFIED" in output
