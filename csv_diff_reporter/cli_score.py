"""CLI integration for the diff scorer feature."""
from __future__ import annotations
import argparse
from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.diff_scorer import score_diff, DiffScore
from csv_diff_reporter.diff_scorer_formatter import format_score


def add_score_args(parser: argparse.ArgumentParser) -> None:
    """Register --show-score and --score-format flags on *parser*."""
    parser.add_argument(
        "--show-score",
        action="store_true",
        default=False,
        help="Append a diff severity score to the report.",
    )
    parser.add_argument(
        "--score-format",
        choices=["text", "json"],
        default="text",
        help="Output format for the score block (default: text).",
    )


def apply_score(result: DiffResult, args: argparse.Namespace) -> DiffScore | None:
    """Return a DiffScore if --show-score is set, else None."""
    if not getattr(args, "show_score", False):
        return None
    return score_diff(result)


def render_score(score: DiffScore | None, args: argparse.Namespace) -> str:
    """Render the score block as a string (empty string if score is None)."""
    if score is None:
        return ""
    fmt = getattr(args, "score_format", "text")
    return format_score(score, fmt=fmt)
