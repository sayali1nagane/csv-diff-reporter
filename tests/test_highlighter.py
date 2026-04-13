"""Tests for csv_diff_reporter.highlighter."""
import pytest
from csv_diff_reporter.differ import RowDiff
from csv_diff_reporter.highlighter import (
    FieldHighlight,
    HighlightedRow,
    highlight_row,
    highlight_diff,
    format_highlighted_row,
)


def _modified(key="1", old=None, new=None) -> RowDiff:
    return RowDiff(
        key=key,
        change_type="modified",
        old_row=old or {"a": "x", "b": "y"},
        new_row=new or {"a": "x", "b": "z"},
    )


def _added(key="2") -> RowDiff:
    return RowDiff(key=key, change_type="added", old_row=None, new_row={"a": "1", "b": "2"})


def _removed(key="3") -> RowDiff:
    return RowDiff(key=key, change_type="removed", old_row={"a": "9", "b": "8"}, new_row=None)


def test_highlight_modified_marks_changed_field():
    hr = highlight_row(_modified())
    assert hr.change_type == "modified"
    assert hr.key == "1"
    changed = {h.column: h for h in hr.highlights if h.is_changed}
    assert "b" in changed
    assert changed["b"].old_value == "y"
    assert changed["b"].new_value == "z"


def test_highlight_modified_unchanged_field_not_in_changed_columns():
    hr = highlight_row(_modified())
    assert "a" not in hr.changed_columns
    assert "b" in hr.changed_columns


def test_highlight_added_all_fields_have_no_old_value():
    hr = highlight_row(_added())
    assert hr.change_type == "added"
    for h in hr.highlights:
        assert h.old_value is None
        assert h.new_value is not None


def test_highlight_removed_all_fields_have_no_new_value():
    hr = highlight_row(_removed())
    assert hr.change_type == "removed"
    for h in hr.highlights:
        assert h.new_value is None
        assert h.old_value is not None


def test_highlight_diff_returns_list_of_highlighted_rows():
    rows = [_modified(), _added(), _removed()]
    result = highlight_diff(rows)
    assert len(result) == 3
    assert all(isinstance(r, HighlightedRow) for r in result)


def test_highlight_diff_empty():
    assert highlight_diff([]) == []


def test_format_highlighted_row_contains_key():
    hr = highlight_row(_modified())
    text = format_highlighted_row(hr)
    assert "key=1" in text
    assert "MODIFIED" in text


def test_format_highlighted_row_shows_change_arrow():
    hr = highlight_row(_modified())
    text = format_highlighted_row(hr)
    assert "->" in text


def test_field_highlight_is_changed_false_when_equal():
    fh = FieldHighlight(column="x", old_value="same", new_value="same")
    assert not fh.is_changed


def test_field_highlight_is_changed_true_when_different():
    fh = FieldHighlight(column="x", old_value="a", new_value="b")
    assert fh.is_changed
