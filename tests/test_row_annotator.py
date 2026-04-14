"""Tests for csv_diff_reporter.row_annotator."""
import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.row_annotator import (
    AnnotatedResult,
    annotate_diff,
    _label,
    _note,
    _severity,
)


def _make_result(*rows: RowDiff) -> DiffResult:
    return DiffResult(rows=list(rows), headers=[])


def _modified(key: str, diff: dict) -> RowDiff:
    return RowDiff(key=key, change_type="modified", diff=diff)


def _added(key: str) -> RowDiff:
    return RowDiff(key=key, change_type="added", diff={})


def _removed(key: str) -> RowDiff:
    return RowDiff(key=key, change_type="removed", diff={})


def test_annotate_empty_result():
    result = annotate_diff(_make_result())
    assert isinstance(result, AnnotatedResult)
    assert result.rows == []


def test_annotate_added_row_label_and_severity():
    result = annotate_diff(_make_result(_added("r1")))
    ar = result.rows[0]
    assert ar.label == "Row Added"
    assert ar.severity == "info"
    assert ar.note is None


def test_annotate_removed_row_label_and_severity():
    result = annotate_diff(_make_result(_removed("r1")))
    ar = result.rows[0]
    assert ar.label == "Row Removed"
    assert ar.severity == "warning"


def test_annotate_modified_row_label_and_severity():
    row = _modified("r1", {"col": ("a", "b")})
    result = annotate_diff(_make_result(row))
    ar = result.rows[0]
    assert ar.label == "Row Modified"
    assert ar.severity == "critical"


def test_annotate_modified_row_note_lists_columns():
    diff = {"name": ("Alice", "Bob"), "age": ("30", "31")}
    row = _modified("r1", diff)
    result = annotate_diff(_make_result(row))
    ar = result.rows[0]
    assert ar.note is not None
    assert "name" in ar.note or "age" in ar.note


def test_annotate_note_truncates_beyond_three_columns():
    diff = {f"col{i}": ("x", "y") for i in range(5)}
    row = _modified("r1", diff)
    result = annotate_diff(_make_result(row))
    ar = result.rows[0]
    assert "+2 more" in (ar.note or "")


def test_annotate_preserves_source():
    dr = _make_result(_added("r1"))
    result = annotate_diff(dr)
    assert result.source is dr


def test_severity_unknown_type_defaults_to_info():
    assert _severity("unknown") == "info"


def test_label_unknown_type_title_cases():
    assert _label("merged") == "Merged"


def test_note_returns_none_for_non_modified():
    row = _added("r1")
    assert _note(row) is None
