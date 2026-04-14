"""Tests for csv_diff_reporter.row_annotator_formatter."""
import json

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.row_annotator import AnnotatedResult, annotate_diff
from csv_diff_reporter.row_annotator_formatter import format_annotated


def _make_result(*rows: RowDiff) -> DiffResult:
    return DiffResult(rows=list(rows), headers=[])


def _modified(key: str, diff: dict) -> RowDiff:
    return RowDiff(key=key, change_type="modified", diff=diff)


def _added(key: str) -> RowDiff:
    return RowDiff(key=key, change_type="added", diff={})


def _removed(key: str) -> RowDiff:
    return RowDiff(key=key, change_type="removed", diff={})


def _annotated(*rows: RowDiff) -> AnnotatedResult:
    return annotate_diff(_make_result(*rows))


def test_format_text_empty():
    out = format_annotated(_annotated())
    assert "No annotated changes" in out


def test_format_text_added_contains_label():
    out = format_annotated(_annotated(_added("r1")))
    assert "Row Added" in out
    assert "r1" in out


def test_format_text_severity_icon_present():
    out = format_annotated(_annotated(_removed("r2")))
    assert "WARNING" in out


def test_format_text_note_included():
    diff = {"col": ("a", "b")}
    out = format_annotated(_annotated(_modified("r1", diff)))
    assert "Changed columns" in out
    assert "col" in out


def test_format_json_empty():
    out = format_annotated(_annotated(), fmt="json")
    parsed = json.loads(out)
    assert parsed == []


def test_format_json_added_row_structure():
    out = format_annotated(_annotated(_added("r1")), fmt="json")
    parsed = json.loads(out)
    assert len(parsed) == 1
    assert parsed[0]["key"] == "r1"
    assert parsed[0]["change_type"] == "added"
    assert parsed[0]["severity"] == "info"


def test_format_json_modified_row_has_diff():
    diff = {"name": ("Alice", "Bob")}
    out = format_annotated(_annotated(_modified("r1", diff)), fmt="json")
    parsed = json.loads(out)
    assert "diff" in parsed[0]
    assert parsed[0]["diff"]["name"] == {"old": "Alice", "new": "Bob"}


def test_format_json_note_absent_when_no_diff():
    out = format_annotated(_annotated(_added("r1")), fmt="json")
    parsed = json.loads(out)
    assert "note" not in parsed[0]
