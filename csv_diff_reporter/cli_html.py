"""CLI helpers for HTML output format."""
from __future__ import annotations

import argparse
from pathlib import Path

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.diff_formatter_html import format_diff_as_html


def add_html_args(parser: argparse.ArgumentParser) -> None:
    """Register HTML-related flags on *parser*."""
    parser.add_argument(
        "--html",
        metavar="FILE",
        default=None,
        help="Write an HTML report to FILE in addition to normal output.",
    )
    parser.add_argument(
        "--html-title",
        metavar="TITLE",
        default="CSV Diff Report",
        help="Title embedded in the HTML report (default: 'CSV Diff Report').",
    )


def apply_html_export(args: argparse.Namespace, result: DiffResult) -> None:
    """If --html was requested, render and write the HTML report."""
    output_path: str | None = getattr(args, "html", None)
    if not output_path:
        return

    title: str = getattr(args, "html_title", "CSV Diff Report")
    html_content = format_diff_as_html(result, title=title)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_content, encoding="utf-8")
