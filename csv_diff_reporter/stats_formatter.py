"""Format DiffStats as JSON or Markdown for output."""
from __future__ import annotations

import json
from typing import Literal

from csv_diff_reporter.stats import DiffStats, format_stats_text


def _stats_to_markdown(stats: DiffStats) -> str:
    """Render *stats* as a Markdown table."""
    lines = [
        f"**Rows compared:** {stats.total_rows_compared}\n",
        "| Column | Changes | Added | Removed |",
        "| --- | --- | --- | --- |",
    ]
    if not stats.columns:
        lines.append("| — | 0 | 0 | 0 |")
        return "\n".join(lines)
    for col in sorted(stats.columns.values(), key=lambda c: -c.changes):
        lines.append(
            f"| {col.name} | {col.changes} | {col.added_occurrences} | {col.removed_occurrences} |"
        )
    return "\n".join(lines)


def format_stats(
    stats: DiffStats,
    output_format: Literal["text", "json", "markdown"] = "text",
) -> str:
    """Return *stats* serialised in the requested *output_format*."""
    if output_format == "json":
        return json.dumps(stats.as_dict(), indent=2)
    if output_format == "markdown":
        return _stats_to_markdown(stats)
    return format_stats_text(stats)
