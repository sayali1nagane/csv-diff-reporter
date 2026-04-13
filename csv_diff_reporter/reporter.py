"""Generates human-readable diff reports from DiffResult objects."""

from __future__ import annotations

from io import StringIO
from typing import TextIO

from .differ import DiffResult, RowDiff


DIVIDER = "-" * 60


def _format_row_diff(diff: RowDiff) -> str:
    """Return a formatted block describing a single row change."""
    lines: list[str] = []

    if diff.status == "added":
        lines.append(f"  [+] Row '{diff.key}' added")
        for col, (_, new) in diff.changes.items():
            lines.append(f"      {col}: {new!r}")

    elif diff.status == "removed":
        lines.append(f"  [-] Row '{diff.key}' removed")
        for col, (old, _) in diff.changes.items():
            lines.append(f"      {col}: {old!r}")

    elif diff.status == "modified":
        lines.append(f"  [~] Row '{diff.key}' modified")
        for col, (old, new) in diff.changes.items():
            lines.append(f"      {col}: {old!r} -> {new!r}")

    return "\n".join(lines)


def generate_report(result: DiffResult, file: TextIO | None = None) -> str:
    """Render a diff report and optionally write it to *file*.

    Returns the report as a string regardless of whether *file* is supplied.
    """
    buf = StringIO()

    buf.write("CSV Diff Report\n")
    buf.write(DIVIDER + "\n")

    added = [d for d in result.diffs if d.status == "added"]
    removed = [d for d in result.diffs if d.status == "removed"]
    modified = [d for d in result.diffs if d.status == "modified"]

    buf.write(
        f"Summary: {len(added)} added, {len(removed)} removed, "
        f"{len(modified)} modified\n"
    )
    buf.write(DIVIDER + "\n")

    if not result.diffs:
        buf.write("No differences found.\n")
    else:
        for diff in result.diffs:
            buf.write(_format_row_diff(diff) + "\n")

    buf.write(DIVIDER + "\n")

    report = buf.getvalue()

    if file is not None:
        file.write(report)

    return report
