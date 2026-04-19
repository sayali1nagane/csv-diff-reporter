"""Produce a concise human-readable summary sentence for a DiffResult."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

from csv_diff_reporter.differ import DiffResult


@dataclass
class SummaryLine:
    added: int
    removed: int
    modified: int
    unchanged: int
    total_rows: int

    def as_dict(self) -> dict:
        return {
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
            "unchanged": self.unchanged,
            "total_rows": self.total_rows,
            "changed": self.added + self.removed + self.modified,
        }


def build_summary_line(result: DiffResult) -> SummaryLine:
    added = sum(1 for r in result.rows if r.change_type == "added")
    removed = sum(1 for r in result.rows if r.change_type == "removed")
    modified = sum(1 for r in result.rows if r.change_type == "modified")
    unchanged = sum(1 for r in result.rows if r.change_type == "unchanged")
    total_rows = added + removed + modified + unchanged
    return SummaryLine(
        added=added,
        removed=removed,
        modified=modified,
        unchanged=unchanged,
        total_rows=total_rows,
    )


def format_summary_line(
    summary: SummaryLine,
    fmt: Literal["text", "json"] = "text",
) -> str:
    if fmt == "json":
        return json.dumps(summary.as_dict(), indent=2)

    changed = summary.added + summary.removed + summary.modified
    if changed == 0:
        return "No differences found."

    parts: list[str] = []
    if summary.added:
        parts.append(f"{summary.added} added")
    if summary.removed:
        parts.append(f"{summary.removed} removed")
    if summary.modified:
        parts.append(f"{summary.modified} modified")

    pct = (changed / summary.total_rows * 100) if summary.total_rows else 0.0
    return f"{changed} change(s) across {summary.total_rows} row(s): {', '.join(parts)} ({pct:.1f}% affected)."
