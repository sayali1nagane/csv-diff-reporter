"""Track how diff metrics change across multiple runs over time."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from csv_diff_reporter.differ import DiffResult


@dataclass
class TimelineEntry:
    timestamp: str
    added: int
    removed: int
    modified: int
    total_rows: int

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class Timeline:
    entries: List[TimelineEntry] = field(default_factory=list)

    def append(self, entry: TimelineEntry) -> None:
        self.entries.append(entry)

    def as_dict(self) -> dict:
        return {"entries": [e.as_dict() for e in self.entries]}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def entry_from_diff(result: DiffResult, timestamp: Optional[str] = None) -> TimelineEntry:
    added = sum(1 for r in result.rows if r.change_type == "added")
    removed = sum(1 for r in result.rows if r.change_type == "removed")
    modified = sum(1 for r in result.rows if r.change_type == "modified")
    return TimelineEntry(
        timestamp=timestamp or _now_iso(),
        added=added,
        removed=removed,
        modified=modified,
        total_rows=len(result.rows),
    )


def load_timeline(path: Path) -> Timeline:
    if not path.exists():
        return Timeline()
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = [TimelineEntry(**e) for e in data.get("entries", [])]
    return Timeline(entries=entries)


def save_timeline(timeline: Timeline, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(timeline.as_dict(), indent=2), encoding="utf-8")


def format_timeline_text(timeline: Timeline) -> str:
    if not timeline.entries:
        return "No timeline entries recorded."
    lines = ["Diff Timeline", "=" * 40]
    for e in timeline.entries:
        lines.append(
            f"{e.timestamp}  +{e.added} -{e.removed} ~{e.modified}  total={e.total_rows}"
        )
    return "\n".join(lines)
