"""CLI helpers for the diff-tagger feature."""
from __future__ import annotations

import argparse
from typing import List, Optional

from csv_diff_reporter.differ import DiffResult, RowDiff
from csv_diff_reporter.diff_tagger import TagOptions, TagRule, TaggedResult, tag_diff
from csv_diff_reporter.diff_tagger_formatter import format_tagged


def add_tag_args(parser: argparse.ArgumentParser) -> None:
    """Register ``--tag`` and ``--tag-output-format`` arguments on *parser*."""
    parser.add_argument(
        "--tag-added",
        metavar="LABEL",
        default=None,
        help="Tag all added rows with LABEL.",
    )
    parser.add_argument(
        "--tag-removed",
        metavar="LABEL",
        default=None,
        help="Tag all removed rows with LABEL.",
    )
    parser.add_argument(
        "--tag-modified",
        metavar="LABEL",
        default=None,
        help="Tag all modified rows with LABEL.",
    )
    parser.add_argument(
        "--tag-output-format",
        choices=["text", "json"],
        default="text",
        help="Output format for the tag report (default: text).",
    )


def _build_options(args: argparse.Namespace) -> Optional[TagOptions]:
    rules: List[TagRule] = []
    if getattr(args, "tag_added", None):
        label = args.tag_added
        rules.append(TagRule(tag=label, predicate=lambda r: r.change_type == "added"))
    if getattr(args, "tag_removed", None):
        label = args.tag_removed
        rules.append(TagRule(tag=label, predicate=lambda r: r.change_type == "removed"))
    if getattr(args, "tag_modified", None):
        label = args.tag_modified
        rules.append(TagRule(tag=label, predicate=lambda r: r.change_type == "modified"))
    return TagOptions(rules=rules) if rules else None


def apply_tagging(result: DiffResult, args: argparse.Namespace) -> TaggedResult:
    """Build tag options from *args* and run the tagger over *result*."""
    options = _build_options(args)
    return tag_diff(result, options)


def render_tagged(tagged: TaggedResult, args: argparse.Namespace) -> str:
    """Format *tagged* according to ``--tag-output-format``."""
    fmt = getattr(args, "tag_output_format", "text")
    return format_tagged(tagged, fmt=fmt)
