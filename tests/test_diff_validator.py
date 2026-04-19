import pytest
from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_validator import (
    ThresholdOptions, ThresholdResult, ThresholdViolation, validate_thresholds,
)
from csv_diff_reporter.diff_validator_formatter import format_threshold_result


def _row(change_type: str, key: str = "k") -> RowDiff:
    return RowDiff(key=key, change_type=change_type, old_fields={}, new_fields={})


def _result(*change_types: str) -> DiffResult:
    rows = [_row(ct, key=str(i)) for i, ct in enumerate(change_types)]
    return DiffResult(headers=[], rows=rows)


def test_validate_empty_result_passes():
    opts = ThresholdOptions(max_added=0, max_removed=0)
    r = validate_thresholds(_result(), opts)
    assert r.is_valid()
    assert r.violations == []


def test_validate_added_within_limit():
    opts = ThresholdOptions(max_added=3)
    r = validate_thresholds(_result("added", "added"), opts)
    assert r.is_valid()


def test_validate_added_exceeds_limit():
    opts = ThresholdOptions(max_added=1)
    r = validate_thresholds(_result("added", "added", "added"), opts)
    assert not r.is_valid()
    assert any(v.rule == "max_added" for v in r.violations)


def test_validate_removed_exceeds_limit():
    opts = ThresholdOptions(max_removed=0)
    r = validate_thresholds(_result("removed"), opts)
    assert not r.is_valid()
    assert r.violations[0].rule == "max_removed"
    assert r.violations[0].actual == 1


def test_validate_modified_exceeds_limit():
    opts = ThresholdOptions(max_modified=1)
    r = validate_thresholds(_result("modified", "modified"), opts)
    assert not r.is_valid()


def test_validate_change_rate_passes():
    opts = ThresholdOptions(max_change_rate=0.5)
    r = validate_thresholds(_result("added", "unchanged", "unchanged", "unchanged"), opts)
    assert r.is_valid()


def test_validate_change_rate_fails():
    opts = ThresholdOptions(max_change_rate=0.1)
    r = validate_thresholds(_result("added", "removed", "modified"), opts)
    assert not r.is_valid()
    assert any(v.rule == "max_change_rate" for v in r.violations)


def test_multiple_violations():
    opts = ThresholdOptions(max_added=0, max_removed=0)
    r = validate_thresholds(_result("added", "removed"), opts)
    assert len(r.violations) == 2


def test_violation_as_dict():
    v = ThresholdViolation(rule="max_added", limit=1, actual=3)
    d = v.as_dict()
    assert d == {"rule": "max_added", "limit": 1, "actual": 3}


def test_format_text_passed():
    r = ThresholdResult()
    assert "passed" in format_threshold_result(r, fmt="text").lower()


def test_format_text_failed():
    r = ThresholdResult(violations=[ThresholdViolation("max_added", 1, 5)])
    out = format_threshold_result(r, fmt="text")
    assert "FAILED" in out
    assert "max_added" in out


def test_format_json_valid():
    import json
    r = ThresholdResult(violations=[ThresholdViolation("max_removed", 0, 2)])
    data = json.loads(format_threshold_result(r, fmt="json"))
    assert data["passed"] is False
    assert data["violations"][0]["rule"] == "max_removed"
