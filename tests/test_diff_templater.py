"""Tests for csv_diff_reporter.diff_templater."""
import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_templater import TemplateOptions, render_template, list_variables


def _row(key: str, change: str, old=None, new=None) -> RowDiff:
    old = old or {}
    new = new or {}
    return RowDiff(key=key, change_type=change, old_fields=old, new_fields=new)


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id", "name"], rows=list(rows))


def test_render_empty_template():
    result = _result()
    opts = TemplateOptions(template="")
    assert render_template(result, opts) == ""


def test_render_no_variables():
    result = _result()
    opts = TemplateOptions(template="No changes today.")
    assert render_template(result, opts) == "No changes today."


def test_render_added_count():
    result = _result(_row("1", "added", new={"id": "1", "name": "Alice"}))
    opts = TemplateOptions(template="Added: {{ added }}")
    assert render_template(result, opts) == "Added: 1"


def test_render_multiple_variables():
    result = _result(
        _row("1", "added", new={"id": "1", "name": "Alice"}),
        _row("2", "removed", old={"id": "2", "name": "Bob"}),
        _row("3", "modified", old={"id": "3", "name": "C"}, new={"id": "3", "name": "D"}),
    )
    opts = TemplateOptions(template="+{{ added }} -{{ removed }} ~{{ modified }}")
    assert render_template(result, opts) == "+1 -1 ~1"


def test_render_total_changes():
    result = _result(
        _row("1", "added", new={"id": "1", "name": "A"}),
        _row("2", "added", new={"id": "2", "name": "B"}),
    )
    opts = TemplateOptions(template="Total: {{ total_changes }}")
    assert render_template(result, opts) == "Total: 2"


def test_render_unknown_variable_uses_missing():
    result = _result()
    opts = TemplateOptions(template="{{ unknown_var }}", missing="N/A")
    assert render_template(result, opts) == "N/A"


def test_render_headers():
    result = _result()
    opts = TemplateOptions(template="Cols: {{ headers }}")
    assert render_template(result, opts) == "Cols: id, name"


def test_render_change_rate_format():
    result = _result(_row("1", "added", new={"id": "1", "name": "A"}))
    opts = TemplateOptions(template="{{ change_rate }}")
    rendered = render_template(result, opts)
    float(rendered)  # should be parseable as float


def test_list_variables_returns_list():
    variables = list_variables()
    assert isinstance(variables, list)
    assert "added" in variables
    assert "removed" in variables
    assert "total_changes" in variables
