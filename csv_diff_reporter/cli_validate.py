"""CLI integration for threshold validation."""
from __future__ import annotations
import argparse
import sys
from csv_diff_reporter.diff_validator import ThresholdOptions, validate_thresholds
from csv_diff_reporter.diff_validator_formatter import format_threshold_result
from csv_diff_reporter.differ import DiffResult


def add_validate_args(parser: argparse.ArgumentParser) -> None:
    g = parser.add_argument_group("threshold validation")
    g.add_argument("--max-added", type=int, default=None, metavar="N",
                   help="Fail if added rows exceed N")
    g.add_argument("--max-removed", type=int, default=None, metavar="N",
                   help="Fail if removed rows exceed N")
    g.add_argument("--max-modified", type=int, default=None, metavar="N",
                   help="Fail if modified rows exceed N")
    g.add_argument("--max-change-rate", type=float, default=None, metavar="R",
                   help="Fail if change rate exceeds R (0.0-1.0)")
    g.add_argument("--validate-exit-code", action="store_true", default=False,
                   help="Exit with code 1 when thresholds are violated")


def build_threshold_options(args: argparse.Namespace) -> ThresholdOptions:
    return ThresholdOptions(
        max_added=args.max_added,
        max_removed=args.max_removed,
        max_modified=args.max_modified,
        max_change_rate=args.max_change_rate,
    )


def apply_validation(result: DiffResult, args: argparse.Namespace, fmt: str = "text") -> str:
    opts = build_threshold_options(args)
    any_threshold = any([
        opts.max_added is not None,
        opts.max_removed is not None,
        opts.max_modified is not None,
        opts.max_change_rate is not None,
    ])
    if not any_threshold:
        return ""
    threshold_result = validate_thresholds(result, opts)
    output = format_threshold_result(threshold_result, fmt=fmt)
    if getattr(args, "validate_exit_code", False) and not threshold_result.is_valid():
        print(output, file=sys.stderr)
        sys.exit(1)
    return output
