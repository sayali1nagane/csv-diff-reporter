"""Output formatters for diff reports (plain text, JSON, Markdown)."""

from __future__ import annotations

import json
from typing import Literal

from csv_diff_reporter.differ import DiffResult, RowDiff

OutputFormat = Literal["text", "json", "markdown"]


def _row_diff_to_dict(rd: RowDiff) -> dict:
    return {
        "key": rd.key,
        "status": rd.status,
        "old": rd.old_row,
        "new": rd.new_row,
        "changed_fields": rd.changed_fields,
    }


def format_as_json(result: DiffResult, indent: int = 2) -> str:
    """Serialise a DiffResult to a JSON string."""
    payload = {
        "summary": {
            "added": result.added,
            "removed": result.removed,
            "modified": result.modified,
            "total_changes": result.total_changes,
        },
        "changes": [_row_diff_to_dict(rd) for rd in result.row_diffs],
    }
    return json.dumps(payload, indent=indent, ensure_ascii=False)


def format_as_markdown(result: DiffResult) -> str:
    """Render a DiffResult as a Markdown document."""
    lines: list[str] = []
    lines.append("# CSV Diff Report\n")
    lines.append("## Summary\n")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Added  | {result.added} |")
    lines.append(f"| Removed | {result.removed} |")
    lines.append(f"| Modified | {result.modified} |")
    lines.append(f"| **Total changes** | **{result.total_changes}** |\n")

    if not result.row_diffs:
        lines.append("_No differences found._")
        return "\n".join(lines)

    lines.append("## Changes\n")
    for rd in result.row_diffs:
        status_icon = {"added": "➕", "removed": "➖", "modified": "✏️"}.get(rd.status, "?")
        lines.append(f"### {status_icon} `{rd.key}` ({rd.status})\n")
        if rd.status == "modified" and rd.changed_fields:
            lines.append("| Field | Old | New |")
            lines.append("|-------|-----|-----|")
            for field in rd.changed_fields:
                old_val = (rd.old_row or {}).get(field, "")
                new_val = (rd.new_row or {}).get(field, "")
                lines.append(f"| `{field}` | {old_val} | {new_val} |")
            lines.append("")
        elif rd.status == "added" and rd.new_row:
            lines.append(", ".join(f"`{k}`: {v}" for k, v in rd.new_row.items()))
            lines.append("")
        elif rd.status == "removed" and rd.old_row:
            lines.append(", ".join(f"`{k}`: {v}" for k, v in rd.old_row.items()))
            lines.append("")
    return "\n".join(lines)


def format_output(result: DiffResult, fmt: OutputFormat) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "json":
        return format_as_json(result)
    if fmt == "markdown":
        return format_as_markdown(result)
    # Default: reuse the existing text reporter
    from csv_diff_reporter.reporter import generate_report
    return generate_report(result)
