"""CLI helpers for the diff-grouper feature."""
from __future__ import annotations

import argparse
import json
from typing import Optional

from csv_diff_reporter.diff_grouper import GroupOptions, GroupedDiff, group_diff
from csv_diff_reporter.differ import DiffResult


def add_group_args(parser: argparse.ArgumentParser) -> None:
    """Register --group-by and related flags on *parser*."""
    parser.add_argument(
        "--group-by",
        metavar="COLUMN",
        default=None,
        help="Group diff rows by the value of COLUMN.",
    )
    parser.add_argument(
        "--group-drop-ungrouped",
        action="store_true",
        default=False,
        help="Exclude rows that do not contain the grouping column.",
    )
    parser.add_argument(
        "--group-ungrouped-label",
        metavar="LABEL",
        default="(other)",
        help="Label used for rows missing the grouping column (default: '(other)').",
    )


def apply_grouping(
    result: DiffResult, args: argparse.Namespace
) -> Optional[GroupedDiff]:
    """Return a GroupedDiff when --group-by is set, else None."""
    column: Optional[str] = getattr(args, "group_by", None)
    if not column:
        return None
    options = GroupOptions(
        column=column,
        include_ungrouped=not getattr(args, "group_drop_ungrouped", False),
        ungrouped_label=getattr(args, "group_ungrouped_label", "(other)"),
    )
    return group_diff(result, options)


def render_grouped(grouped: GroupedDiff, fmt: str = "text") -> str:
    """Render a GroupedDiff as text or JSON."""
    if fmt == "json":
        payload = {
            "grouped_by": grouped.column,
            "groups": {
                key: [
                    {"key": r.key, "change_type": r.change_type}
                    for r in rows
                ]
                for key, rows in grouped.groups.items()
            },
        }
        return json.dumps(payload, indent=2)

    lines = [f"Grouped by: {grouped.column}"]
    for key in grouped.group_keys():
        rows = grouped.rows_for(key)
        lines.append(f"  [{key}]  {len(rows)} row(s)")
        for row in rows:
            lines.append(f"    {row.change_type:10s}  key={row.key}")
    return "\n".join(lines)
