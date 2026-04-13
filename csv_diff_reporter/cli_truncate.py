"""CLI helpers for applying truncation options and rendering the truncation notice.

This module bridges the truncator with the CLI layer so that ``--max-rows``
can be applied uniformly regardless of output format.
"""
from __future__ import annotations

import argparse
from typing import Optional

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.truncator import TruncateResult, format_truncation_notice, truncate_diff


def add_truncate_args(parser: argparse.ArgumentParser) -> None:
    """Register ``--max-rows`` on *parser* in-place."""
    parser.add_argument(
        "--max-rows",
        metavar="N",
        type=int,
        default=None,
        help="Limit output to the first N changed rows (default: no limit).",
    )


def apply_truncation(
    result: DiffResult,
    max_rows: Optional[int],
    *,
    verbose: bool = False,
) -> tuple[DiffResult, str]:
    """Apply truncation to *result* and return the trimmed diff plus a notice.

    Parameters
    ----------
    result:
        Full diff result from the pipeline.
    max_rows:
        Maximum rows to keep.  ``None`` means keep all.
    verbose:
        When *True* a notice is always returned even if no truncation occurred
        (empty string in that case).

    Returns
    -------
    tuple[DiffResult, str]
        The (possibly shortened) diff and a human-readable truncation notice
        (empty string when no rows were dropped).
    """
    tr: TruncateResult = truncate_diff(result, limit=max_rows)
    notice: str = format_truncation_notice(tr)
    return tr.diff, notice


def render_notice(notice: str, output_format: str = "text") -> str:
    """Wrap *notice* in a format-appropriate comment/block.

    Parameters
    ----------
    notice:
        Raw notice string from :func:`format_truncation_notice`.
    output_format:
        One of ``"text"``, ``"markdown"``, or ``"json"``.

    Returns
    -------
    str
        Formatted notice, or empty string when *notice* is empty.
    """
    if not notice:
        return ""

    if output_format == "markdown":
        return f"> ⚠️  {notice}\n"
    if output_format == "json":
        # Callers should embed this as a top-level key; we just return the raw text.
        return notice
    # default: plain text
    return f"# {notice}\n"
