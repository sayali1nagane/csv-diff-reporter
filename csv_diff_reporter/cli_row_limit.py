"""CLI helpers for the row-limit feature."""
from __future__ import annotations

import argparse
import sys
from typing import Dict, List

from csv_diff_reporter.row_limit import RowLimitOptions, apply_row_limit, format_row_limit_warning


def add_row_limit_args(parser: argparse.ArgumentParser) -> None:
    """Register --max-rows CLI flag on *parser*."""
    parser.add_argument(
        "--max-rows",
        metavar="N",
        type=int,
        default=None,
        help="Maximum number of rows to read from each CSV file (default: unlimited).",
    )
    parser.add_argument(
        "--no-row-limit-warning",
        action="store_true",
        default=False,
        help="Suppress the warning printed when rows are omitted due to --max-rows.",
    )


def _validate_max_rows(max_rows: int | None) -> None:
    """Raise :class:`argparse.ArgumentTypeError` if *max_rows* is not a positive integer.

    This provides a clearer error message than the default argparse behaviour,
    which would silently accept zero or negative values.
    """
    if max_rows is not None and max_rows < 1:
        raise argparse.ArgumentTypeError(
            f"--max-rows must be a positive integer, got {max_rows!r}"
        )


def apply_row_limit_from_args(
    args: argparse.Namespace,
    data: Dict[str, List[dict]],
) -> Dict[str, List[dict]]:
    """Apply row limit based on parsed CLI arguments.

    Prints a warning to *stderr* when rows are dropped (unless suppressed).

    Raises :class:`argparse.ArgumentTypeError` if ``--max-rows`` is not a
    positive integer.

    Returns the (possibly truncated) data mapping.
    """
    _validate_max_rows(args.max_rows)

    options = RowLimitOptions(
        max_rows=args.max_rows,
        warn_on_truncation=not args.no_row_limit_warning,
    )
    result = apply_row_limit(data, options)

    if result.was_limited and options.warn_on_truncation:
        print(format_row_limit_warning(result), file=sys.stderr)

    return result.data
