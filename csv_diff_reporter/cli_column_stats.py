"""CLI helpers for the column-stats-reporter feature."""
from __future__ import annotations

import argparse
from typing import List, Optional

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.column_stats_reporter import EnrichedReport, build_enriched_report
from csv_diff_reporter.column_stats_formatter import format_enriched_report


def add_column_stats_args(parser: argparse.ArgumentParser) -> None:
    """Register column-stats flags on an existing argument parser."""
    grp = parser.add_argument_group("column stats")
    grp.add_argument(
        "--stats-include-columns",
        metavar="COL",
        nargs="+",
        default=None,
        help="Only include these columns in the stats report.",
    )
    grp.add_argument(
        "--stats-exclude-columns",
        metavar="COL",
        nargs="+",
        default=None,
        help="Exclude these columns from the stats report.",
    )
    grp.add_argument(
        "--stats-format",
        choices=["text", "json"],
        default="text",
        help="Output format for the enriched stats report (default: text).",
    )


def apply_column_stats(
    diff: DiffResult,
    args: argparse.Namespace,
) -> EnrichedReport:
    """Build an EnrichedReport from CLI args."""
    include: Optional[List[str]] = getattr(args, "stats_include_columns", None)
    exclude: Optional[List[str]] = getattr(args, "stats_exclude_columns", None)
    return build_enriched_report(diff, include_columns=include, exclude_columns=exclude)


def render_enriched_report(report: EnrichedReport, args: argparse.Namespace) -> str:
    """Render the enriched report according to the chosen format."""
    fmt = getattr(args, "stats_format", "text")
    return format_enriched_report(report, fmt=fmt)
