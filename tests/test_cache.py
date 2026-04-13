"""Tests for csv_diff_reporter.cache."""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from csv_diff_reporter.cache import (
    CacheStore,
    load_cache,
    save_cache,
)


@pytest.fixture
def tmp_csv(tmp_path: Path) -> Path:
    p = tmp_path / "sample.csv"
    p.write_text("a,b\n1,2\n")
    return p


def test_cache_miss_on_empty_store(tmp_csv: Path):
    store = CacheStore()
    assert store.get(str(tmp_csv)) is None


def test_cache_hit_after_set(tmp_csv: Path):
    store = CacheStore()
    store.set(str(tmp_csv), {"rows": 42})
    result = store.get(str(tmp_csv))
    assert result == {"rows": 42}


def test_cache_miss_after_file_modified(tmp_csv: Path):
    store = CacheStore()
    store.set(str(tmp_csv), "old")
    # Modify the file so mtime/size changes
    time.sleep(0.01)
    tmp_csv.write_text("a,b\n1,2\n3,4\n")
    os.utime(tmp_csv, (time.time() + 1, time.time() + 1))
    assert store.get(str(tmp_csv)) is None


def test_cache_invalidate(tmp_csv: Path):
    store = CacheStore()
    store.set(str(tmp_csv), "data")
    store.invalidate(str(tmp_csv))
    assert store.get(str(tmp_csv)) is None


def test_cache_clear(tmp_csv: Path):
    store = CacheStore()
    store.set(str(tmp_csv), "data")
    store.clear()
    assert store.get(str(tmp_csv)) is None


def test_cache_missing_file_returns_none():
    store = CacheStore()
    assert store.get("/nonexistent/path/file.csv") is None


def test_set_missing_file_does_not_raise():
    store = CacheStore()
    store.set("/nonexistent/path/file.csv", "data")  # should not raise


def test_save_and_load_cache(tmp_path: Path, tmp_csv: Path):
    store = CacheStore()
    store.set(str(tmp_csv), ["row1", "row2"])
    cache_file = tmp_path / ".cache" / "csv_diff.pkl"
    save_cache(store, cache_file)
    assert cache_file.exists()
    loaded = load_cache(cache_file)
    assert loaded.get(str(tmp_csv)) == ["row1", "row2"]


def test_load_cache_returns_empty_store_on_missing_file(tmp_path: Path):
    cache_file = tmp_path / "nonexistent.pkl"
    store = load_cache(cache_file)
    assert isinstance(store, CacheStore)


def test_load_cache_returns_empty_store_on_corrupt_file(tmp_path: Path):
    cache_file = tmp_path / "corrupt.pkl"
    cache_file.write_bytes(b"not valid pickle data!!!")
    store = load_cache(cache_file)
    assert isinstance(store, CacheStore)
