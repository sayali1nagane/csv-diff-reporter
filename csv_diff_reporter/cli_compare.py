"""CLI helpers for the diff-compare feature."""
from __future__ import annotations
import argparse
from csv_diff_reporter.diff_comparator import compare_diffs, ComparisonResult
from csv_diff_reporter.diff_comparator_formatter import format_comparison
from csv_diff_reporter.differ import DiffResult


def add_compare_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--compare",
        metavar="FILE",
        default=None,
        help="Path to a second diff result (CSV export) to compare against the primary diff.",
    )
    parser.add_argument(
        "--compare-label-a",
        default="A",
        metavar="LABEL",
        help="Label for the primary diff (default: A).",
    )
    parser.add_argument(
        "--compare-label-b",
        default="B",
        metavar="LABEL",
        help="Label for the comparison diff (default: B).",
    )
    parser.add_argument(
        "--compare-format",
        choices=["text", "json"],
        default="text",
        help="Output format for the comparison report.",
    )


def apply_compare(
    args: argparse.Namespace,
    primary: DiffResult,
    secondary: DiffResult,
) -> ComparisonResult:
    return compare_diffs(
        primary,
        secondary,
        label_a=args.compare_label_a,
        label_b=args.compare_label_b,
    )


def render_compare(result: ComparisonResult, fmt: str = "text") -> str:
    return format_comparison(result, fmt=fmt)
