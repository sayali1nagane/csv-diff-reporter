"""Format an EnrichedReport as text or JSON for CLI output."""
from __future__ import annotations

import json
from typing import Literal

from csv_diff_reporter.column_stats_reporter import EnrichedReport
from csv_diff_reporter.stats_formatter import format_stats
from csv_diff_reporter.reporter import generate_report


OutputFormat = Literal["text", "json"]


def format_enriched_report(report: EnrichedReport, fmt: OutputFormat = "text") -> str:
    """Render an EnrichedReport as either plain text or JSON."""
    if fmt == "json":
        return _as_json(report)
    return _as_text(report)


def _as_text(report: EnrichedReport) -> str:
    lines: list[str] = []

    diff_text = generate_report(report.diff)
    if diff_text:
        lines.append(diff_text)

    stats_text = format_stats(report.stats, fmt="text")
    if stats_text:
        lines.append("")
        lines.append("=== Column Statistics ===")
        lines.append(stats_text)

    most_changed = report.most_changed_column
    if most_changed:
        lines.append(f"Most changed column: {most_changed}")

    return "\n".join(lines)


def _as_json(report: EnrichedReport) -> str:
    stats_payload = json.loads(format_stats(report.stats, fmt="json"))
    payload = {
        "stats": stats_payload,
        "most_changed_column": report.most_changed_column,
        "filtered_columns": report.filtered_columns,
    }
    return json.dumps(payload, indent=2)
