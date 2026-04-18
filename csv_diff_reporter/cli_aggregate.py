"""CLI helpers for the diff aggregation feature."""
from __future__ import annotations
import argparse
from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.diff_aggregator import AggregateResult, aggregate_diff
from csv_diff_reporter.diff_aggregator_formatter import format_aggregate


def add_aggregate_args(parser: argparse.ArgumentParser) -> None:
    grp = parser.add_argument_group("aggregation")
    grp.add_argument(
        "--aggregate-by",
        metavar="COLUMN",
        default=None,
        help="Aggregate diff counts grouped by values of COLUMN.",
    )
    grp.add_argument(
        "--aggregate-format",
        choices=["text", "json"],
        default="text",
        help="Output format for the aggregation report (default: text).",
    )


def apply_aggregation(
    args: argparse.Namespace, result: DiffResult
) -> AggregateResult | None:
    col = getattr(args, "aggregate_by", None)
    if not col:
        return None
    return aggregate_diff(result, col)


def render_aggregate(agg: AggregateResult | None, fmt: str = "text") -> str:
    if agg is None:
        return ""
    return format_aggregate(agg, fmt)
