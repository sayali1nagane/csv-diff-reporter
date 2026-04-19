"""Archive diff results to a timestamped directory structure."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.formatter import format_output


class ArchiveError(Exception):
    pass


@dataclass
class ArchiveOptions:
    base_dir: str = "archives"
    label: str = ""
    formats: list = field(default_factory=lambda: ["text"])
    timestamp: Optional[datetime] = None


@dataclass
class ArchiveEntry:
    path: str
    timestamp: str
    label: str
    formats: list

    def as_dict(self) -> dict:
        return {
            "path": self.path,
            "timestamp": self.timestamp,
            "label": self.label,
            "formats": self.formats,
        }


def _timestamp_str(dt: Optional[datetime]) -> str:
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def archive_diff(result: DiffResult, options: ArchiveOptions) -> ArchiveEntry:
    ts = _timestamp_str(options.timestamp)
    slug = f"{ts}_{options.label}" if options.label else ts
    target = Path(options.base_dir) / slug
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ArchiveError(f"Cannot create archive directory {target}: {exc}") from exc

    written = []
    for fmt in options.formats:
        content = format_output(result, fmt)
        ext = "json" if fmt == "json" else "md" if fmt == "markdown" else "txt"
        file_path = target / f"diff.{ext}"
        try:
            file_path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise ArchiveError(f"Cannot write {file_path}: {exc}") from exc
        written.append(fmt)

    meta_path = target / "meta.json"
    meta = {"timestamp": ts, "label": options.label, "formats": written}
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return ArchiveEntry(path=str(target), timestamp=ts, label=options.label, formats=written)
