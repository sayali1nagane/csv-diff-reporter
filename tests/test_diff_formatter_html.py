"""Tests for diff_formatter_html."""
import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_formatter_html import format_diff_as_html


def _row(key: str, change_type: str, old: dict, new: dict) -> RowDiff:
    return RowDiff(key=key, change_type=change_type, old_fields=old, new_fields=new)


def _make_result(rows):
    return DiffResult(headers=["name", "value"], rows=rows)


def test_format_html_empty_result_contains_no_differences():
    result = _make_result([])
    html = format_diff_as_html(result)
    assert "No differences found." in html


def test_format_html_empty_result_shows_zero_counts():
    result = _make_result([])
    html = format_diff_as_html(result)
    assert "Added: 0" in html
    assert "Removed: 0" in html
    assert "Modified: 0" in html


def test_format_html_added_row_has_correct_class():
    rows = [_row("1", "added", {}, {"name": "Alice", "value": "10"})]
    html = format_diff_as_html(_make_result(rows))
    assert 'class="diff-added"' in html
    assert "Alice" in html


def test_format_html_removed_row_has_correct_class():
    rows = [_row("2", "removed", {"name": "Bob", "value": "5"}, {})]
    html = format_diff_as_html(_make_result(rows))
    assert 'class="diff-removed"' in html
    assert "Bob" in html


def test_format_html_modified_row_has_correct_class():
    rows = [_row("3", "modified", {"name": "Carol", "value": "1"}, {"name": "Carol", "value": "2"})]
    html = format_diff_as_html(_make_result(rows))
    assert 'class="diff-modified"' in html


def test_format_html_summary_counts_are_correct():
    rows = [
        _row("1", "added", {}, {"name": "A", "value": "1"}),
        _row("2", "added", {}, {"name": "B", "value": "2"}),
        _row("3", "removed", {"name": "C", "value": "3"}, {}),
    ]
    html = format_diff_as_html(_make_result(rows))
    assert "Added: 2" in html
    assert "Removed: 1" in html
    assert "Modified: 0" in html


def test_format_html_custom_title_appears():
    result = _make_result([])
    html = format_diff_as_html(result, title="My Report")
    assert "My Report" in html


def test_format_html_headers_appear_in_table():
    result = _make_result([])
    html = format_diff_as_html(result)
    assert "<th>name</th>" in html
    assert "<th>value</th>" in html


def test_format_html_escapes_special_characters():
    rows = [_row("<key>", "added", {}, {"name": "<script>", "value": "x"})]
    html = format_diff_as_html(_make_result(rows))
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
