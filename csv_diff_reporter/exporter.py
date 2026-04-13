"""Exporter module: write diff reports to output files or stdout."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from csv_diff_reporter.formatter import format_output
from csv_diff_reporter.differ import DiffResult


class ExportError(Exception):
    """Raised when writing the report fails."""


def export_to_file(content: str, path: Path) -> None:
    """Write *content* to *path*, creating parent directories as needed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise ExportError(f"Cannot write to '{path}': {exc}") from exc


def export_to_stdout(content: str) -> None:
    """Write *content* to standard output."""
    sys.stdout.write(content)
    if not content.endswith("\n"):
        sys.stdout.write("\n")


def export(
    result: DiffResult,
    fmt: str = "text",
    output_path: Optional[Path] = None,
) -> None:
    """Format *result* and send it to *output_path* or stdout.

    Parameters
    ----------
    result:
        The diff result produced by :func:`csv_diff_reporter.differ.diff_csv`.
    fmt:
        Output format – one of ``"text"``, ``"json"``, or ``"markdown"``.
    output_path:
        Destination file.  When *None* the report is written to stdout.
    """
    content = format_output(result, fmt)
    if output_path is None:
        export_to_stdout(content)
    else:
        export_to_file(content, output_path)
