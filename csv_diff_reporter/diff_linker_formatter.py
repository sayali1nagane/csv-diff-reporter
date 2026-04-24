"""Formatter for LinkedDiffResult produced by diff_linker.

Supports text and JSON output modes.
"""

from __future__ import annotations

import json
from typing import Union

from csv_diff_reporter.diff_linker import LinkedDiffResult, LinkedRow


def _row_to_dict(row: LinkedRow) -> dict:
    """Serialise a LinkedRow to a plain dictionary."""
    return row.as_dict()


def _as_text(result: LinkedDiffResult) -> str:
    """Render a LinkedDiffResult as a human-readable text report."""
    lines: list[str] = []

    lines.append("=== Linked Diff Report ===")
    lines.append(
        f"Left:  {result.left_label}  |  Right: {result.right_label}"
    )
    lines.append(
        f"Matched: {len(result.matched)}  "
        f"Left-only: {len(result.left_only)}  "
        f"Right-only: {len(result.right_only)}"
    )
    lines.append("")

    if result.matched:
        lines.append("--- Matched rows (present in both) ---")
        for row in result.matched:
            d = _row_to_dict(row)
            key_str = ", ".join(f"{k}={v}" for k, v in d.get("key", {}).items())
            left_str = ", ".join(
                f"{k}={v}" for k, v in d.get("left_fields", {}).items()
            )
            right_str = ", ".join(
                f"{k}={v}" for k, v in d.get("right_fields", {}).items()
            )
            changed = d.get("changed", False)
            marker = "*" if changed else " "
            lines.append(f"  [{marker}] key=({key_str})")
            if changed:
                lines.append(f"      left : {left_str}")
                lines.append(f"      right: {right_str}")
        lines.append("")

    if result.left_only:
        lines.append(f"--- Left-only rows ({result.left_label}) ---")
        for row in result.left_only:
            d = _row_to_dict(row)
            key_str = ", ".join(f"{k}={v}" for k, v in d.get("key", {}).items())
            fields_str = ", ".join(
                f"{k}={v}" for k, v in d.get("left_fields", {}).items()
            )
            lines.append(f"  [-] key=({key_str})  {fields_str}")
        lines.append("")

    if result.right_only:
        lines.append(f"--- Right-only rows ({result.right_label}) ---")
        for row in result.right_only:
            d = _row_to_dict(row)
            key_str = ", ".join(f"{k}={v}" for k, v in d.get("key", {}).items())
            fields_str = ", ".join(
                f"{k}={v}" for k, v in d.get("right_fields", {}).items()
            )
            lines.append(f"  [+] key=({key_str})  {fields_str}")
        lines.append("")

    if not result.matched and not result.left_only and not result.right_only:
        lines.append("No rows to display.")

    return "\n".join(lines)


def _as_json(result: LinkedDiffResult) -> str:
    """Render a LinkedDiffResult as a JSON string."""
    payload = {
        "left_label": result.left_label,
        "right_label": result.right_label,
        "matched": [_row_to_dict(r) for r in result.matched],
        "left_only": [_row_to_dict(r) for r in result.left_only],
        "right_only": [_row_to_dict(r) for r in result.right_only],
        "summary": {
            "matched": len(result.matched),
            "left_only": len(result.left_only),
            "right_only": len(result.right_only),
            "changed_matched": sum(
                1 for r in result.matched if r.in_both() and r.as_dict().get("changed")
            ),
        },
    }
    return json.dumps(payload, indent=2)


def format_linked(
    result: LinkedDiffResult,
    fmt: str = "text",
) -> str:
    """Format *result* using the requested output format.

    Parameters
    ----------
    result:
        The ``LinkedDiffResult`` produced by ``diff_linker.link_diffs``.
    fmt:
        Either ``"text"`` (default) or ``"json"``.

    Returns
    -------
    str
        Formatted output ready for display or writing to a file.
    """
    if fmt == "json":
        return _as_json(result)
    return _as_text(result)
