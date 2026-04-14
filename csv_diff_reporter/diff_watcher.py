"""Watch CSV files for changes and trigger re-diff automatically."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


@dataclass
class WatchOptions:
    interval: float = 2.0  # seconds between polls
    max_cycles: Optional[int] = None  # None means run forever
    on_change: Optional[Callable[[Path, Path], None]] = None


@dataclass
class WatchState:
    path_a: Path
    path_b: Path
    last_mtime_a: float = 0.0
    last_mtime_b: float = 0.0
    cycles: int = 0
    changes_detected: int = 0


def _mtime(path: Path) -> float:
    """Return modification time for *path*, or 0.0 if the file is missing."""
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _files_changed(state: WatchState) -> bool:
    """Return True if either file has been modified since the last check."""
    mtime_a = _mtime(state.path_a)
    mtime_b = _mtime(state.path_b)
    changed = mtime_a != state.last_mtime_a or mtime_b != state.last_mtime_b
    state.last_mtime_a = mtime_a
    state.last_mtime_b = mtime_b
    return changed


def watch(path_a: Path, path_b: Path, options: WatchOptions) -> WatchState:
    """Poll *path_a* and *path_b* and invoke *options.on_change* on each change.

    Returns the final :class:`WatchState` after the watch loop exits.
    """
    state = WatchState(path_a=path_a, path_b=path_b)
    # Seed mtimes so the very first cycle does not fire a spurious change.
    state.last_mtime_a = _mtime(path_a)
    state.last_mtime_b = _mtime(path_b)

    while True:
        if options.max_cycles is not None and state.cycles >= options.max_cycles:
            break

        time.sleep(options.interval)
        state.cycles += 1

        if _files_changed(state):
            state.changes_detected += 1
            if options.on_change is not None:
                options.on_change(path_a, path_b)

    return state
