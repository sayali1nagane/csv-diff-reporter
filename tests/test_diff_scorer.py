"""Tests for csv_diff_reporter.diff_scorer."""
import pytest
from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_scorer import score_diff, _severity


def _row(key: str, change_type: str) -> RowDiff:
    return RowDiff(key=key, change_type=change_type, fields={})


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id"], rows=list(rows))


def test_score_empty_result():
    r = _result()
    s = score_diff(r)
    assert s.total_rows == 0
    assert s.changed_rows == 0
    assert s.change_rate == 0.0
    assert s.severity == "none"
    assert s.score == 0


def test_score_all_unchanged():
    r = _result(_row("1", "unchanged"), _row("2", "unchanged"))
    s = score_diff(r)
    assert s.changed_rows == 0
    assert s.severity == "none"


def test_score_all_changed():
    r = _result(_row("1", "added"), _row("2", "removed"), _row("3", "modified"))
    s = score_diff(r)
    assert s.changed_rows == 3
    assert s.total_rows == 3
    assert s.change_rate == 1.0
    assert s.score == 100
    assert s.severity == "high"


def test_score_partial_changes():
    rows = [_row(str(i), "modified") for i in range(2)] + \
           [_row(str(i + 10), "unchanged") for i in range(8)]
    r = _result(*rows)
    s = score_diff(r)
    assert s.changed_rows == 2
    assert s.total_rows == 10
    assert s.severity == "low"


def test_severity_boundaries():
    assert _severity(0.0) == "none"
    assert _severity(0.05) == "low"
    assert _severity(0.1) == "medium"
    assert _severity(0.39) == "medium"
    assert _severity(0.4) == "high"
    assert _severity(1.0) == "high"


def test_as_dict_keys():
    r = _result(_row("1", "added"))
    d = score_diff(r).as_dict()
    assert set(d.keys()) == {"total_rows", "changed_rows", "change_rate", "severity", "score"}
