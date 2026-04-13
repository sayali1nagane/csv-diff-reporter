"""CLI helpers for the --highlight flag that annotates changed fields."""
import argparse
from typing import List

from csv_diff_reporter.differ import DiffResult
from csv_diff_reporter.highlighter import highlight_diff, format_highlighted_row, HighlightedRow


def add_highlight_args(parser: argparse.ArgumentParser) -> None:
    """Register the --highlight argument on an existing ArgumentParser."""
    parser.add_argument(
        "--highlight",
        action="store_true",
        default=False,
        help="Annotate each changed row with per-field before/after values.",
    )


def apply_highlight(result: DiffResult, *, enabled: bool) -> List[HighlightedRow]:
    """Return highlighted rows when enabled, otherwise an empty list."""
    if not enabled:
        return []
    return highlight_diff(result.rows)


def render_highlights(highlighted_rows: List[HighlightedRow], output_format: str = "text") -> str:
    """Render highlighted rows as a string in the requested format.

    Supported formats: ``text`` (default), ``plain`` (alias for text).
    Returns an empty string when there are no rows to render.
    """
    if not highlighted_rows:
        return ""

    if output_format in ("text", "plain"):
        sections = [format_highlighted_row(hr) for hr in highlighted_rows]
        return "\n\n".join(sections)

    raise ValueError(f"Unsupported highlight output format: {output_format!r}")
