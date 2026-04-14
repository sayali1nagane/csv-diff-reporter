"""Simple in-memory event log for watch cycles."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List


@dataclass
class WatchEvent:
    timestamp: datetime
    path_a: Path
    path_b: Path
    cycle: int

    def as_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "path_a": str(self.path_a),
            "path_b": str(self.path_b),
            "cycle": self.cycle,
        }


@dataclass
class EventLog:
    _events: List[WatchEvent] = field(default_factory=list)

    def record(self, path_a: Path, path_b: Path, cycle: int) -> WatchEvent:
        event = WatchEvent(
            timestamp=datetime.now(tz=timezone.utc),
            path_a=path_a,
            path_b=path_b,
            cycle=cycle,
        )
        self._events.append(event)
        return event

    def all(self) -> List[WatchEvent]:
        return list(self._events)

    def count(self) -> int:
        return len(self._events)

    def clear(self) -> None:
        self._events.clear()


def make_logging_callback(log: EventLog, cycle_counter: list):
    """Return an on_change callback that records each event into *log*.

    *cycle_counter* should be a one-element list ``[0]`` that the caller
    increments externally, or we track internally here.
    """

    def _callback(path_a: Path, path_b: Path) -> None:
        cycle_counter[0] += 1
        log.record(path_a=path_a, path_b=path_b, cycle=cycle_counter[0])

    return _callback
