"""Tests for csv_diff_reporter.diff_timeline."""
import json
import pytest
from pathlib import Path

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_timeline import (
    TimelineEntry,
    Timeline,
    entry_from_diff,
    load_timeline,
    save_timeline,
    format_timeline_text,
)


def _row(change_type: str) -> RowDiff:
    return RowDiff(key="k", change_type=change_type, before={}, after={})


def _result(*types: str) -> DiffResult:
    return DiffResult(headers=["a"], rows=[_row(t) for t in types])


def test_entry_from_diff_empty():
    e = entry_from_diff(_result(), timestamp="2024-01-01T00:00:00+00:00")
    assert e.added == 0
    assert e.removed == 0
    assert e.modified == 0
    assert e.total_rows == 0


def test_entry_from_diff_counts():
    result = _result("added", "added", "removed", "modified")
    e = entry_from_diff(result, timestamp="2024-01-01T00:00:00+00:00")
    assert e.added == 2
    assert e.removed == 1
    assert e.modified == 1
    assert e.total_rows == 4


def test_entry_from_diff_uses_provided_timestamp():
    e = entry_from_diff(_result(), timestamp="ts-fixed")
    assert e.timestamp == "ts-fixed"


def test_timeline_append():
    tl = Timeline()
    e = TimelineEntry(timestamp="t", added=1, removed=0, modified=0, total_rows=1)
    tl.append(e)
    assert len(tl.entries) == 1


def test_save_and_load_timeline(tmp_path: Path):
    tl = Timeline()
    tl.append(TimelineEntry(timestamp="2024-01-01T00:00:00+00:00", added=1, removed=2, modified=3, total_rows=6))
    dest = tmp_path / "sub" / "timeline.json"
    save_timeline(tl, dest)
    assert dest.exists()
    loaded = load_timeline(dest)
    assert len(loaded.entries) == 1
    assert loaded.entries[0].added == 1
    assert loaded.entries[0].removed == 2


def test_load_timeline_missing_file(tmp_path: Path):
    tl = load_timeline(tmp_path / "nonexistent.json")
    assert tl.entries == []


def test_save_timeline_creates_parent_dirs(tmp_path: Path):
    dest = tmp_path / "a" / "b" / "c" / "tl.json"
    save_timeline(Timeline(), dest)
    assert dest.exists()


def test_format_timeline_text_empty():
    out = format_timeline_text(Timeline())
    assert "No timeline" in out


def test_format_timeline_text_contains_entry():
    tl = Timeline()
    tl.append(TimelineEntry(timestamp="2024-06-01T12:00:00+00:00", added=3, removed=1, modified=2, total_rows=6))
    out = format_timeline_text(tl)
    assert "+3" in out
    assert "-1" in out
    assert "~2" in out
    assert "2024-06-01" in out


def test_timeline_as_dict_structure():
    tl = Timeline()
    tl.append(TimelineEntry(timestamp="t", added=0, removed=0, modified=0, total_rows=0))
    d = tl.as_dict()
    assert "entries" in d
    assert isinstance(d["entries"], list)
    assert d["entries"][0]["timestamp"] == "t"
