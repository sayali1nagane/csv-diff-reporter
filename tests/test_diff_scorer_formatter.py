"""Tests for csv_diff_reporter.diff_scorer_formatter."""
import json
import pytest
from csv_diff_reporter.diff_scorer import DiffScore
from csv_diff_reporter.diff_scorer_formatter import format_score


def _score(severity="low", score=8, changed=1, total=10, rate=0.1) -> DiffScore:
    return DiffScore(
        total_rows=total,
        changed_rows=changed,
        change_rate=rate,
        severity=severity,
        score=score,
    )


def test_format_text_contains_severity():
    out = format_score(_score(severity="medium"), fmt="text")
    assert "MEDIUM" in out


def test_format_text_contains_score():
    out = format_score(_score(score=42), fmt="text")
    assert "42/100" in out


def test_format_text_contains_row_counts():
    out = format_score(_score(changed=3, total=30), fmt="text")
    assert "3" in out
    assert "30" in out


def test_format_json_is_valid_json():
    out = format_score(_score(), fmt="json")
    data = json.loads(out)
    assert "severity" in data
    assert "score" in data


def test_format_json_values_match():
    s = _score(severity="high", score=75)
    data = json.loads(format_score(s, fmt="json"))
    assert data["severity"] == "high"
    assert data["score"] == 75


def test_format_text_none_severity_icon():
    out = format_score(_score(severity="none", score=0, changed=0, rate=0.0), fmt="text")
    assert "NONE" in out
    assert "✔" in out
