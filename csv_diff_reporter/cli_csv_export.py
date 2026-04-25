"""CLI helpers for exporting the diff as a CSV file."""
from __future__ import annotations

import argparse
from pathlib import Path

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.diff_formatter_csv import format_diff_as_csv


def add_csv_export_args(parser: argparse.ArgumentParser) -> None:
    """Register ``--csv-output`` and ``--csv-unchanged`` flags on *parser*."""
    group = parser.add_argument_group("CSV export")
    group.add_argument(
        "--csv-output",
        metavar="PATH",
        default=None,
        help="Write diff as CSV to PATH.",
    )
    group.add_argument(
        "--csv-stdout",
        action="store_true",
        default=False,
        help="Print diff as CSV to stdout.",
    )
    group.add_argument(
        "--csv-unchanged",
        action="store_true",
        default=False,
        help="Include unchanged rows in the CSV output.",
    )


def apply_csv_export(args: argparse.Namespace, result: DiffResult) -> str | None:
    """Write CSV output if requested; return the CSV string or *None*.

    The CSV content is written to ``args.csv_output`` when provided, and
    printed to stdout when ``args.csv_stdout`` is *True*.  Returns the
    generated CSV string so callers can inspect or chain it; returns *None*
    when no CSV export was requested.
    """
    if not getattr(args, "csv_output", None) and not getattr(args, "csv_stdout", False):
        return None

    include_unchanged: bool = getattr(args, "csv_unchanged", False)
    csv_text = format_diff_as_csv(result, include_unchanged=include_unchanged)

    if getattr(args, "csv_output", None):
        dest = Path(args.csv_output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(csv_text, encoding="utf-8")

    if getattr(args, "csv_stdout", False):
        print(csv_text, end="")

    return csv_text
