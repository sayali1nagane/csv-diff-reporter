"""Tests for csv_diff_reporter.diff_watcher."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

import pytest

from csv_diff_reporter.diff_watcher import (
    WatchOptions,
    WatchState,
    _files_changed,
    _mtime,
    watch,
)


# ---------------------------------------------------------------------------
# _mtime
# ---------------------------------------------------------------------------

def test_mtime_returns_zero_for_missing_file(tmp_path):
    assert _mtime(tmp_path / "ghost.csv") == 0.0


def test_mtime_returns_positive_for_existing_file(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("x")
    assert _mtime(f) > 0.0


# ---------------------------------------------------------------------------
# _files_changed
# ---------------------------------------------------------------------------

def test_files_changed_detects_modification(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("old")
    b.write_text("old")

    state = WatchState(path_a=a, path_b=b)
    state.last_mtime_a = _mtime(a)
    state.last_mtime_b = _mtime(b)

    # Ensure mtime advances (some filesystems have 1-second resolution)
    time.sleep(0.01)
    a.write_text("new")
    a.touch()  # force mtime update

    # Patch stat so we get a reliably different mtime
    original_mtime = state.last_mtime_a
    state.last_mtime_a = original_mtime - 1  # simulate stale cache

    assert _files_changed(state) is True


def test_files_changed_returns_false_when_unchanged(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("x")
    b.write_text("y")

    state = WatchState(path_a=a, path_b=b)
    state.last_mtime_a = _mtime(a)
    state.last_mtime_b = _mtime(b)

    assert _files_changed(state) is False


# ---------------------------------------------------------------------------
# watch
# ---------------------------------------------------------------------------

def test_watch_respects_max_cycles(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("a")
    b.write_text("b")

    options = WatchOptions(interval=0.0, max_cycles=3)
    state = watch(a, b, options)

    assert state.cycles == 3


def test_watch_calls_on_change_when_file_modified(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("a")
    b.write_text("b")

    calls = []

    def _on_change(pa, pb):
        calls.append((pa, pb))

    # Seed state so first cycle sees a change
    options = WatchOptions(interval=0.0, max_cycles=1, on_change=_on_change)

    # Patch _files_changed to always return True
    with patch("csv_diff_reporter.diff_watcher._files_changed", return_value=True):
        state = watch(a, b, options)

    assert len(calls) == 1
    assert state.changes_detected == 1


def test_watch_no_change_on_change_not_called(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("a")
    b.write_text("b")

    calls = []
    options = WatchOptions(interval=0.0, max_cycles=5, on_change=lambda pa, pb: calls.append(1))

    with patch("csv_diff_reporter.diff_watcher._files_changed", return_value=False):
        state = watch(a, b, options)

    assert calls == []
    assert state.changes_detected == 0
