"""CLI helpers for the diff-merge feature."""
from __future__ import annotations

import argparse
from typing import List

from csv_diff_reporter.diff_merger import MergeOptions, MergeResult, merge_diffs
from csv_diff_reporter.differ import DiffResult


def add_merge_args(parser: argparse.ArgumentParser) -> None:
    """Register merge-related flags on *parser*."""
    group = parser.add_argument_group("merge")
    group.add_argument(
        "--merge",
        metavar="FILE",
        dest="merge_diff_file",
        default=None,
        help="Path to a second diff to merge into the primary diff output.",
    )
    group.add_argument(
        "--merge-no-dedup",
        action="store_true",
        default=False,
        help="Keep duplicate keys from the secondary diff instead of dropping them.",
    )
    group.add_argument(
        "--merge-tag-source",
        action="store_true",
        default=False,
        help="Annotate each row with a '__source__' field (\"a\" or \"b\").",
    )
    group.add_argument(
        "--merge-source-a-label",
        default="a",
        metavar="LABEL",
        help="Label used for rows from the primary diff (default: a).",
    )
    group.add_argument(
        "--merge-source-b-label",
        default="b",
        metavar="LABEL",
        help="Label used for rows from the secondary diff (default: b).",
    )


def build_merge_options(args: argparse.Namespace) -> MergeOptions:
    """Construct a :class:`MergeOptions` from parsed CLI *args*."""
    return MergeOptions(
        deduplicate=not getattr(args, "merge_no_dedup", False),
        tag_source=getattr(args, "merge_tag_source", False),
        source_a_label=getattr(args, "merge_source_a_label", "a"),
        source_b_label=getattr(args, "merge_source_b_label", "b"),
    )


def apply_merge(
    primary: DiffResult,
    secondary: DiffResult,
    args: argparse.Namespace,
) -> tuple[DiffResult, List[str]]:
    """Merge *secondary* into *primary* using options from *args*.

    Returns
    -------
    tuple
        ``(merged_diff, duplicate_keys)``
    """
    options = build_merge_options(args)
    merge_result: MergeResult = merge_diffs(primary, secondary, options)
    return merge_result.result, merge_result.duplicate_keys


def render_merge_notice(duplicate_keys: List[str]) -> str:
    """Return a human-readable notice about dropped duplicate keys."""
    if not duplicate_keys:
        return ""
    count = len(duplicate_keys)
    sample = duplicate_keys[:5]
    sample_str = ", ".join(str(k) for k in sample)
    suffix = " ..." if count > 5 else ""
    return (
        f"[merge] {count} duplicate key(s) dropped from secondary diff: "
        f"{sample_str}{suffix}"
    )
