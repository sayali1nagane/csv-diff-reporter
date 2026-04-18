"""CLI helpers for the redact feature."""
from __future__ import annotations

import argparse
from typing import Optional

from csv_diff_reporter.diff_redactor import RedactOptions, redact_diff
from csv_diff_reporter.differ import DiffResult


def add_redact_args(parser: argparse.ArgumentParser) -> None:
    """Register --redact-columns and --redact-mask flags."""
    parser.add_argument(
        "--redact-columns",
        metavar="COL",
        nargs="+",
        default=[],
        help="Column names whose values should be masked in the report.",
    )
    parser.add_argument(
        "--redact-mask",
        metavar="MASK",
        default="***",
        help="Replacement string for redacted values (default: ***).",
    )


def build_redact_options(args: argparse.Namespace) -> Optional[RedactOptions]:
    cols = getattr(args, "redact_columns", []) or []
    if not cols:
        return None
    return RedactOptions(
        columns=frozenset(cols),
        mask=getattr(args, "redact_mask", "***"),
    )


def apply_redact(result: DiffResult, args: argparse.Namespace) -> DiffResult:
    opts = build_redact_options(args)
    return redact_diff(result, opts)
