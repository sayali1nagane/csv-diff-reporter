"""CLI integration for diff sampling."""
from __future__ import annotations

import argparse
from typing import Optional

from csv_diff_reporter.diff_sampler import SampleOptions, SampleResult, format_sample_notice, sample_diff
from csv_diff_reporter.differ import DiffResult


def add_sample_args(parser: argparse.ArgumentParser) -> None:
    grp = parser.add_argument_group("sampling")
    grp.add_argument(
        "--sample-n",
        type=int,
        default=None,
        metavar="N",
        help="Keep at most N rows from the diff.",
    )
    grp.add_argument(
        "--sample-fraction",
        type=float,
        default=None,
        metavar="F",
        help="Keep a fraction (0.0–1.0) of diff rows.",
    )
    grp.add_argument(
        "--sample-seed",
        type=int,
        default=None,
        metavar="SEED",
        help="Random seed for reproducible sampling.",
    )
    grp.add_argument(
        "--sample-types",
        nargs="+",
        choices=["added", "removed", "modified"],
        default=None,
        metavar="TYPE",
        help="Restrict sampling to specific change types.",
    )
    grp.add_argument(
        "--sample-notice",
        action="store_true",
        default=False,
        help="Print a notice showing how many rows were sampled.",
    )


def apply_sample(diff: DiffResult, args: argparse.Namespace) -> tuple[DiffResult, Optional[SampleResult]]:
    n = getattr(args, "sample_n", None)
    fraction = getattr(args, "sample_fraction", None)
    if n is None and fraction is None:
        return diff, None

    options = SampleOptions(
        n=n,
        fraction=fraction,
        seed=getattr(args, "sample_seed", None),
        change_types=getattr(args, "sample_types", None),
    )
    result = sample_diff(diff, options)
    return result.diff, result


def render_sample_notice(result: Optional[SampleResult]) -> str:
    if result is None:
        return ""
    return format_sample_notice(result)
