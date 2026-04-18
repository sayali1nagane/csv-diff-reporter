"""Tests for csv_diff_reporter.diff_sampler."""
import pytest

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_sampler import (
    SampleOptions,
    format_sample_notice,
    sample_diff,
)


def _row(key: str, old=None, new=None) -> RowDiff:
    return RowDiff(key=key, old=old, new=new)


def _result(*rows: RowDiff) -> DiffResult:
    return DiffResult(headers=["id", "value"], rows=list(rows))


_added = _row("a", old=None, new={"id": "a", "value": "1"})
_removed = _row("b", old={"id": "b", "value": "2"}, new=None)
_modified = _row("c", old={"id": "c", "value": "3"}, new={"id": "c", "value": "4"})


def test_sample_no_options_returns_all():
    result = _result(_added, _removed, _modified)
    sr = sample_diff(result, SampleOptions())
    assert sr.sampled_count == 3
    assert sr.dropped == 0


def test_sample_n_limits_rows():
    result = _result(_added, _removed, _modified)
    sr = sample_diff(result, SampleOptions(n=2, seed=0))
    assert sr.sampled_count == 2
    assert sr.dropped == 1


def test_sample_n_greater_than_count_keeps_all():
    result = _result(_added, _removed)
    sr = sample_diff(result, SampleOptions(n=100, seed=0))
    assert sr.sampled_count == 2


def test_sample_fraction():
    rows = [_row(str(i), old=None, new={"id": str(i)}) for i in range(10)]
    result = _result(*rows)
    sr = sample_diff(result, SampleOptions(fraction=0.5, seed=42))
    assert sr.sampled_count == 5


def test_sample_seed_reproducible():
    result = _result(_added, _removed, _modified)
    sr1 = sample_diff(result, SampleOptions(n=2, seed=7))
    sr2 = sample_diff(result, SampleOptions(n=2, seed=7))
    keys1 = [r.key for r in sr1.diff.rows]
    keys2 = [r.key for r in sr2.diff.rows]
    assert keys1 == keys2


def test_sample_filter_by_change_type():
    result = _result(_added, _removed, _modified)
    sr = sample_diff(result, SampleOptions(change_types=["added"]))
    assert sr.sampled_count == 1
    assert sr.diff.rows[0].key == "a"


def test_sample_filter_and_n():
    result = _result(_added, _removed, _modified)
    sr = sample_diff(result, SampleOptions(n=1, seed=0, change_types=["added", "removed"]))
    assert sr.sampled_count == 1


def test_format_notice_no_drop():
    result = _result(_added)
    sr = sample_diff(result, SampleOptions())
    notice = format_sample_notice(sr)
    assert "all rows retained" in notice


def test_format_notice_with_drop():
    result = _result(_added, _removed, _modified)
    sr = sample_diff(result, SampleOptions(n=1, seed=0))
    notice = format_sample_notice(sr)
    assert "1 of 3" in notice
    assert "2 dropped" in notice


def test_headers_preserved():
    result = _result(_added, _removed)
    sr = sample_diff(result, SampleOptions(n=1, seed=0))
    assert sr.diff.headers == ["id", "value"]
