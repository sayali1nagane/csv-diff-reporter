"""Tests for csv_diff_reporter.watch_event_log."""

from __future__ import annotations

from pathlib import Path

import pytest

from csv_diff_reporter.watch_event_log import (
    EventLog,
    WatchEvent,
    make_logging_callback,
)


PA = Path("a.csv")
PB = Path("b.csv")


# ---------------------------------------------------------------------------
# EventLog
# ---------------------------------------------------------------------------

def test_event_log_starts_empty():
    log = EventLog()
    assert log.count() == 0
    assert log.all() == []


def test_event_log_records_event():
    log = EventLog()
    event = log.record(PA, PB, cycle=1)
    assert isinstance(event, WatchEvent)
    assert log.count() == 1


def test_event_log_all_returns_copy():
    log = EventLog()
    log.record(PA, PB, cycle=1)
    first = log.all()
    log.record(PA, PB, cycle=2)
    assert len(first) == 1  # snapshot not affected by later records


def test_event_log_clear_resets_count():
    log = EventLog()
    log.record(PA, PB, cycle=1)
    log.clear()
    assert log.count() == 0


def test_event_as_dict_has_expected_keys():
    log = EventLog()
    event = log.record(PA, PB, cycle=7)
    d = event.as_dict()
    assert set(d.keys()) == {"timestamp", "path_a", "path_b", "cycle"}
    assert d["cycle"] == 7
    assert d["path_a"] == "a.csv"


# ---------------------------------------------------------------------------
# make_logging_callback
# ---------------------------------------------------------------------------

def test_make_logging_callback_increments_cycle():
    log = EventLog()
    counter = [0]
    cb = make_logging_callback(log, counter)

    cb(PA, PB)
    cb(PA, PB)

    assert log.count() == 2
    assert counter[0] == 2


def test_make_logging_callback_stores_paths():
    log = EventLog()
    counter = [0]
    cb = make_logging_callback(log, counter)
    cb(PA, PB)

    event = log.all()[0]
    assert event.path_a == PA
    assert event.path_b == PB
