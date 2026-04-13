"""Simple file-based cache for parsed CSV data keyed by file path and mtime."""

from __future__ import annotations

import hashlib
import os
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class CacheEntry:
    mtime: float
    size: int
    data: Any


@dataclass
class CacheStore:
    _store: Dict[str, CacheEntry] = field(default_factory=dict)

    def _key(self, path: str) -> str:
        return hashlib.md5(path.encode()).hexdigest()

    def get(self, path: str) -> Optional[Any]:
        """Return cached data if the file has not changed since caching."""
        try:
            stat = os.stat(path)
        except OSError:
            return None
        key = self._key(path)
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.mtime != stat.st_mtime or entry.size != stat.st_size:
            return None
        return entry.data

    def set(self, path: str, data: Any) -> None:
        """Store data for the given file path."""
        try:
            stat = os.stat(path)
        except OSError:
            return
        key = self._key(path)
        self._store[key] = CacheEntry(mtime=stat.st_mtime, size=stat.st_size, data=data)

    def invalidate(self, path: str) -> None:
        key = self._key(path)
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


def save_cache(store: CacheStore, cache_path: Path) -> None:
    """Persist a CacheStore to disk."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("wb") as fh:
        pickle.dump(store, fh)


def load_cache(cache_path: Path) -> CacheStore:
    """Load a CacheStore from disk, returning an empty store on any error."""
    try:
        with cache_path.open("rb") as fh:
            obj = pickle.load(fh)
        if isinstance(obj, CacheStore):
            return obj
    except Exception:
        pass
    return CacheStore()
