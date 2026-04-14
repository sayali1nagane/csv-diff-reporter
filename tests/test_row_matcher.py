"""Tests for row_matcher and row_matcher_formatter."""
from __future__ import annotations

import json
from typing import Dict

import pytest

from csv_diff_reporter.differ import RowDiff
from csv_diff_reporter.row_matcher import (
    MatchScore,
    _field_similarity,
    _row_similarity,
    find_best_match,
    match_unmatched_rows,
)
from csv_diff_reporter.row_matcher_formatter import format_match_results, MatchResult


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _added(key: str, row: Dict[str, str]) -> RowDiff:
    return RowDiff(key=key, change_type="added", old_row=None, new_row=row)


def _removed(key: str, row: Dict[str, str]) -> RowDiff:
    return RowDiff(key=key, change_type="removed", old_row=row, new_row=None)


# ---------------------------------------------------------------------------
# _field_similarity
# ---------------------------------------------------------------------------

def test_field_similarity_identical():
    assert _field_similarity("hello", "hello") == 1.0


def test_field_similarity_completely_different():
    score = _field_similarity("abc", "xyz")
    assert score == 0.0


def test_field_similarity_partial():
    score = _field_similarity("abcd", "abce")
    assert 0.0 < score < 1.0


# ---------------------------------------------------------------------------
# _row_similarity
# ---------------------------------------------------------------------------

def test_row_similarity_identical_rows():
    row = {"name": "Alice", "city": "London"}
    score, fields = _row_similarity(row, row)
    assert score == 1.0
    assert set(fields) == {"name", "city"}


def test_row_similarity_no_common_keys():
    score, fields = _row_similarity({"a": "1"}, {"b": "2"})
    assert score == 0.0
    assert fields == {}


# ---------------------------------------------------------------------------
# find_best_match
# ---------------------------------------------------------------------------

def test_find_best_match_returns_none_when_below_threshold():
    candidates = [("r2", {"name": "zzz", "city": "yyy"})]
    result = find_best_match({"name": "Alice", "city": "London"}, candidates, threshold=0.9)
    assert result is None


def test_find_best_match_returns_best_above_threshold():
    candidates = [
        ("r2", {"name": "Alice", "city": "Paris"}),
        ("r3", {"name": "Alice", "city": "London"}),
    ]
    result = find_best_match({"name": "Alice", "city": "London"}, candidates, threshold=0.5)
    assert result is not None
    assert result.key == "r3"
    assert result.score == 1.0


# ---------------------------------------------------------------------------
# match_unmatched_rows
# ---------------------------------------------------------------------------

def test_match_unmatched_rows_skips_modified():
    modified = RowDiff(key="1", change_type="modified",
                       old_row={"name": "A"}, new_row={"name": "B"})
    results = match_unmatched_rows([modified], all_rows={"2": {"name": "A"}})
    assert results == []


def test_match_unmatched_rows_added_row_gets_match():
    diff = _added("99", {"name": "Alice", "city": "London"})
    all_rows = {"1": {"name": "Alice", "city": "London"}}
    results = match_unmatched_rows([diff], all_rows)
    assert len(results) == 1
    assert results[0].has_match
    assert results[0].best_match.key == "1"  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# format_match_results
# ---------------------------------------------------------------------------

def test_format_text_empty():
    out = format_match_results([], fmt="text")
    assert "No unmatched rows" in out


def test_format_json_empty():
    out = format_match_results([], fmt="json")
    assert json.loads(out) == []


def test_format_text_with_no_match():
    diff = _added("5", {"name": "Ghost"})
    result = MatchResult(row_diff=diff, best_match=None)
    out = format_match_results([result], fmt="text")
    assert "ADDED" in out
    assert "No close match" in out


def test_format_json_with_match():
    diff = _removed("3", {"name": "Bob"})
    ms = MatchScore(key="7", score=0.75, fields={"name": ("Bob", "Bobby")})
    result = MatchResult(row_diff=diff, best_match=ms)
    out = format_match_results([result], fmt="json")
    data = json.loads(out)
    assert data[0]["change_type"] == "removed"
    assert data[0]["best_match"]["key"] == "7"
    assert data[0]["best_match"]["score"] == 0.75
