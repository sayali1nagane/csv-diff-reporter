"""Compute per-column change statistics from a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from csv_diff_reporter.differ import DiffResult


@dataclass
class ColumnStats:
    """Statistics for a single column."""
    name: str
    changes: int = 0
    added_occurrences: int = 0
    removed_occurrences: int = 0

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "changes": self.changes,
            "added_occurrences": self.added_occurrences,
            "removed_occurrences": self.removed_occurrences,
        }


@dataclass
class DiffStats:
    """Aggregated per-column statistics for a diff result."""
    total_rows_compared: int = 0
    columns: Dict[str, ColumnStats] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "total_rows_compared": self.total_rows_compared,
            "columns": {k: v.as_dict() for k, v in self.columns.items()},
        }


def compute_stats(result: DiffResult) -> DiffStats:
    """Return per-column statistics derived from *result*."""
    stats = DiffStats()
    all_rows = result.added + result.removed + result.modified + result.unchanged
    stats.total_rows_compared = len(all_rows)

    for row_diff in result.modified:
        for col in row_diff.changed_fields:
            if col not in stats.columns:
                stats.columns[col] = ColumnStats(name=col)
            stats.columns[col].changes += 1

    for row_diff in result.added:
        for col in (row_diff.new_row or {}):
            if col not in stats.columns:
                stats.columns[col] = ColumnStats(name=col)
            stats.columns[col].added_occurrences += 1

    for row_diff in result.removed:
        for col in (row_diff.old_row or {}):
            if col not in stats.columns:
                stats.columns[col] = ColumnStats(name=col)
            stats.columns[col].removed_occurrences += 1

    return stats


def format_stats_text(stats: DiffStats) -> str:
    """Return a human-readable text representation of *stats*."""
    lines = [f"Rows compared : {stats.total_rows_compared}"]
    if not stats.columns:
        lines.append("No column-level changes detected.")
        return "\n".join(lines)
    lines.append("\nPer-column breakdown:")
    for col_stats in sorted(stats.columns.values(), key=lambda c: -c.changes):
        lines.append(
            f"  {col_stats.name}: {col_stats.changes} change(s), "
            f"{col_stats.added_occurrences} added, "
            f"{col_stats.removed_occurrences} removed"
        )
    return "\n".join(lines)
