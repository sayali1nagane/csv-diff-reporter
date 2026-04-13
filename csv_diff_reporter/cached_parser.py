"""Wrapper around parser.load_csv that uses CacheStore to avoid re-parsing."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union

from .cache import CacheStore, load_cache, save_cache
from .parser import load_csv

_DEFAULT_CACHE_PATH = Path(".csv_diff_cache") / "parsed.pkl"


def _get_store(cache_path: Path, persist: bool) -> CacheStore:
    if persist and cache_path.exists():
        return load_cache(cache_path)
    return CacheStore()


def cached_load_csv(
    path: str,
    key_column: Optional[str] = None,
    *,
    store: Optional[CacheStore] = None,
    cache_path: Path = _DEFAULT_CACHE_PATH,
    persist: bool = False,
) -> Union[List[Dict], Dict]:
    """Load a CSV file, returning a cached result when the file is unchanged.

    Parameters
    ----------
    path:
        Path to the CSV file.
    key_column:
        Optional column name to use as the row key (passed to ``load_csv``).
    store:
        An existing :class:`CacheStore` instance.  When *None* a new in-memory
        store is created (or loaded from *cache_path* when *persist* is True).
    cache_path:
        Location of the on-disk pickle file used when *persist* is True.
    persist:
        When True the cache is loaded from and saved to *cache_path*.
    """
    if store is None:
        store = _get_store(cache_path, persist)

    cache_key = f"{path}::{key_column}"
    # Use a temporary file path for the store key so mtime checks work.
    cached = store.get(path)
    if cached is not None and isinstance(cached, dict) and cache_key in cached:
        return cached[cache_key]

    data = load_csv(path, key_column=key_column)

    # Store all variants for this path in a single entry keyed by path.
    entry: dict = store.get(path) or {}
    entry[cache_key] = data
    store.set(path, entry)

    if persist:
        save_cache(store, cache_path)

    return data
