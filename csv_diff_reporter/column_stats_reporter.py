"""Combines column-level stats with highlighting to produce enriched diff reports."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.stats import ColumnStats, DiffStats, compute_stats
from csv_diff_reporter.highlighter import HighlightedRow, highlight_row
from csv_diff_reporter.column_filter import ColumnFilterOptions, filter_columns


@dataclass
class EnrichedReport:
    """Holds the diff result alongside computed stats and highlighted rows."""

    diff: DiffResult
    stats: DiffStats
    highlighted_rows: List[HighlightedRow] = field(default_factory=list)
    filtered_columns: Optional[List[str]] = None

    def column_stats(self, column: str) -> Optional[ColumnStats]:
        """Return stats for a specific column, or None if not tracked."""
        return self.stats.by_column.get(column)

    @property
    def most_changed_column(self) -> Optional[str]:
        """Return the column name with the highest change count."""
        if not self.stats.by_column:
            return None
        return max(self.stats.by_column, key=lambda c: self.stats.by_column[c].change_count)


def build_enriched_report(
    diff: DiffResult,
    include_columns: Optional[List[str]] = None,
    exclude_columns: Optional[List[str]] = None,
) -> EnrichedReport:
    """Build an EnrichedReport from a DiffResult, applying optional column filtering."""
    opts = ColumnFilterOptions(
        include=include_columns or [],
        exclude=exclude_columns or [],
    )
    filtered = filter_columns(diff, opts) if (include_columns or exclude_columns) else diff

    stats = compute_stats(filtered)
    highlighted = [highlight_row(row_diff) for row_diff in filtered.rows]

    return EnrichedReport(
        diff=filtered,
        stats=stats,
        highlighted_rows=highlighted,
        filtered_columns=include_columns or exclude_columns or None,
    )
