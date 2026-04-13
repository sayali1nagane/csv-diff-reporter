"""Tests for csv_diff_reporter.reporter."""

from io import StringIO

import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.reporter import generate_report


def _make_result(*diffs: RowDiff) -> DiffResult:
    return DiffResult(diffs=list(diffs))


def test_report_no_differences():
    result = _make_result()
    report = generate_report(result)
    assert "No differences found." in report
    assert "0 added, 0 removed, 0 modified" in report


def test_report_added_row():
    diff = RowDiff(key="1", status="added", changes={"name": (None, "Alice")})
    report = generate_report(_make_result(diff))
    assert "[+]" in report
    assert "Row '1' added" in report
    assert "'Alice'" in report
    assert "1 added" in report


def test_report_removed_row():
    diff = RowDiff(key="2", status="removed", changes={"name": ("Bob", None)})
    report = generate_report(_make_result(diff))
    assert "[-]" in report
    assert "Row '2' removed" in report
    assert "'Bob'" in report
    assert "1 removed" in report


def test_report_modified_row():
    diff = RowDiff(
        key="3",
        status="modified",
        changes={"age": ("30", "31")},
    )
    report = generate_report(_make_result(diff))
    assert "[~]" in report
    assert "Row '3' modified" in report
    assert "'30' -> '31'" in report
    assert "1 modified" in report


def test_report_writes_to_file():
    diff = RowDiff(key="1", status="added", changes={"x": (None, "v")})
    buf = StringIO()
    report = generate_report(_make_result(diff), file=buf)
    assert buf.getvalue() == report


def test_report_summary_counts_all_types():
    diffs = [
        RowDiff(key="a", status="added", changes={"c": (None, "1")}),
        RowDiff(key="b", status="removed", changes={"c": ("2", None)}),
        RowDiff(key="c", status="modified", changes={"c": ("3", "4")}),
    ]
    report = generate_report(_make_result(*diffs))
    assert "1 added, 1 removed, 1 modified" in report


def test_report_contains_dividers():
    report = generate_report(_make_result())
    assert report.count("-" * 60) >= 2
