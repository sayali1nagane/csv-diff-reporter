"""CLI helpers for the row-annotation feature."""
from __future__ import annotations

import argparse
from typing import Optional

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.row_annotator import AnnotatedResult, annotate_diff
from csv_diff_reporter.row_annotator_formatter import format_annotated


def add_annotate_args(parser: argparse.ArgumentParser) -> None:
    """Register --annotate and --annotate-format flags on *parser*."""
    parser.add_argument(
        "--annotate",
        action="store_true",
        default=False,
        help="Annotate each changed row with a label and severity.",
    )
    parser.add_argument(
        "--annotate-format",
        choices=["text", "json"],
        default="text",
        dest="annotate_format",
        help="Output format for the annotation report (default: text).",
    )


def apply_annotation(
    args: argparse.Namespace,
    result: DiffResult,
) -> Optional[AnnotatedResult]:
    """Return an AnnotatedResult when --annotate is set, else None."""
    if not getattr(args, "annotate", False):
        return None
    return annotate_diff(result)


def render_annotation(
    annotated: Optional[AnnotatedResult],
    fmt: str = "text",
) -> str:
    """Render *annotated* to a string, or return an empty string."""
    if annotated is None:
        return ""
    return format_annotated(annotated, fmt=fmt)
