"""Tests for csv_diff_reporter.diff_formatter_latex."""
from __future__ import annotations

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_formatter_latex import _escape, format_diff_as_latex


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row(
    change_type: str,
    old: dict | None = None,
    new: dict | None = None,
    key: str = "1",
) -> RowDiff:
    return RowDiff(
        key=key,
        change_type=change_type,
        old_fields=old or {},
        new_fields=new or {},
    )


def _make_result(rows: list[RowDiff], headers: list[str] | None = None) -> DiffResult:
    return DiffResult(
        headers=headers or ["id", "name"],
        rows=rows,
    )


# ---------------------------------------------------------------------------
# _escape
# ---------------------------------------------------------------------------

def test_escape_plain_string():
    assert _escape("hello") == "hello"


def test_escape_ampersand():
    assert _escape("a & b") == r"a \& b"


def test_escape_underscore():
    assert _escape("col_name") == r"col\_name"


def test_escape_percent():
    assert _escape("50%") == r"50\%"


def test_escape_backslash():
    assert _escape("a\\b") == r"a\textbackslash{}b"


# ---------------------------------------------------------------------------
# format_diff_as_latex — structure
# ---------------------------------------------------------------------------

def test_format_latex_starts_with_documentclass():
    result = _make_result([])
    latex = format_diff_as_latex(result)
    assert latex.startswith(r"\documentclass{article}")


def test_format_latex_contains_end_document():
    result = _make_result([])
    latex = format_diff_as_latex(result)
    assert r"\end{document}" in latex


def test_format_latex_empty_result_shows_no_differences():
    result = _make_result([])
    latex = format_diff_as_latex(result)
    assert "No differences found." in latex


def test_format_latex_custom_title_appears_in_section():
    result = _make_result([])
    latex = format_diff_as_latex(result, title="My Report")
    assert r"\section*{My Report}" in latex


def test_format_latex_headers_appear_in_table():
    result = _make_result([], headers=["id", "value"])
    latex = format_diff_as_latex(result)
    assert "id" in latex
    assert "value" in latex


def test_format_latex_added_row_uses_diffadded_color():
    row = _row("added", new={"id": "1", "name": "Alice"})
    result = _make_result([row])
    latex = format_diff_as_latex(result)
    assert "diffadded" in latex


def test_format_latex_removed_row_uses_diffremoved_color():
    row = _row("removed", old={"id": "2", "name": "Bob"})
    result = _make_result([row])
    latex = format_diff_as_latex(result)
    assert "diffremoved" in latex


def test_format_latex_modified_row_uses_diffmodified_color():
    row = _row("modified", old={"id": "3", "name": "Old"}, new={"id": "3", "name": "New"})
    result = _make_result([row])
    latex = format_diff_as_latex(result)
    assert "diffmodified" in latex


def test_format_latex_row_field_value_appears_in_output():
    row = _row("added", new={"id": "42", "name": "Zara"})
    result = _make_result([row])
    latex = format_diff_as_latex(result)
    assert "Zara" in latex
    assert "42" in latex


def test_format_latex_special_chars_in_field_are_escaped():
    row = _row("added", new={"id": "1", "name": "A & B"})
    result = _make_result([row])
    latex = format_diff_as_latex(result)
    assert r"A \& B" in latex
    assert "A & B" not in latex.split(r"\& B")[0].split("\n")[-1]  # raw & not in cell
