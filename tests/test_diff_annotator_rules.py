"""Tests for diff_annotator_rules and its formatter."""
import json
import pytest
from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_annotator_rules import (
    RuleOptions, apply_rules, RuleResult,
)
from csv_diff_reporter.diff_annotator_rules_formatter import format_rule_result


def _row(key, change_type, old=None, new=None):
    return RowDiff(key=key, change_type=change_type, old_fields=old or {}, new_fields=new or {})


def _result(*rows):
    return DiffResult(rows=list(rows), headers=["id", "name", "value"])


def test_apply_rules_empty_result():
    r = apply_rules(_result())
    assert r.total_checked == 0
    assert not r.has_violations


def test_apply_rules_no_options_no_violations():
    row = _row("1", "added", new={"id": "1", "name": "Alice"})
    r = apply_rules(_result(row))
    assert r.total_checked == 1
    assert not r.has_violations


def test_flag_empty_fields_detects_blank_value():
    row = _row("2", "modified", new={"id": "2", "name": ""})
    opts = RuleOptions(flag_empty_fields=True)
    r = apply_rules(_result(row), opts)
    assert r.has_violations
    assert any(m.rule_name == "empty_field" for m in r.matches)


def test_flag_empty_fields_ignores_non_empty():
    row = _row("3", "added", new={"id": "3", "name": "Bob"})
    opts = RuleOptions(flag_empty_fields=True)
    r = apply_rules(_result(row), opts)
    assert not r.has_violations


def test_required_columns_missing_triggers_violation():
    row = _row("4", "added", new={"id": "4"})
    opts = RuleOptions(required_columns=["name"])
    r = apply_rules(_result(row), opts)
    assert r.has_violations
    assert r.matches[0].rule_name == "missing_required_column"
    assert r.matches[0].row_key == "4"


def test_required_columns_present_no_violation():
    row = _row("5", "added", new={"id": "5", "name": "Carol"})
    opts = RuleOptions(required_columns=["name"])
    r = apply_rules(_result(row), opts)
    assert not r.has_violations


def test_forbidden_columns_present_triggers_violation():
    row = _row("6", "added", new={"id": "6", "secret": "x"})
    opts = RuleOptions(forbidden_columns=["secret"])
    r = apply_rules(_result(row), opts)
    assert r.has_violations
    assert r.matches[0].rule_name == "forbidden_column_present"


def test_forbidden_columns_absent_no_violation():
    row = _row("7", "added", new={"id": "7", "name": "Dave"})
    opts = RuleOptions(forbidden_columns=["secret"])
    r = apply_rules(_result(row), opts)
    assert not r.has_violations


def test_format_text_no_violations():
    r = RuleResult(total_checked=3)
    out = format_rule_result(r)
    assert "No violations" in out
    assert "3 rows checked" in out


def test_format_text_with_violations():
    from csv_diff_reporter.diff_annotator_rules import RuleMatch
    r = RuleResult(total_checked=1, matches=[
        RuleMatch(rule_name="empty_field", message="Col empty", row_key="1", change_type="added")
    ])
    out = format_rule_result(r)
    assert "empty_field" in out
    assert "key=1" in out


def test_format_json_is_valid():
    from csv_diff_reporter.diff_annotator_rules import RuleMatch
    r = RuleResult(total_checked=2, matches=[
        RuleMatch(rule_name="missing_required_column", message="x", row_key="k", change_type="modified")
    ])
    out = format_rule_result(r, fmt="json")
    data = json.loads(out)
    assert data["total_checked"] == 2
    assert data["violations"] == 1
    assert data["matches"][0]["rule"] == "missing_required_column"
