"""CLI helpers for the diff-splitter feature."""
from __future__ import annotations

import argparse
from typing import Optional

from csv_diff_reporter.diff_splitter import SplitOptions, SplitResult, split_diff
from csv_diff_reporter.differ import DiffResult


def add_split_args(parser: argparse.ArgumentParser) -> None:
    """Register split-related flags on *parser*."""
    group = parser.add_argument_group("splitting")
    group.add_argument(
        "--split-size",
        type=int,
        default=None,
        metavar="N",
        help="Split diff output into chunks of at most N rows.",
    )
    group.add_argument(
        "--split-by-type",
        action="store_true",
        default=False,
        help="Emit a separate chunk for each change type (added/removed/modified).",
    )


def build_split_options(args: argparse.Namespace) -> Optional[SplitOptions]:
    """Return a SplitOptions from parsed *args*, or None if splitting is disabled."""
    size: Optional[int] = getattr(args, "split_size", None)
    by_type: bool = getattr(args, "split_by_type", False)
    if size is None and not by_type:
        return None
    return SplitOptions(chunk_size=size, by_type=by_type)


def apply_split(result: DiffResult, args: argparse.Namespace) -> SplitResult:
    """Apply splitting to *result* based on CLI *args*."""
    options = build_split_options(args)
    return split_diff(result, options)


def render_split_notice(split: SplitResult) -> str:
    """Return a short human-readable summary of the split operation."""
    if split.count <= 1:
        return ""
    total_rows = sum(len(c.rows) for c in split.chunks)
    return (
        f"[split] {split.count} chunks, {total_rows} rows total "
        f"(labels: {', '.join(split.labels)})"
    )
