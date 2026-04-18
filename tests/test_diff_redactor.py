"""Tests for csv_diff_reporter.diff_redactor."""
import pytest
from csv_diff_reporter.diff_redactor import RedactOptions, redact_diff
from csv_diff_reporter.differ import DiffResult, RowDiff


def _row(key, change_type, old=None, new=None):
    return RowDiff(key=key, change_type=change_type, old_fields=old, new_fields=new)


def _result(*rows):
    return DiffResult(headers=["id", "name", "email"], rows=list(rows))


def test_redact_no_options_returns_same_object():
    r = _result(_row("1", "added", new={"id": "1", "name": "Alice", "email": "a@b.com"}))
    assert redact_diff(r) is r


def test_redact_empty_columns_returns_same_object():
    r = _result(_row("1", "added", new={"id": "1", "name": "Alice", "email": "a@b.com"}))
    opts = RedactOptions(columns=frozenset())
    assert redact_diff(r, opts) is r


def test_redact_masks_new_fields_for_added_row():
    r = _result(_row("1", "added", new={"id": "1", "name": "Alice", "email": "a@b.com"}))
    opts = RedactOptions(columns=frozenset(["email"]))
    out = redact_diff(r, opts)
    assert out.rows[0].new_fields["email"] == "***"
    assert out.rows[0].new_fields["name"] == "Alice"


def test_redact_masks_old_fields_for_removed_row():
    r = _result(_row("1", "removed", old={"id": "1", "name": "Bob", "email": "b@c.com"}))
    opts = RedactOptions(columns=frozenset(["email"]))
    out = redact_diff(r, opts)
    assert out.rows[0].old_fields["email"] == "***"
    assert out.rows[0].new_fields is None


def test_redact_masks_both_fields_for_modified_row():
    r = _result(_row("1", "modified",
                     old={"id": "1", "name": "Bob", "email": "old@x.com"},
                     new={"id": "1", "name": "Bob", "email": "new@x.com"}))
    opts = RedactOptions(columns=frozenset(["email"]))
    out = redact_diff(r, opts)
    assert out.rows[0].old_fields["email"] == "***"
    assert out.rows[0].new_fields["email"] == "***"


def test_redact_custom_mask():
    r = _result(_row("1", "added", new={"id": "1", "name": "Alice", "email": "a@b.com"}))
    opts = RedactOptions(columns=frozenset(["email"]), mask="[REDACTED]")
    out = redact_diff(r, opts)
    assert out.rows[0].new_fields["email"] == "[REDACTED]"


def test_redact_preserves_headers():
    r = _result(_row("1", "added", new={"id": "1", "name": "Alice", "email": "a@b.com"}))
    opts = RedactOptions(columns=frozenset(["email"]))
    out = redact_diff(r, opts)
    assert out.headers == ["id", "name", "email"]


def test_redact_multiple_columns():
    r = _result(_row("1", "added", new={"id": "1", "name": "Alice", "email": "a@b.com"}))
    opts = RedactOptions(columns=frozenset(["name", "email"]))
    out = redact_diff(r, opts)
    assert out.rows[0].new_fields["name"] == "***"
    assert out.rows[0].new_fields["email"] == "***"
    assert out.rows[0].new_fields["id"] == "1"
