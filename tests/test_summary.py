"""Tests for csv_diff_reporter.summary."""
import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.summary import (
    DiffSummary,
    compute_summary,
    format_summary_text,
)


def _make_result(added=None, removed=None, modified=None, unchanged=None) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        modified=modified or [],
        unchanged=unchanged or [],
    )


def _row(key="k1"):
    return RowDiff(key=key, old={"id": key}, new={"id": key}, changed_fields=[])


def test_compute_summary_empty():
    result = _make_result()
    summary = compute_summary(result, total_rows_old=0, total_rows_new=0)
    assert summary.added == 0
    assert summary.removed == 0
    assert summary.modified == 0
    assert summary.unchanged == 0
    assert summary.change_rate == 0.0


def test_compute_summary_counts():
    result = _make_result(
        added=[_row("a1"), _row("a2")],
        removed=[_row("r1")],
        modified=[_row("m1")],
        unchanged=[_row("u1"), _row("u2"), _row("u3")],
    )
    summary = compute_summary(result, total_rows_old=6, total_rows_new=7)
    assert summary.added == 2
    assert summary.removed == 1
    assert summary.modified == 1
    assert summary.unchanged == 3
    assert summary.total_rows_old == 6
    assert summary.total_rows_new == 7


def test_compute_summary_change_rate():
    result = _make_result(
        added=[_row("a1")],
        removed=[_row("r1")],
        modified=[_row("m1"), _row("m2")],
    )
    summary = compute_summary(result, total_rows_old=8, total_rows_new=9)
    # (1 + 1 + 2) / 8 = 0.5
    assert summary.change_rate == pytest.approx(0.5)


def test_compute_summary_zero_old_rows_no_division_error():
    result = _make_result(added=[_row("a1")])
    summary = compute_summary(result, total_rows_old=0, total_rows_new=1)
    assert summary.change_rate == pytest.approx(1.0)


def test_as_dict_keys():
    result = _make_result(added=[_row()])
    summary = compute_summary(result, total_rows_old=1, total_rows_new=2)
    d = summary.as_dict()
    assert set(d.keys()) == {
        "total_rows_old", "total_rows_new",
        "added", "removed", "modified", "unchanged", "change_rate",
    }


def test_format_summary_text_contains_labels():
    result = _make_result(added=[_row()], removed=[_row("r")])
    summary = compute_summary(result, total_rows_old=5, total_rows_new=5)
    text = format_summary_text(summary)
    assert "Diff Summary" in text
    assert "Added" in text
    assert "Removed" in text
    assert "Change %" in text


def test_format_summary_text_values():
    result = _make_result(modified=[_row("m1"), _row("m2")])
    summary = compute_summary(result, total_rows_old=4, total_rows_new=4)
    text = format_summary_text(summary)
    assert "50.00%" in text
    assert "2" in text
